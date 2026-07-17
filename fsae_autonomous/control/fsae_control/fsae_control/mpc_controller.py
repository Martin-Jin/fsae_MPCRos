import rclpy
from rclpy.node import Node
import numpy as np
import math

from geometry_msgs.msg import PoseArray, Pose
from ackermann_msgs.msg import AckermannDrive, AckermannDriveStamped
from std_msgs.msg import Header

from .control_utils import MPCController


def angle_mod(x, zero_2_2pi=False, degree=False):
    """
    Angle modulo operation. Copied from stanley_controller.py so this node
    has no dependency on the old controller file.
    Default angle modulo range is [-pi, pi).
    """
    if isinstance(x, float):
        is_float = True
    else:
        is_float = False

    x = np.asarray(x).flatten()
    if degree:
        x = np.deg2rad(x)

    if zero_2_2pi:
        mod_angle = x % (2 * np.pi)
    else:
        mod_angle = (x + np.pi) % (2 * np.pi) - np.pi

    if degree:
        mod_angle = np.rad2deg(mod_angle)

    if is_float:
        return mod_angle.item()
    else:
        return mod_angle


class MPCControl(Node):
    """
    MPC path-tracking controller node for the fsae_planning stack.

    Drop-in replacement for stanley_controller.py: same input topics
    (/fsae/planning/selected_trajectory, /fsae/slam/car_position), same
    three-topic AckermannDrive/AckermannDriveStamped output convention, same
    parameter-loading pattern. Internally it wraps control_utils.MPCController
    — the same MPC (model, cost function, adaptive gain scheduling, OSQP/
    Clarabel solve) used in the FSDS simulator integration.

    ============================================================================
    THIS IS NOT A 1:1 PORT OF THE FSDS control_node.py — READ BEFORE DEPLOYING
    ============================================================================
    FSDS has direct access to real odometry (Odometry.twist for car_speed and
    car_yaw_rate), a fused cone map for a cone-proximity brake, a GO-signal
    topic, and a per-point curvature-aware speed profile from the planner.
    None of those exist on this stack's current topic set. Every place this
    node deviates from FSDS's control_node.py because of that is marked
    "# TODO (1:1 gap):" inline, with the specific reason and what real sensor/
    topic would remove the gap. Search this file for "TODO (1:1 gap)" for the
    full list before trusting this on a real car. Summary:

      1. car_speed / car_yaw_rate — finite-differenced from consecutive SLAM
         poses (see _update_motion_estimate), not read from odometry/IMU.
         Noisier than FSDS's ground-truth twist; feeds directly into the MPC's
         e_y_dot and x0[3] states.
      2. desired_speed — flat constant parameter, not a per-point profile.
         /fsae/planning/selected_trajectory (PoseArray) carries no speed
         field, so there is currently no way to recover corner-aware speed
         targets on this stack at all — this is a planner-side gap, not
         something this node can fix alone.
      3. GO signal — a static launch parameter (wait_for_go), not a real
         subscription. If left True, this WILL make the car never drive,
         since nothing ever flips it back to False at runtime. No stack topic
         for this currently exists; flagged for whoever owns mission control.
      4. Stale-path safety — no staleness/timeout check on the trajectory
         topic, unlike FSDS's TARGET_TIMEOUT-based Phase 2 brake. Nothing
         resets the MPC or brakes if centerline_planner stops publishing.
      5. Longitudinal output — MPCController.compute() returns normalised
         throttle/brake fractions (FSDS ControlCommand convention), but
         ack_to_can.py expects a raw acceleration (m/s^2) in
         AckermannDrive.acceleration, sent on its own CAN byte independent of
         speed. Reconstructed accordingly (see publish_ackermann) — but
         ack_to_can.py's bounds check currently REJECTS negative
         acceleration/speed outright, meaning braking commands cannot reach
         the kart until that validation is updated. This node cannot fix that
         on its own; flagged here for visibility.
    ============================================================================
    """

    def __init__(self):
        super().__init__('mpc_controller')
        self.get_logger().info("MPC Controller Node Started")

        # Parameters (loaded from fsae_bringup/config/fsae_params.yaml).
        # target_velocity kept for parity with stanley_controller.py (used
        # as the flat speed target — see class docstring gap #2). wait_for_go
        # is a placeholder until a real GO-signal topic exists on this stack
        # (see class docstring gap #3).
        self.declare_parameters(
            namespace='',
            parameters=[
                ('target_velocity', 8.0),   # [m/s] flat speed target (no per-point profile yet)
                ('front_axle_dist', 1.0),   # [m] camera/SLAM origin to front axle
                ('wait_for_go', False),     # placeholder — no GO topic on this stack yet
                ('path_timeout_sec', 0.5),  # [s] TODO (1:1 gap #4): mirrors FSDS TARGET_TIMEOUT
            ]
        )
        self.front_axle_dist = self.get_parameter('front_axle_dist').get_parameter_value().double_value
        self.wait_for_go = self.get_parameter('wait_for_go').get_parameter_value().bool_value
        self._go_received = not self.wait_for_go   # if not waiting, start "received"
        # TODO (1:1 gap #3): _go_received is set once here and NEVER updated
        # again anywhere in this node — there is no /fsae/mission/go (or
        # equivalent) subscription on this stack to flip it. If wait_for_go
        # is left True at launch, this node will hold full brake FOREVER.
        # FSDS's ControlNode._go_cb() latches a real GoSignal message; port
        # that pattern once a mission-control GO topic exists (see sys_status.py
        # / MISSION_STATES for where that signal likely originates on this stack).

        self.path_timeout_sec = self.get_parameter('path_timeout_sec').get_parameter_value().double_value

        # ── Path state (mirrors stanley's tx/ty, kept as one (N,2) array) ──
        self.path_pts: np.ndarray = np.empty((0, 2))
        # TODO (1:1 gap #4): FSDS's ControlNode._path_cb() stamps
        # self._path_stamp = self.get_clock().now() on every path message and
        # _control_loop() checks that timestamp against TARGET_TIMEOUT before
        # trusting the path (see control_node.py Phase 2). This node does the
        # same here (see selected_trajectory_handler / main_heartbeat) so a
        # stalled centerline_planner triggers a brake instead of silently
        # re-using a stale path_pts array indefinitely.
        self._path_stamp = None

        # ── Car pose/motion state ───────────────────────────────────────
        # car_yaw uses the same convention as stanley_controller.py:
        # orientation.w read directly as yaw (radians), not a quaternion
        # conversion — matches whatever this stack's SLAM/camera node
        # publishes on /fsae/slam/car_position (see ARCHITECTURE.md: yaw is
        # repurposed into orientation.w by cone_detection_node). This is
        # correct for THIS stack's convention, unlike a generic ROS Pose.
        self._have_pose      = False
        self._car_pos        = np.zeros(2)
        self._car_yaw        = 0.0
        self._car_speed      = 0.0
        self._car_yaw_rate   = 0.0
        self._prev_pos       = None
        self._prev_yaw       = None
        self._prev_stamp     = None

        # ── Subscriptions ────────────────────────────────────────────────
        self.create_subscription(PoseArray, "/fsae/planning/selected_trajectory",
                                  self.selected_trajectory_handler, 5)
        self.create_subscription(Pose, "/fsae/slam/car_position",
                                  self.main_heartbeat, 5)

        # ── Publishers ────────
        # Same three-topic pattern as stanley_controller.py: /drive (raw,
        # unstamped, orphan in-repo per ARCHITECTURE.md), /drive_vis (feeds
        # pursuit_viz), /cmd_vel (the live command actually consumed by
        # ack_to_can_node).
        self.cmd_drive_pub = self.create_publisher(AckermannDrive, "/fsae/control/drive", 5)
        self.cmd_vis_pub   = self.create_publisher(AckermannDrive, "/fsae/control/drive_vis", 5)
        self.cmd_vel_pub   = self.create_publisher(AckermannDriveStamped, "/fsae/control/cmd_vel", 5)

        # ── MPC controller ──
        # Same model/cost-function/solver/adaptive-gain implementation as the
        # FSDS integration — this is the part of the stack that IS a 1:1
        # match. dt/N must stay in sync with settings.N_HORIZON in the
        # offline tuner if weights are re-tuned.
        self._mpc = MPCController(dt=0.05, N=25)

        self.steering_angle = 0.0
        self.target_speed   = 0.0
        self.accel_cmd       = 0.0   # [m/s^2] see publish_ackermann() gap #5

    # ------------------------------------------------------------------
    # Subscriber callbacks
    # ------------------------------------------------------------------

    def selected_trajectory_handler(self, msg: PoseArray) -> None:
        """
        Store the latest planned path as an (N,2) array, mirroring stanley's
        tx/ty lists. Also stamps arrival time for the staleness check in
        main_heartbeat (TODO (1:1 gap #4) — mirrors FSDS's _path_cb()).
        """
        self.path_pts = np.array(
            [[p.position.x, p.position.y] for p in msg.poses],
            dtype=np.float64,
        ) if msg.poses else np.empty((0, 2))
        self._path_stamp = self.get_clock().now()

    def main_heartbeat(self, msg: Pose) -> None:
        """
        Runs the MPC solve on every car-position update, mirroring stanley's
        main_hearback() (same event-driven, pose-triggered control pattern
        rather than a fixed-rate timer, since that's what this stack expects
        — /fsae/slam/car_position is the highest-rate topic available here).
        """
        car_pose = msg
        self._car_pos = np.array([car_pose.position.x, car_pose.position.y])
        # Same yaw convention as stanley_controller.py (see class docstring).
        self._car_yaw = self.normalize_angle(car_pose.orientation.w)

        self._update_motion_estimate()

        self.target_speed = self.get_parameter('target_velocity').get_parameter_value().double_value
        # TODO (1:1 gap #2): FSDS reads a per-point v_target from
        # SimPlanner.v_profile (curvature-aware — see speed_profile.py) here
        # instead of a flat constant. This stack's /fsae/planning/
        # selected_trajectory (PoseArray) has no speed field to carry that
        # information, so the MPC's e_v state never anticipates corners on
        # this stack — it will attempt to hold target_velocity through
        # hairpins and rely entirely on lateral cost terms to survive. Fixing
        # this properly requires the planner (centerline_planner.py) to
        # publish a speed alongside each waypoint (e.g. a custom Trajectory
        # msg with per-point speed, or reusing Pose.position.z as a speed
        # channel), and this node to interpolate against car_pos the same way
        # rollout_core.py does with planner.v_profile.

        # ── Placeholder GO-wait: full brake until "received" ────────────
        if not self._go_received:
            self.steering_angle = 0.0
            self.target_speed = 0.0
            self.accel_cmd = 0.0
            self.get_logger().warn("Waiting for GO (placeholder) — holding brake.", throttle_duration_sec=2.0)
            self.publish_ackermann()
            return

        # ── Path validity + staleness check ─────────────────────────────
        # TODO (1:1 gap #4): staleness half of this check (path_stale) mirrors
        # FSDS control_node.py's Phase 2. The length check alone existed in
        # the original version of this node; the staleness check is new here
        # since selected_trajectory_handler now stamps _path_stamp.
        path_stale = (
            self._path_stamp is None
            or (self.get_clock().now() - self._path_stamp).nanoseconds * 1e-9 > self.path_timeout_sec
        )
        if len(self.path_pts) < 2 or path_stale:
            self.steering_angle = 0.0
            self.target_speed = 0.0
            self.accel_cmd = 0.0
            reason = "no trajectory found" if len(self.path_pts) < 2 else "trajectory stale"
            self.get_logger().warn(f"Warning: {reason}, will set steering angle to 0!!!!")
            self.publish_ackermann()
            return

        # ── MPC solve ────────────────────────────────────────────────────
        # 1:1 match with the FSDS integration's control_node.py Phase 3 call
        # — same inputs, same controller. See class docstring gaps #1/#2 for
        # what car_speed/car_yaw_rate/desired_speed actually are on this
        # stack vs. FSDS.
        steer_out, throttle_out, brake_out = self._mpc.compute(
            path=self.path_pts,
            car_pos=self._car_pos,
            car_yaw=self._car_yaw,
            car_speed=self._car_speed,
            desired_speed=self.target_speed,
            car_yaw_rate=self._car_yaw_rate,
        )

        # steer_out is normalised [-1, 1] (FSDS ControlCommand convention
        # inside MPCController); convert to a signed degree angle for
        # AckermannDrive, matching stanley's delta-in-degrees output.
        # self._mpc.u_max[0] is MAX_STEER_RAD (radians), so this product is
        # (unitless fraction) x (radians) -> degrees(...) is a valid rad->deg
        # conversion of the actual steering angle, not a units bug — kept as
        # a derived value off the controller's own bound rather than
        # re-importing MAX_STEER_RAD, so it can never drift out of sync with
        # control_utils.py if that bound changes.
        self.steering_angle = math.degrees(steer_out * self._mpc.u_max[0])

        # TODO (1:1 gap #5): MPCController.compute() returns throttle/brake
        # as normalised [0,1] fractions of a_max / a_max_brake (FSDS
        # ControlCommand convention — separate throttle/brake channels).
        # AckermannDrive has both a `speed` field AND an `acceleration`
        # field, and ack_to_can.py sends BOTH as independent CAN bytes (see
        # ack_to_can.py's ackermann_to_can_parser — acceleration is not
        # derived from speed, it has its own byte). So instead of collapsing
        # throttle/brake into a binary speed-or-zero decision (which was the
        # old/incorrect approach and silently discarded all braking intent),
        # reconstruct the actual acceleration command the MPC decided on and
        # send it in drive.acceleration, keeping drive.speed as the
        # (currently flat, see gap #2) target speed for whatever closed-loop
        # speed controller consumes it kart-side.
        #
        # KNOWN DOWNSTREAM BLOCKER: ack_to_can.py's ackermann_to_can_parser()
        # validates `0 <= acceleration <= 255` and `0 <= speed <= 255` and
        # silently drops (returns None, no publish) any message with a
        # negative value in either field. Braking (a_cmd < 0) therefore
        # CANNOT currently reach the kart at all through this pipeline — this
        # is a bug in ack_to_can.py's validation/encoding, not something
        # fixable from this node alone. Flagging loudly here so it isn't
        # missed: whoever owns ack_to_can.py needs to add a sign
        # convention (e.g. separate brake byte, or signed-magnitude encoding
        # matching what's already done for steering_angle in that file) before
        # this controller's braking output has any effect on the real car.
        if throttle_out > 0.0:
            self.accel_cmd = throttle_out * self._mpc.a_max
        else:
            self.accel_cmd = -brake_out * self._mpc.a_max_brake   # negative — see blocker above

        self.publish_ackermann()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _update_motion_estimate(self) -> None:
        """
        Finite-difference car_speed and car_yaw_rate from consecutive pose
        messages.

        TODO (1:1 gap #1): FSDS's ControlNode._odom_cb() reads car_speed
        and car_yaw_rate directly from Odometry.twist (linear velocity
        magnitude and angular.z), which on the sim side comes from
        ground-truth plant state. This stack has no odometry/IMU-twist topic
        wired to this node, so both are approximated here by
        finite-differencing consecutive /fsae/slam/car_position poses. This
        is noisier than a real twist reading (amplifies any SLAM pose jitter
        into a velocity/yaw-rate estimate) and both values feed directly into
        the MPC's cost function (e_y_dot in _error_state(), and x0[3]/kappa
        via curvature_estimate-equivalent logic) — expect noisier steering
        and adaptive-gain behaviour than in sim. If /fsae/slam or a future
        IMU node ever publishes a twist/velocity topic, wire it in here
        directly and delete this FD estimate.
        """
        now = self.get_clock().now()

        if self._prev_pos is not None and self._prev_stamp is not None:
            dt = (now - self._prev_stamp).nanoseconds * 1e-9
            if dt > 1e-3:
                self._car_speed = float(np.linalg.norm(self._car_pos - self._prev_pos)) / dt
                dyaw = angle_mod(self._car_yaw - self._prev_yaw)
                self._car_yaw_rate = dyaw / dt

        self._prev_pos   = self._car_pos.copy()
        self._prev_yaw   = self._car_yaw
        self._prev_stamp = now

    def publish_ackermann(self) -> None:
        """
        Publish to all three drive topics, mirroring stanley_controller.py
        exactly. TODO (1:1 gap #5): unlike stanley (which always sent
        acceleration=0.0, since Stanley is a lateral-only controller), this
        node now populates `acceleration` with the MPC's actual longitudinal
        decision — see main_heartbeat() for the derivation and the
        ack_to_can.py validation blocker.
        """
        args1 = {"steering_angle": float(self.steering_angle),
                 "steering_angle_velocity": 0.0,
                 "speed": float(self.target_speed),
                 "acceleration": float(self.accel_cmd),
                 "jerk": 0.0}
        msg1 = AckermannDrive(**args1)

        args2 = {"steering_angle": float(self.steering_angle),
                 "steering_angle_velocity": 0.0,
                 "speed": float(self.target_speed),
                 "acceleration": float(self.accel_cmd),
                 "jerk": 0.0}
        msg2 = AckermannDrive(**args2)

        args3 = {"header": Header(stamp=self.get_clock().now().to_msg(), frame_id="mpc_controller"),
                 "drive": msg1}
        msg3 = AckermannDriveStamped(**args3)

        self.get_logger().warn('Sending Angle: ' + str(self.steering_angle))

        self.cmd_drive_pub.publish(msg1)
        self.cmd_vis_pub.publish(msg2)
        self.cmd_vel_pub.publish(msg3)

    def normalize_angle(self, angle):
        return angle_mod(angle, zero_2_2pi=True)


def main(args=None):
    rclpy.init(args=args)
    mpc_controller = MPCControl()
    rclpy.spin(mpc_controller)
    mpc_controller.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
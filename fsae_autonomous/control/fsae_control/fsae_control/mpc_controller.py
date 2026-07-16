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

    Drop-in replacement for stanley_controller.py: same topics, same
    AckermannDrive output convention, same parameter-loading pattern.
    Internally it wraps control_utils.MPCController (the same MPC used by
    the FSDS simulator/tuner project) instead of a Stanley law.

    KNOWN GAPS vs. the simulator's MPCController.compute() inputs
    ---------------------------------------------------------------
    The simulator/FSDS integration has direct access to odometry
    (car_speed, car_yaw_rate) and a per-point speed profile from the
    planner. Neither is available on this stack's current topics:
      - car_speed / car_yaw_rate are estimated here by finite-differencing
        consecutive /fsae/slam/car_position poses (see _update_motion_estimate).
        This is noisier than a real odometry/IMU reading — if a twist topic
        becomes available later, wire it in and delete the FD estimate.
      - desired_speed has no per-point profile from the planner (PoseArray
        carries no speed field), so it falls back to the same flat
        'target_velocity' param stanley_controller.py used.
      - GO signal: no topic currently exists for this on the stack, so this
        is a placeholder parameter (wait_for_go) rather than a subscription.
    """

    def __init__(self):
        super().__init__('mpc_controller')
        self.get_logger().info("MPC Controller Node Started")

        # Parameters (loaded from fsae_bringup/config/fsae_params.yaml).
        # target_velocity kept for parity with stanley_controller.py (used
        # as the flat speed target, see class docstring). wait_for_go is a
        # placeholder until a real GO-signal topic exists on this stack.
        self.declare_parameters(
            namespace='',
            parameters=[
                ('target_velocity', 8.0),   # [m/s] flat speed target (no per-point profile yet)
                ('front_axle_dist', 1.0),   # [m] camera/SLAM origin to front axle
                ('wait_for_go', False),     # placeholder — no GO topic on this stack yet
            ]
        )
        self.front_axle_dist = self.get_parameter('front_axle_dist').get_parameter_value().double_value
        self.wait_for_go = self.get_parameter('wait_for_go').get_parameter_value().bool_value
        self._go_received = not self.wait_for_go   # if not waiting, start "received"

        # ── Path state (mirrors stanley's tx/ty, kept as one (N,2) array) ──
        self.path_pts: np.ndarray = np.empty((0, 2))

        # ── Car pose/motion state ───────────────────────────────────────
        # car_yaw uses the same convention as stanley_controller.py:
        # orientation.w read directly as yaw (radians), not a quaternion
        # conversion — matches whatever this stack's SLAM node publishes.
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

        # ── Publishers (same three topics as stanley_controller.py) ────────
        self.cmd_drive_pub = self.create_publisher(AckermannDrive, "/fsae/control/drive", 5)
        self.cmd_vis_pub   = self.create_publisher(AckermannDrive, "/fsae/control/drive_vis", 5)
        self.cmd_vel_pub   = self.create_publisher(AckermannDriveStamped, "/fsae/control/cmd_vel", 5)

        # ── MPC controller (shared implementation with the FSDS project) ──
        self._mpc = MPCController(dt=0.05, N=25)

        self.steering_angle = 0.0
        self.target_speed   = 0.0

    # ------------------------------------------------------------------
    # Subscriber callbacks
    # ------------------------------------------------------------------

    def selected_trajectory_handler(self, msg: PoseArray) -> None:
        """Store the latest planned path as an (N,2) array, mirroring stanley's tx/ty lists."""
        self.path_pts = np.array(
            [[p.position.x, p.position.y] for p in msg.poses],
            dtype=np.float64,
        ) if msg.poses else np.empty((0, 2))

    def main_heartbeat(self, msg: Pose) -> None:
        """
        Runs the MPC solve on every car-position update, mirroring stanley's
        main_hearback() (same event-driven, pose-triggered control pattern
        rather than a fixed-rate timer, since that's what this stack expects).
        """
        car_pose = msg
        self._car_pos = np.array([car_pose.position.x, car_pose.position.y])
        # Same yaw convention as stanley_controller.py (see class docstring).
        self._car_yaw = self.normalize_angle(car_pose.orientation.w)

        self._update_motion_estimate()

        self.target_speed = self.get_parameter('target_velocity').get_parameter_value().double_value

        # ── Placeholder GO-wait: full brake until "received" ────────────
        if not self._go_received:
            self.steering_angle = 0.0
            self.target_speed = 0.0
            self.get_logger().warn("Waiting for GO (placeholder) — holding brake.", throttle_duration_sec=2.0)
            self.publish_ackermann()
            return

        if len(self.path_pts) < 2:
            self.steering_angle = 0.0
            self.target_speed = 0.0
            self.get_logger().warn("Warning: no trajectory found, will set steering angle to 0!!!!")
            self.publish_ackermann()
            return

        # ── MPC solve ────────────────────────────────────────────────────
        steer_out, throttle_out, brake_out = self._mpc.compute(
            path=self.path_pts,
            car_pos=self._car_pos,
            car_yaw=self._car_yaw,
            car_speed=self._car_speed,
            desired_speed=self.target_speed,
            car_yaw_rate=self._car_yaw_rate,
        )

        # steer_out is normalised [-1, 1] (FSDS convention inside
        # MPCController); convert to a signed degree angle for AckermannDrive,
        # matching stanley's delta-in-degrees output.
        self.steering_angle = math.degrees(steer_out * self._mpc.u_max[0])
        # Collapse throttle/brake back into a single signed speed target,
        # since AckermannDrive only carries one speed field (no separate
        # brake channel like fs_msgs/ControlCommand).
        self.target_speed = self.target_speed if throttle_out > 0.0 else 0.0

        self.publish_ackermann()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _update_motion_estimate(self) -> None:
        """
        Finite-difference car_speed and car_yaw_rate from consecutive pose
        messages. See class docstring — this stack has no odometry/twist
        topic to read these from directly.
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
        """Publish to all three drive topics, mirroring stanley_controller.py exactly."""
        args1 = {"steering_angle": float(self.steering_angle),
                 "steering_angle_velocity": 0.0,
                 "speed": float(self.target_speed),
                 "acceleration": 0.0,
                 "jerk": 0.0}
        msg1 = AckermannDrive(**args1)

        args2 = {"steering_angle": float(self.steering_angle),
                 "steering_angle_velocity": 0.0,
                 "speed": float(self.target_speed),
                 "acceleration": 0.0,
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
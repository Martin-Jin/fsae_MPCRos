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
    Wraps an angle into a consistent range so comparisons/subtractions
    between angles behave sensibly (e.g. so "359 degrees" and "1 degree"
    are recognised as only 2 degrees apart, not 358). Default range is
    [-180, 180) degrees / [-pi, pi) radians.
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
    The ROS node that connects the MPC controller (control_utils.py) to
    the rest of this car's software. Its job is simple in outline: listen
    for the planned path and the car's current position, pass both into
    the controller, and publish the steering/throttle/brake command it
    returns.

    This node currently runs as the drop-in replacement for the older
    stanley_controller.py node — it listens to the same two input topics
    (/fsae/planning/selected_trajectory for the path,
    /fsae/slam/car_position for the car's position) and publishes to the
    same three output topics, so it can be swapped in without changing
    anything else in the stack.

    ============================================================================
    IMPORTANT CONTEXT BEFORE READING/CHANGING THIS FILE
    ============================================================================
    The MPC controller (control_utils.py) itself was written and tuned with
    a richer set of sensor inputs in mind than this car currently has —
    things like a direct speed/turn-rate sensor, a map of nearby cones for
    an extra safety brake, a "go ahead and drive" signal from mission
    control, and a path that comes with a suggested speed at every point.
    None of those exist as usable inputs on this car's current wiring yet.
    Where this node has to work around a missing input, that's marked
    inline with "# NOTE (missing input):" and explains exactly what's
    missing and what would need to exist to remove the workaround. Search
    this file for "NOTE (missing input)" for the full list. In short:

      1. car_speed / car_yaw_rate — this car has no dedicated speed/turn-
         rate sensor wired to this node, so both are estimated by comparing
         consecutive position updates (see _update_motion_estimate). This
         is noisier than a direct sensor reading would be, and both values
         feed directly into how the controller judges "how off-track am
         I".
      2. desired_speed — currently a single fixed number set in the launch
         config, not a speed that varies along the path. The path message
         this node receives has no field to carry a per-point speed at
         all, so there is currently no way to give the car a
         faster-on-straights, slower-in-corners speed target — this would
         need a change on the path-planning side, not just here.
      3. "Go" signal — controlled by a fixed setting chosen at startup, not
         a live signal that can be sent while the car is running. If that
         setting is left "wait for go", the car will simply never start
         driving, since nothing currently exists to tell it to go. Flagged
         here for whoever owns startup/mission control.
      4. Stale-path safety — if the path stops being updated (e.g. the
         node producing it crashes), this node checks how long it's been
         since the last update and brakes if that gets too old, rather
         than continuing to blindly follow a path that's no longer
         current.
      5. Throttle/brake output — the controller internally thinks in terms
         of separate throttle and brake fractions, but the message type
         this node publishes on has a single combined
         acceleration field instead. This node converts between the two
         (see publish_ackermann) — but there is a known issue further
         downstream (in the code that turns this message into actual CAN-
         bus signals for the car) that currently blocks braking commands
         from having any effect. See the note near where accel_cmd is set,
         below.
    ============================================================================
    """

    def __init__(self):
        super().__init__('mpc_controller')
        self.get_logger().info("MPC Controller Node Started")

        # Settings (loaded from this car's config file). target_velocity is
        # kept as a single flat number for now (see note #2 above — there's
        # currently no way to vary it along the path). wait_for_go is a
        # placeholder until a real "go" signal exists on this car (see note
        # #3 above).
        self.declare_parameters(
            namespace='',
            parameters=[
                ('target_velocity', 8.0),   # [m/s] flat speed target (no per-point profile yet)
                ('front_axle_dist', 1.0),   # [m] distance from the position sensor to the front axle
                ('wait_for_go', False),     # placeholder — no live "go" signal exists yet
                ('path_timeout_sec', 0.5),  # [s] how old the path is allowed to get before braking
            ]
        )
        self.front_axle_dist = self.get_parameter('front_axle_dist').get_parameter_value().double_value
        self.wait_for_go = self.get_parameter('wait_for_go').get_parameter_value().bool_value
        self._go_received = not self.wait_for_go   # if not waiting, start "received"
        # NOTE (missing input #3): _go_received is set once here, right at
        # startup, and nothing in this node ever changes it again — there's
        # no live signal this car can currently receive to say "you're
        # cleared to drive now". If wait_for_go is left True at launch,
        # this means the car will hold full brake and never start driving,
        # since nothing will ever flip this back to True. This should be
        # replaced with a real subscription once a startup/mission-control
        # system exists that can send that signal.

        self.path_timeout_sec = self.get_parameter('path_timeout_sec').get_parameter_value().double_value

        # ── Path state ───────────────────────────────────────────────────
        self.path_pts: np.ndarray = np.empty((0, 2))
        # Timestamp of the last time a path was received, used by the
        # staleness check in main_heartbeat() below — if too much time
        # passes without a new path, the car treats that as unsafe and
        # brakes, rather than continuing to follow an old path forever.
        self._path_stamp = None

        # ── Car pose/motion state ───────────────────────────────────────
        # car_yaw is read directly from a field that this car's
        # position-tracking software repurposes to carry the heading angle
        # (in radians) rather than a full 3D orientation — see
        # ARCHITECTURE.md for why. This matches how that value is actually
        # published on this car, so it's the correct way to read it here.
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

        # ── Publishers ───────────────────────────────────────────────────
        # Same three output topics as the previous controller:
        # /drive is the raw command, /drive_vis feeds the steering
        # visualisation tool, and /cmd_vel is the command that's actually
        # picked up and sent toward the car's hardware.
        self.cmd_drive_pub = self.create_publisher(AckermannDrive, "/fsae/control/drive", 5)
        self.cmd_vis_pub   = self.create_publisher(AckermannDrive, "/fsae/control/drive_vis", 5)
        self.cmd_vel_pub   = self.create_publisher(AckermannDriveStamped, "/fsae/control/cmd_vel", 5)

        # ── MPC controller ───────────────────────────────────────────────
        # dt/N (tick length / lookahead steps) must stay matched to
        # whatever value the controller's tuning weights were tuned for —
        # see control_utils.py's file header for what these mean.
        self._mpc = MPCController(dt=0.05, N=25)

        self.steering_angle = 0.0
        self.target_speed   = 0.0
        self.accel_cmd       = 0.0   # [m/s^2] see publish_ackermann() note #5

    # ------------------------------------------------------------------
    # Subscriber callbacks
    # ------------------------------------------------------------------

    def selected_trajectory_handler(self, msg: PoseArray) -> None:
        """
        Saves the most recently received path as a simple (N, 2) array of
        [x, y] points, and records when it arrived (used by the
        staleness check in main_heartbeat below).
        """
        self.path_pts = np.array(
            [[p.position.x, p.position.y] for p in msg.poses],
            dtype=np.float64,
        ) if msg.poses else np.empty((0, 2))
        self._path_stamp = self.get_clock().now()

    def main_heartbeat(self, msg: Pose) -> None:
        """
        Runs one full control decision every time a new car-position
        update arrives (rather than on a fixed timer), since the
        position update is the fastest-arriving signal this node has
        available to trigger on.
        """
        car_pose = msg
        self._car_pos = np.array([car_pose.position.x, car_pose.position.y])
        # Heading angle, read the same way the rest of this stack reads it
        # (see class docstring above for why).
        self._car_yaw = self.normalize_angle(car_pose.orientation.w)

        self._update_motion_estimate()

        self.target_speed = self.get_parameter('target_velocity').get_parameter_value().double_value
        # NOTE (missing input #2): ideally the target speed would vary
        # along the path — slower through corners, faster on straights —
        # so the controller can anticipate corners instead of just
        # reacting to them. The path message this node receives has no
        # field to carry a speed value at each point, so for now every
        # point on the path is chased at this same flat speed. Fixing this
        # properly needs a change on the path-planning side (adding a
        # speed value to each path point somehow), plus this node
        # interpolating against the car's position the way it already
        # does for the path itself.

        # ── Placeholder "go" wait: hold full brake until cleared ────────
        if not self._go_received:
            self.steering_angle = 0.0
            self.target_speed = 0.0
            self.accel_cmd = 0.0
            self.get_logger().warn("Waiting for GO (placeholder) — holding brake.", throttle_duration_sec=2.0)
            self.publish_ackermann()
            return

        # ── Path validity + staleness check ──────────────────────────────
        # Brakes if there isn't a usable path yet, or if the path hasn't
        # been updated recently enough to still be trusted.
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
        # Hands the current path and car state to the controller and gets
        # back a steering / throttle / brake decision. See control_utils.py
        # for what actually happens inside compute(), and the class
        # docstring above (notes #1/#2) for how car_speed/car_yaw_rate/
        # desired_speed are obtained on this car specifically.
        steer_out, throttle_out, brake_out = self._mpc.compute(
            path=self.path_pts,
            car_pos=self._car_pos,
            car_yaw=self._car_yaw,
            car_speed=self._car_speed,
            desired_speed=self.target_speed,
            car_yaw_rate=self._car_yaw_rate,
        )

        # steer_out comes back as a normalised value between -1 and 1.
        # Convert that fraction back into an actual angle in degrees (the
        # unit the output message expects) by multiplying by the
        # controller's own maximum steering angle. Reading that maximum
        # directly off the controller (self._mpc.u_max[0]) rather than
        # hardcoding it again here means this can never quietly drift out
        # of sync if that maximum is ever changed in control_utils.py.
        self.steering_angle = math.degrees(steer_out * self._mpc.u_max[0])

        # NOTE (missing input #5): the controller returns throttle and
        # brake as two separate fractions between 0 and 1. The message
        # type this node publishes on doesn't have separate throttle/brake
        # fields — it has a single combined "acceleration" number instead,
        # which is sent to the car's hardware independently of the speed
        # value (i.e. it isn't calculated from speed downstream — it has
        # to be filled in directly). So instead of only ever sending a
        # target speed and ignoring the controller's braking decision
        # entirely, this reconstructs a single signed acceleration value
        # from whichever of throttle/brake the controller actually chose,
        # and sends that. drive.speed is still sent alongside it as the
        # (currently flat, see note #2) target speed.
        #
        # KNOWN ISSUE, NOT FIXABLE FROM THIS FILE: the code further
        # downstream that turns this message into signals the car's
        # hardware understands currently rejects any negative value in
        # either the acceleration or speed field, and silently drops the
        # whole message if it sees one. In practice, that means braking
        # commands (which are negative accelerations) cannot currently
        # reach the car through this pipeline at all — the car can be
        # commanded to speed up, but not to actively brake. This is a
        # real safety gap. It needs to be fixed in that downstream code
        # (for example, by using a separate signal for "how hard to
        # brake" the same way it already does for the steering angle),
        # not in this file.
        if throttle_out > 0.0:
            self.accel_cmd = throttle_out * self._mpc.a_max
        else:
            self.accel_cmd = -brake_out * self._mpc.a_max_brake   # negative — see known issue above

        self.publish_ackermann()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _update_motion_estimate(self) -> None:
        """
        Estimates the car's current forward speed and turn rate by
        comparing this position update to the previous one, since this
        car doesn't have a dedicated speed/turn-rate sensor feeding this
        node directly.

        NOTE (missing input #1): this is a workaround, not the ideal
        source for these values. Comparing two position snapshots means
        any small jitter or noise in the position readings themselves
        gets amplified into the speed/turn-rate estimate — a real
        speed/turn-rate sensor would give a cleaner, more direct reading.
        Both values feed straight into how the controller judges how
        off-track the car is, so noisier readings here mean noisier
        steering and less consistent behaviour than a true sensor
        reading would give. If a proper speed/turn-rate sensor is ever
        added to this car, that should be wired in here directly, and
        this estimate should be removed.
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
        Sends the current steering/speed/acceleration command out on all
        three output topics. Unlike the previous controller (which only
        ever handled steering and always sent a fixed acceleration of
        zero), this one also sends the controller's actual throttle/brake
        decision via the acceleration field — see main_heartbeat() above
        for how that value is worked out, and for the known downstream
        issue that currently limits what effect braking commands have.
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
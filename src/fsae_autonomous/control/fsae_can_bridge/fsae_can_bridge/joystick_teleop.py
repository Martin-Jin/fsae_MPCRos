#!/usr/bin/env python3
# Gamepad teleop - manual driving. Deliberately minimal: steer, throttle, brake, deadman.
#
# Reads the stock ros-*-joy node's /joy (sensor_msgs/Joy = axes[] + buttons[]), so any pad
# the kernel recognises works and controllers differ only in which INDEX means what. Those
# indices are parameters, so retargeting a pad is a config change, not a code change.
#
# Controls (defaults verified on a PS4 pad, 2026-07-25 - see fsae_params.yaml):
#   X (Cross) HELD -> DEADMAN: nothing moves unless this is held (button_arm)
#   left stick X   -> steering      (axis_steer)
#   right trigger  -> throttle %    (axis_throttle)
#   left trigger   -> brake %       (axis_brake)
#
# The deadman: release X and every output goes to neutral (steer 0, throttle 0, brake 0) with
# ActuatorCmd.armed false. Frames keep flowing, so this is a soft stop: the kart coasts and the
# Arduino ECU stays live. There is no separate e-stop button - the old L1 binding was removed
# when X became the deadman, because two competing stop controls is worse than one you must
# actively hold.
#
# Pad lost (no /joy for joy_timeout) is a hard stop: actuator_cmd stops being published, the
# serial bridge stops sending frames, and the ECU's 200 ms watchdog trips its failsafe (HV cut,
# brake on). Same if this node dies.
#
# Going live on the ECU (at boot, or after any trip) is the firmware's "go handshake": hold X,
# squeeze the brake, keep the stick centred and throttle off for 3 s (ECU prints READY), then
# let go of the brake (ECU prints GO). See docs/ecu-safety-checks.md in autonomous_gokart.
#
# Publishes cmd_vel always (the live MoTeC/CAN path):
#   /fsae/control/cmd_vel        (AckermannDriveStamped) -> ack_to_can  -> MoTeC car
#
# actuator_cmd (the Arduino bench-rig path) is off in this file's defaults but ENABLED in
# fsae_params.yaml, which is what teleop.launch.py loads - so on the rig both paths publish:
#   /fsae/control/actuator_cmd   (ActuatorCmd)           -> serial_bridge -> Arduino rig
#
# NMPC steering mode (off unless auto_steer_topic and button_auto_steer are set; the go-kart
# NMPC launch, nmpc_gokart.launch.py, sets both):
#   X + R1 HELD     -> steering comes from the NMPC (auto_steer_topic, AckermannDriveStamped,
#                      steering_angle in road-wheel degrees, + = LEFT). Sent as
#                      S = auto_steer_sign * auto_steer_scale_<side> * nmpc_deg, side = left
#                      when nmpc_deg > 0. On the kart +S steers RIGHT (measured), so the kart
#                      launch sets auto_steer_sign -1.
#                      Throttle and brake stay on the triggers, so the driver keeps speed
#                      (the kart ECU firmware currently has its brake actuator disabled, so
#                      on the kart only the throttle trigger has an effect).
#   X alone         -> ordinary manual steering. Do the go handshake this way: it needs
#                      steering at exactly 0, which a live NMPC command never is.
#   NMPC stale (older than auto_steer_timeout) or in safe-stop (frame_id 'nmpc_safe_stop')
#                   -> steering 0 and throttle 0 while R1 is held; the brake trigger is passed on.
#
# The one guard kept: if /joy stops arriving (pad unplugged / out of range), cmd_vel goes to 0
# and actuator_cmd stops, rather than latching the last command. joy does not signal a
# disconnect - it just stops publishing - so without this a throttle command would run on forever.
import math

import rclpy
from rclpy.node import Node

from ackermann_msgs.msg import AckermannDrive, AckermannDriveStamped
from sensor_msgs.msg import Joy
from std_msgs.msg import Header

from fsae_interfaces.msg import ActuatorCmd


def trigger_percent(raw, rest, full):
    """Analogue trigger axis -> 0..100 %. Linux reports triggers as an axis resting at `rest`
    and running to `full` when pressed flat."""
    span = (rest - full) if abs(rest - full) > 1e-6 else 1.0
    return 100.0 * min(1.0, max(0.0, (rest - raw) / span))


class JoystickTeleop(Node):
    def __init__(self):
        super().__init__('joystick_teleop')

        self.declare_parameters(
            namespace='',
            parameters=[
                # --- output limits ---
                ('max_speed', 2.0),              # m/s, cmd_vel path (ack_to_can int()-truncates speed)
                ('max_angle', 22.0),             # degrees (ack_to_can rejects beyond +/-30)
                ('max_throttle_percent', 20.0),  # actuator_cmd path; fsae_params.yaml raises this to 50
                ('max_brake_percent', 100.0),
                ('max_steer_rate', 0.0),         # deg/s slew limit, 0 = off. Caps how fast the
                                                 # commanded angle can move (steering only).
                # Publishes /fsae/control/actuator_cmd for fsae_serial_bridge (Arduino bench
                # rig). Conservative default here; fsae_params.yaml turns it ON for the rig.
                ('actuator_cmd_enabled', False),

                # --- controller map (indices into Joy.axes / Joy.buttons) ---
                ('axis_steer', 0),
                ('axis_throttle', 4),
                ('axis_brake', 3),
                # Deadman button. MEASURED on the DS4 (054c:05c4) via /joy, 2026-09-19:
                # X (Cross) = button 1. HELD = drive; released = neutral. -1 disables the
                # deadman entirely (DANGEROUS on the rig - bench use only).
                ('button_arm', 1),
                # NMPC steering mode, see the header comment. '' / -1 = off.
                ('auto_steer_topic', ''),
                ('button_auto_steer', -1),
                ('auto_steer_timeout', 0.3),     # s; an older NMPC command counts as lost
                # +1 if +S steers LEFT, -1 if +S steers RIGHT. The NMPC is + = LEFT. On the
                # kart +S steers RIGHT (measured 2026-10-14, matches invert_steer: true), so
                # nmpc_gokart.launch.py passes -1. The ECU firmware comment (+S = left) is wrong
                # for this kart.
                ('auto_steer_sign', 1.0),
                # ECU S units per road-wheel degree, per side: the firmware's S -> pulse map is
                # asymmetric (-180 spans 1403 us, +180 only 847 us). UNMEASURED, see
                # docs/NMPC_GOKART_GROUND_TEST.md.
                ('auto_steer_scale_left', 1.0),
                ('auto_steer_scale_right', 1.0),

                # --- axis conditioning ---
                ('invert_steer', False),         # ROS convention: +ve steering_angle = LEFT
                ('steer_deadzone', 0.05),        # ignore |stick| below this (centre drift)
                ('trigger_rest', 1.0),           # axis value with the trigger released
                ('trigger_full', -1.0),          # axis value with the trigger pressed flat

                # --- timing ---
                ('publish_rate', 50.0),          # Hz; commands go out on a timer, not per Joy callback
                ('joy_timeout', 0.25),           # s of /joy silence before commanding neutral
            ]
        )

        g = self.get_parameter
        self.max_speed = g('max_speed').get_parameter_value().double_value
        self.max_angle = g('max_angle').get_parameter_value().double_value
        self.max_throttle_percent = g('max_throttle_percent').get_parameter_value().double_value
        self.max_brake_percent = g('max_brake_percent').get_parameter_value().double_value
        self.max_steer_rate = g('max_steer_rate').get_parameter_value().double_value
        self.actuator_cmd_enabled = g('actuator_cmd_enabled').get_parameter_value().bool_value

        self.axis_steer = g('axis_steer').get_parameter_value().integer_value
        self.axis_throttle = g('axis_throttle').get_parameter_value().integer_value
        self.axis_brake = g('axis_brake').get_parameter_value().integer_value
        self.button_arm = g('button_arm').get_parameter_value().integer_value
        self.auto_steer_topic = g('auto_steer_topic').get_parameter_value().string_value
        self.button_auto_steer = g('button_auto_steer').get_parameter_value().integer_value
        self.auto_steer_timeout = g('auto_steer_timeout').get_parameter_value().double_value
        self.auto_steer_sign = g('auto_steer_sign').get_parameter_value().double_value
        self.auto_steer_scale_left = g('auto_steer_scale_left').get_parameter_value().double_value
        self.auto_steer_scale_right = g('auto_steer_scale_right').get_parameter_value().double_value
        self.auto_steer_enabled = bool(self.auto_steer_topic) and self.button_auto_steer >= 0
        self.last_auto = None       # last NMPC AckermannDriveStamped
        self.last_auto_time = None

        self.invert_steer = g('invert_steer').get_parameter_value().bool_value
        self.steer_deadzone = g('steer_deadzone').get_parameter_value().double_value
        self.trigger_rest = g('trigger_rest').get_parameter_value().double_value
        self.trigger_full = g('trigger_full').get_parameter_value().double_value

        self.publish_rate = g('publish_rate').get_parameter_value().double_value
        self.joy_timeout = g('joy_timeout').get_parameter_value().double_value

        self.last_joy = None
        self.last_joy_time = None
        self.steer_cmd = 0.0        # slew-limited steering state, degrees (see max_steer_rate)
        self._last_dbg = None       # last printed debug tuple (print-on-change)
        self._dbg_beats = 0         # heartbeat counter so an idle terminal still ticks

        self.cmd_vel_pub = self.create_publisher(
            AckermannDriveStamped, '/fsae/control/cmd_vel', 10)
        self.actuator_cmd_pub = self.create_publisher(
            ActuatorCmd, '/fsae/control/actuator_cmd', 10)

        self.create_subscription(Joy, '/joy', self.joy_callback, 10)
        if self.auto_steer_enabled:
            self.create_subscription(
                AckermannDriveStamped, self.auto_steer_topic, self.auto_steer_callback, 10)
        self.dt = 1.0 / self.publish_rate
        self.create_timer(self.dt, self.publish_cmd)

        deadman = ('DISABLED - ALWAYS ARMED' if self.button_arm < 0
                   else f'button {self.button_arm} (HOLD to drive)')
        self.get_logger().info(
            f'joystick_teleop up - reading /joy | steer axis {self.axis_steer}, '
            f'throttle axis {self.axis_throttle}, brake axis {self.axis_brake} | deadman: {deadman} | '
            f'limits: {self.max_angle} deg, {self.max_speed} m/s, {self.max_throttle_percent}% throttle')
        if self.auto_steer_enabled:
            self.get_logger().info(
                f'NMPC steering mode ON: hold X + button {self.button_auto_steer} to steer from '
                f'{self.auto_steer_topic} (sign {self.auto_steer_sign:+.0f}, scale L '
                f'{self.auto_steer_scale_left} / R {self.auto_steer_scale_right}); '
                f'triggers keep throttle/brake')

    def auto_steer_callback(self, msg: AckermannDriveStamped):
        self.last_auto = msg
        self.last_auto_time = self.get_clock().now()

    def auto_steer_held(self):
        if not self.auto_steer_enabled or self.last_joy is None:
            return False
        if not (self.button_auto_steer < len(self.last_joy.buttons)):
            return False
        return self.last_joy.buttons[self.button_auto_steer] == 1

    def auto_steer_command(self):
        """NMPC steering in actuator degrees, or None when the NMPC command is stale or a
        safe-stop. None makes the caller steer straight and cut throttle."""
        if self.last_auto is None or self.last_auto_time is None:
            return None
        age = (self.get_clock().now() - self.last_auto_time).nanoseconds * 1e-9
        if age > self.auto_steer_timeout or self.last_auto.header.frame_id == 'nmpc_safe_stop':
            return None
        nmpc_deg = float(self.last_auto.drive.steering_angle)
        scale = self.auto_steer_scale_left if nmpc_deg > 0.0 else self.auto_steer_scale_right
        steer = self.auto_steer_sign * scale * nmpc_deg
        if not math.isfinite(steer):
            return None
        return max(-self.max_angle, min(self.max_angle, steer))

    def joy_callback(self, msg: Joy):
        self.last_joy = msg
        self.last_joy_time = self.get_clock().now()

    def link_is_live(self):
        if self.last_joy_time is None:
            return False
        age = (self.get_clock().now() - self.last_joy_time).nanoseconds * 1e-9
        return age <= self.joy_timeout

    def read_gamepad(self):
        """Map the current Joy state to (steer_deg, throttle_pct, brake_pct)."""
        axes = self.last_joy.axes

        raw = axes[self.axis_steer] if 0 <= self.axis_steer < len(axes) else 0.0
        # Rescale past the deadzone so steering ramps up from 0 at its edge instead of
        # jumping straight to deadzone * max_angle. Exactly 0 inside it matters: the ECU's
        # go handshake needs steering at exactly 0.
        if abs(raw) < self.steer_deadzone:
            raw = 0.0
        else:
            span = 1.0 - self.steer_deadzone
            raw = math.copysign((abs(raw) - self.steer_deadzone) / span, raw)
        if self.invert_steer:
            raw = -raw
        steer = raw * self.max_angle

        t_raw = axes[self.axis_throttle] if 0 <= self.axis_throttle < len(axes) else self.trigger_rest
        b_raw = axes[self.axis_brake] if 0 <= self.axis_brake < len(axes) else self.trigger_rest
        throttle = trigger_percent(t_raw, self.trigger_rest, self.trigger_full) \
            * (self.max_throttle_percent / 100.0)
        brake = trigger_percent(b_raw, self.trigger_rest, self.trigger_full) \
            * (self.max_brake_percent / 100.0)

        return steer, throttle, brake

    def arm_held(self):
        """True while the deadman button is physically held. button_arm < 0 disables the
        deadman (always armed) - bench escape hatch, not for use with a motor connected."""
        if self.button_arm < 0:
            return True
        if self.last_joy is None or not (self.button_arm < len(self.last_joy.buttons)):
            return False
        return self.last_joy.buttons[self.button_arm] == 1

    def debug_print(self, steer, throttle, brake, live, armed, mode='manual'):
        """Terminal readout for hands-on testing. Prints whenever anything changes, plus a
        slow heartbeat so a still controller still shows the node is alive."""
        key = (round(steer, 1), round(throttle, 1), round(brake, 1), live, armed, mode)
        self._dbg_beats += 1
        if key == self._last_dbg and self._dbg_beats < 100:   # ~2 s heartbeat at 50 Hz
            return
        self._last_dbg = key
        self._dbg_beats = 0
        if not live:
            state = 'PAD LOST -> ECU failsafe'
        elif not armed:
            state = 'X released -> neutral'
        elif mode == 'nmpc':
            state = 'X+R1 held - NMPC steering'
        elif mode == 'nmpc_lost':
            state = 'X+R1 held - NMPC LOST -> steer 0, throttle 0'
        else:
            state = 'X held - driving'
        self.get_logger().info(
            f'[{state}] steer={steer:+6.1f}deg  throttle={throttle:5.1f}%  brake={brake:5.1f}%')

    def publish_cmd(self):
        # Armed only while the pad is alive AND the deadman is held.
        live = self.link_is_live()
        armed = live and self.arm_held()
        mode = 'manual'
        if armed:
            steer, throttle, brake = self.read_gamepad()
            if self.auto_steer_held():
                auto = self.auto_steer_command()
                if auto is None:
                    mode = 'nmpc_lost'
                    steer, throttle = 0.0, 0.0
                else:
                    mode = 'nmpc'
                    steer = auto
        else:
            steer, throttle, brake = 0.0, 0.0, 0.0

        # Steering slew limit: cap how fast the commanded angle can move, in deg/s (0 = off).
        # Applied after the neutral case so a dropout / e-stop also unwinds smoothly to centre
        # rather than snapping. Steering only - throttle/brake stay raw so a dropout still
        # zeroes throttle instantly. Rate-independent: step scales with the tick dt.
        if self.max_steer_rate > 0.0:
            step = self.max_steer_rate * self.dt
            self.steer_cmd += max(-step, min(step, steer - self.steer_cmd))
            steer = self.steer_cmd

        stamp = self.get_clock().now().to_msg()
        steer = float(round(steer, 2))
        self.debug_print(steer, throttle, brake, live, armed, mode)

        # --- CAN / MoTeC path --- speed derived from throttle % so one trigger drives both paths.
        drive = AckermannDrive()
        drive.steering_angle = steer
        drive.steering_angle_velocity = 0.0
        drive.speed = float(round(self.max_speed * throttle / 100.0, 2))
        stamped = AckermannDriveStamped()
        stamped.header = Header(stamp=stamp, frame_id='joystick_teleop')
        stamped.drive = drive
        self.cmd_vel_pub.publish(stamped)

        # --- serial / Arduino path (gated on actuator_cmd_enabled; ON via fsae_params.yaml) ---
        # Pad lost: publish nothing, so the bridge sends no frames and the ECU's watchdog
        # trips its failsafe. A released deadman still publishes (neutral), so that stays
        # a soft stop.
        if self.actuator_cmd_enabled and live:
            actuator = ActuatorCmd()
            actuator.header = Header(stamp=stamp, frame_id='joystick_teleop')
            actuator.steering_angle = steer
            actuator.throttle_percent = float(round(throttle, 1))
            actuator.brake_percent = float(round(brake, 1))
            # The bridge forces a neutral frame whenever this is false, as a backstop.
            actuator.armed = armed
            self.actuator_cmd_pub.publish(actuator)

    def on_shutdown(self):
        """Leave the CAN path neutral rather than latched on the last command. The Arduino
        path needs nothing: once actuator_cmd stops, the ECU's watchdog trips its failsafe."""
        self.get_logger().info('SHUTTING DOWN - zeroing control signals')
        stamped = AckermannDriveStamped()
        stamped.header = Header(stamp=self.get_clock().now().to_msg(), frame_id='joystick_teleop')
        stamped.drive = AckermannDrive()
        try:
            self.cmd_vel_pub.publish(stamped)
        except Exception as e:  # Ctrl-C may have shut the ROS context down already
            self.get_logger().warn(f'could not publish the final zero cmd_vel: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = JoystickTeleop()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.on_shutdown()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

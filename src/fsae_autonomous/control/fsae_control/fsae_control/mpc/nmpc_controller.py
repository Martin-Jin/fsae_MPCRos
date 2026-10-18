"""
NMPC path-tracking controller node

Selected by the `controller:=nmpc` launch arg in control.launch.py; the
default remains `controller:=stanley` (stanley_controller.py), so launching
this node is strictly opt-in and nothing about the existing default launch
behaviour changes.

See docs/NMPC_INTEGRATION_GAPS.md for the full rationale behind every
`# GAP <id>` comment below -- this file only points at that document, it
does not re-explain each gap.

    in   /fsae/planning/selected_trajectory  geometry_msgs/PoseArray        planner centreline
    in   /fsae/slam/car_position             geometry_msgs/Pose             x,y in position; yaw in orientation.w
                                                                             (repo convention; NOT independently
                                                                             timestamped -- see GAP A4)
    in   <odom_topic>                        nav_msgs/Odometry              default /fsae/slam/car_odom (no
                                                                             publisher, GAP A1/A2/A3/A7). The kart
                                                                             launch points it at /zed/zed_node/odom.
                                                                             Preferred v_x/v_y/yaw_rate source while
                                                                             fresh (state_timeout_s); read from the
                                                                             twist, or differentiated from the
                                                                             stamped pose (odom_velocity_source)
    in   <imu_topic>                         sensor_msgs/Imu                default '' (off). When set, its
                                                                             angular_velocity.z replaces every
                                                                             other yaw-rate source while fresh
    in   /fsae/hardware/curr_vel             AckermannDriveStamped          PLACEHOLDER, GAP A1 -- this topic
                                                                             already exists in the repo's naming
                                                                             convention with 2 subscribers and 0
                                                                             publishers; 2nd-choice v_x source
    in   /fsae/hardware/drive_status         AckermannDriveStamped          can_decoder's decoded speed (1 m/s
                                                                             CAN-byte resolution); 3rd-choice
                                                                             v_x source, GAP A1
    in   /fsae/perception/cone_detection     fsae_interfaces/ConeDetection  proximity e-brake, car-local frame
    out  <cmd_topic>                         ackermann_msgs/AckermannDriveStamped  speed (m/s) + steer (deg);
                                                                             default /fsae/control/cmd_vel. frame_id
                                                                             is 'nmpc_safe_stop' on a safe-stop
                                                                             command, 'nmpc_controller' otherwise
    out  /fsae/control/accel_cmd             ackermann_msgs/AckermannDriveStamped  PLACEHOLDER, GAP B1 -- the
                                                                             NMPC's raw signed a_cmd (m/s^2) in
                                                                             .drive.acceleration; nothing
                                                                             consumes this yet
    out  /fsae/viz/nmpc_prediction_raw       geometry_msgs/PoseArray        RViz visualisation only, gated by
                                                                             NMPCParams.nmpc_publish_prediction_enabled
                                                                             (default off); "map"-frame Cartesian
                                                                             conversion of the predicted horizon,
                                                                             republished as a MarkerArray by
                                                                             fsae_visualization
    out  /fsae/viz/nmpc_telemetry            std_msgs/String (JSON)        nmpc_telemetry_gui.py only, gated by
                                                                             NMPCParams.nmpc_publish_telemetry_enabled
                                                                             (default off); last_telemetry dict plus
                                                                             vx_source/car_x/car_y/car_yaw, GAP F1
                                                                             stopgap (no telemetry infra exists here)

CONTROL LOOP PHASES (see _control_step)
----------------------------------------------------------------------------
  Phase 1 -- Emergency brake/reset if the planner path is missing/stale
             (>PATH_TIMEOUT old) or has fewer than 2 points, the SLAM pose
             hasn't arrived yet, or the path fails the forward-direction
             sanity check (GAP C7).
  Phase 2 -- Resolve v_x/v_y/yaw_rate from whichever source is actually live
             (see _resolve_state, GAP A1/A2/A3).
  Phase 3 -- Normal NMPC solve via NMPCController.compute(), wrapped in a
             try/except onto a safe (0 speed, 0 steer) command (GAP B6).
  Phase 4 -- Cone-proximity brake override: forces the speed command (not
             steering) to 0 if a cone is inside the dynamic braking corridor.
             After CONE_RESET_THRESHOLD seconds of continuous braking, the
             NMPC is reset exactly once (edge-triggered, re-armed once clear).
  Phase 5 -- Command adapter: derive a CAN-representable speed from the raw
             a_cmd (GAP B3), clamp steering to the tighter of the solver's
             own limit and max_steer_angle (GAP B4), finite/NaN-guard every
             field, and publish.
"""
import json
import math
import time

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy

from ackermann_msgs.msg import AckermannDriveStamped
from fsae_interfaces.msg import ConeDetection
from geometry_msgs.msg import Pose, PoseArray
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from std_msgs.msg import String

from fsae_control.control_utils import (
    curvature_speed, path_end_speed_cap, tracking_error_speed_gate,
)
from fsae_control.mpc.nmpc_core import NMPCController
from fsae_control.mpc.mpc_params import declare_mpc_params, mpc_params_from_node
from fsae_control.mpc.nmpc_params import declare_nmpc_params, nmpc_params_from_node

CONTROL_HZ = 20.0   # must match NMPCController(dt=0.05); dt = 1 / CONTROL_HZ

CONE_BRAKE_DIST      = 2.0    # m — forward corridor depth for cone proximity brake
CONE_BRAKE_WIDTH     = 0.18   # m — lateral half-width of braking corridor (36 cm total)
CONE_RESET_THRESHOLD = 0.3    # s — continuous cone-brake duration before one NMPC reset
PATH_TIMEOUT         = 0.5    # s — reset the NMPC if no fresh trajectory within this window

# Max rate (m/s^2) at which the speed TARGET may rise. Decreases are never
# rate-limited; delaying a brake request is the failure this is meant to
# prevent. Value tuned in simulation; UNVERIFIED on the car or kart.
SPEED_TARGET_RISE_RATE = 7.0

# Max speed error (m/s) the rise limiter is allowed to open up before it stops
# ramping and waits for the car. Value tuned in simulation; UNVERIFIED on the
# car or kart.
#
# SPEED_TARGET_RISE_RATE alone assumes the car can accelerate at that rate. From
# a standing start it cannot: the car does not break static friction for ~1 s,
# so the target ramps to ~7 m/s while the car is still stationary and banks a
# deficit it spends the next second chasing. The NMPC minimises one scalar cost
# over the horizon, so a speed error that large swamps the lateral term and the
# optimiser trades e_y away for speed it was never going to get. In simulation
# this shows as a sideways excursion at launch that self-corrects once the car
# is rolling; UNVERIFIED on the car or kart.
#
# Capping the DEFICIT rather than gating on measured speed is deliberate. A gate
# of the form "hold the target while v_actual is near zero" deadlocks: no target
# means no speed error, which means no throttle, which means the car never moves
# and the gate never opens. Holding at v_actual + DEFICIT_MAX always leaves a
# real speed error, so throttle still commands and the launch still happens; the
# ramp resumes by itself as the car closes the gap.
#
# Not specific to launch: the same rule stops the target running away after a
# spin or a heavy brake, for the same reason.
SPEED_TARGET_DEFICIT_MAX = 2.55
# Max rate (gate-units/s) at which tracking_error_speed_gate()'s output may
# change per tick, in EITHER direction — see control_utils' own docstring.
GATE_RATE_LIMIT = 2.0

# GAP C7: a path pointing away from the car's current heading (reversed or
# wrapped) would otherwise be projected onto with a wrong-signed e_y and
# steered on as if correct. Generous threshold (not a tuned value) — this
# only needs to catch a grossly wrong path, not flag ordinary path noise.
PATH_DIRECTION_MAX_ERROR_RAD = math.radians(120.0)

# GAP B6: how many consecutive failed/rejected ticks before the watchdog
# latches the safe command regardless of what the solver just returned.
WATCHDOG_MAX_CONSECUTIVE_FAILS = 5


def _wrap(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


class NMPCControllerNode(Node):
    def __init__(self):
        super().__init__('nmpc_controller')

        self.declare_parameters(
            namespace='',
            parameters=[
                ('v_max', 20.0),      # m/s — top speed on straights
                ('v_min', 1.5),       # m/s — minimum speed through tight corners
                ('steer_lp', 0.3),    # output steering low-pass (EMA); 1.0 disables
                # GAP B4: tighter of this and the solver's own control_limits.
                # MAX_STEER_RAD wins. Neither is verified against the real
                # rack yet — see NMPC_INTEGRATION_GAPS.md.
                ('max_steer_angle', 30.0),   # degrees
                # GAP B3: the CAN frame carries a speed, not an acceleration.
                # v_cmd = clip(v_meas + a_cmd * this, 0, v_max). Starting
                # value, not a validated constant -- expect to retune on the
                # rig.
                ('accel_to_speed_horizon_s', 0.25),   # s
                # Stop at the end of the path: the speed target is capped so the car
                # can still stop path_end_margin_m before the last waypoint at
                # path_end_decel, allowing path_end_lag_s of tracking lag. 0 disables. Comfort values, UNVERIFIED on the car or
                # kart. See control_utils.path_end_speed_cap.
                ('path_end_decel', 1.5),      # m/s^2
                ('path_end_margin_m', 0.5),   # m
                ('path_end_lag_s', 1.0),      # s, allowance for the NMPC's speed-tracking lag
                # State inputs. Defaults keep the original topic contract; the
                # go-kart launch (nmpc_gokart.launch.py) overrides them.
                ('odom_topic', '/fsae/slam/car_odom'),
                # 'twist' reads the Odometry twist. 'pose_diff' differentiates
                # the stamped pose instead, for an odometry source whose twist
                # is empty or untrusted.
                ('odom_velocity_source', 'twist'),
                ('odom_diff_lp', 0.5),       # EMA weight on pose_diff samples; 1.0 = raw
                ('use_measured_vy', True),   # false -> v_y = 0 (kinematic-regime vehicles)
                ('imu_topic', ''),           # '' = off
                ('imu_yaw_rate_sign', 1.0),  # flip to -1.0 if the IMU's z axis points down
                ('state_timeout_s', 0.3),    # odom/IMU older than this is ignored
                ('cmd_topic', '/fsae/control/cmd_vel'),
                # Vehicle model. -1.0 keeps nmpc_core._Plant's built-in
                # default, which was set for a simulated car; UNVERIFIED on
                # the car or kart.
                # The pose this node receives is the model's reference point:
                # lr is how far that point sits ahead of the rear axle, lf how
                # far it sits behind the front axle.
                ('plant_lf', -1.0),          # m
                ('plant_lr', -1.0),          # m
                ('plant_v_blend_lo', -1.0),  # m/s, fully kinematic model below this
                ('plant_v_blend_hi', -1.0),  # m/s, fully dynamic (tyre) model above this
                ('plant_tau_delta', -1.0),   # s, steering actuator lag
                ('plant_max_steer_deg', -1.0),   # road-wheel steering limit
            ],
        )
        self._v_max = self.get_parameter('v_max').get_parameter_value().double_value
        self._v_min = self.get_parameter('v_min').get_parameter_value().double_value
        self._steer_lp = self.get_parameter('steer_lp').get_parameter_value().double_value
        max_steer_deg = self.get_parameter('max_steer_angle').get_parameter_value().double_value
        self._accel_to_speed_horizon_s = self.get_parameter(
            'accel_to_speed_horizon_s').get_parameter_value().double_value
        g = self.get_parameter
        self._path_end_decel = g('path_end_decel').get_parameter_value().double_value
        self._path_end_margin_m = g('path_end_margin_m').get_parameter_value().double_value
        self._path_end_lag_s = g('path_end_lag_s').get_parameter_value().double_value
        odom_topic = g('odom_topic').get_parameter_value().string_value
        self._odom_velocity_source = g('odom_velocity_source').get_parameter_value().string_value
        if self._odom_velocity_source not in ('twist', 'pose_diff'):
            raise ValueError(
                f"odom_velocity_source must be 'twist' or 'pose_diff', got "
                f"{self._odom_velocity_source!r}")
        self._odom_diff_lp = g('odom_diff_lp').get_parameter_value().double_value
        self._use_measured_vy = g('use_measured_vy').get_parameter_value().bool_value
        imu_topic = g('imu_topic').get_parameter_value().string_value
        self._imu_yaw_rate_sign = g('imu_yaw_rate_sign').get_parameter_value().double_value
        self._state_timeout_s = g('state_timeout_s').get_parameter_value().double_value
        cmd_topic = g('cmd_topic').get_parameter_value().string_value
        plant_overrides = {}
        for field in ('lf', 'lr', 'v_blend_lo', 'v_blend_hi', 'tau_delta'):
            value = g(f'plant_{field}').get_parameter_value().double_value
            if value >= 0.0:
                plant_overrides[field] = value
        plant_max_steer_deg = g('plant_max_steer_deg').get_parameter_value().double_value
        max_steer_rad = math.radians(plant_max_steer_deg) if plant_max_steer_deg > 0.0 else None

        declare_mpc_params(self)
        mpc_params = mpc_params_from_node(self)
        declare_nmpc_params(self)
        nmpc_params = nmpc_params_from_node(self)
        if not nmpc_params.use_nmpc:
            self.get_logger().warn(
                'nmpc_controller launched with use_nmpc=false — this node '
                'always runs the NMPC regardless of that flag (there is no '
                'LTV-QP fallback in this repo); the flag is declared only '
                'so the MPCParams/NMPCParams field set stays complete. Set it '
                'true to silence this warning.'
            )

        # Always drives the live planner path (/fsae/planning/selected_trajectory)
        # with a speed target from its curvature. Precomputed path and speed-profile
        # CSVs are not supported: no recorded track exists for the car or the kart.
        # GAP F1: no telemetry_logger.py/scoring.py in this repo yet (stage 2,
        # deferred). Nothing is logged to CSV; solve/tracking diagnostics are
        # only available via the ROS logger below.
        self._delta_filt: float | None = None

        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        self.create_subscription(PoseArray, '/fsae/planning/selected_trajectory', self._path_cb, 10)
        self.create_subscription(Pose, '/fsae/slam/car_position', self._pose_cb, 10)
        # PLACEHOLDER (GAP A1/A2/A3/A7): no publisher exists in this repo
        # today. Subscribed unconditionally so a future state estimator on
        # this exact topic/type needs no change here.
        self.create_subscription(Odometry, odom_topic, self._odom_cb, sensor_qos)
        if imu_topic:
            self.create_subscription(Imu, imu_topic, self._imu_cb, sensor_qos)
        # PLACEHOLDER (GAP A1): already exists in the repo's own topic naming
        # with 2 subscribers and 0 publishers — not a new topic.
        self.create_subscription(
            AckermannDriveStamped, '/fsae/hardware/curr_vel', self._curr_vel_cb, 10)
        # 3rd-choice v_x source — can_decoder DOES publish this one, at 1 m/s
        # CAN-byte resolution (GAP A1).
        self.create_subscription(
            AckermannDriveStamped, '/fsae/hardware/drive_status', self._drive_status_cb, 10)
        self.create_subscription(
            ConeDetection, '/fsae/perception/cone_detection', self._cone_cb, 10)

        self.pub_cmd = self.create_publisher(AckermannDriveStamped, cmd_topic, 5)
        # PLACEHOLDER (GAP B1): nothing subscribes today. Exists so the raw
        # acceleration command is not silently discarded, and so a future
        # MoTeC channel / revised ack_to_can has something to read directly.
        self.pub_accel = self.create_publisher(
            AckermannDriveStamped, '/fsae/control/accel_cmd', 5)
        # RViz visualisation only (default off, see NMPCParams.
        # nmpc_publish_prediction_enabled): the NMPC's own predicted
        # trajectory, converted to Cartesian, republished as a MarkerArray by
        # fsae_visualization/visualise_trajectories.py.
        self.pub_nmpc_prediction = self.create_publisher(
            PoseArray, '/fsae/viz/nmpc_prediction_raw', 5)
        # GAP F1 stopgap (no telemetry infra exists in this repo): JSON-
        # serialised NMPCController.last_telemetry for nmpc_telemetry_gui.py,
        # gated off by default (NMPCParams.nmpc_publish_telemetry_enabled),
        # same convention as pub_nmpc_prediction above.
        self.pub_telemetry = self.create_publisher(
            String, '/fsae/viz/nmpc_telemetry', 5)
        self._nmpc_publish_telemetry_enabled = nmpc_params.nmpc_publish_telemetry_enabled

        self._path: np.ndarray = np.empty((0, 2))
        self._path_stamp = None          # GAP C6: arrival-time compromise
        self._have_pose = False
        self._car_pos = np.zeros(2)
        self._car_yaw = 0.0
        self._pose_stamp = None          # GAP A4: arrival-time compromise
        self._prev_yaw: float | None = None
        self._prev_yaw_time = None
        self._yaw_rate_est = 0.0         # GAP A3 fallback (finite-diff + light LP)

        # v_x fallback ladder state (GAP A1) — see _resolve_state().
        self._have_odom = False
        self._odom_stamp = None
        self._odom_prev = None           # (t, x, y, yaw) of the last odom pose, pose_diff only
        self._odom_filt = None           # filtered (v_x, v_y, r), pose_diff only
        self._imu_r = 0.0
        self._imu_stamp = None
        self._odom_vx = 0.0
        self._odom_vy = 0.0
        self._odom_r = 0.0
        self._have_curr_vel = False
        self._curr_vel_speed = 0.0
        self._have_drive_status = False
        self._drive_status_speed = 0.0
        self._open_loop_speed = 0.0      # last-resort v_x fallback (open-loop), see _control_step
        self._active_vx_source: str | None = None   # logged on change only

        self._v_des_prev: float | None = None
        self._gate_prev: float | None = None

        self._cones_local: np.ndarray = np.empty((0, 2))
        self._cone_brake_duration = 0.0
        self._cone_reset_done = False

        self._consecutive_solve_fails = 0   # GAP B6 watchdog

        dt = 1.0 / CONTROL_HZ
        self._mpc = NMPCController(
            dt=dt, params=mpc_params, nmpc=nmpc_params, logger=self.get_logger(),
            plant_overrides=plant_overrides, max_steer_rad=max_steer_rad,
        )
        # GAP B4: the tighter of the two limits, so the published command can
        # never exceed either the solver's own assumption or ack_to_can's
        # hard-rejection threshold.
        self._max_steer_deg = min(max_steer_deg, math.degrees(self._mpc.max_steer_rad))
        if plant_overrides or max_steer_rad is not None:
            self.get_logger().info(
                f'Vehicle model overrides: {plant_overrides}, '
                f'max steer {math.degrees(self._mpc.max_steer_rad):.1f} deg')

        self.create_timer(dt, self._control_step)
        self.get_logger().info(
            f'NMPC controller ready (N={self._mpc.N}, max_steer={self._max_steer_deg:.1f} deg) '
            '— waiting for a trajectory + car_position. See '
            'docs/NMPC_INTEGRATION_GAPS.md for every placeholder/compromise below.'
        )

    # ------------------------------------------------------------------
    # Subscribers (cache latest state; the timer does the work)
    # ------------------------------------------------------------------

    def _path_cb(self, msg: PoseArray) -> None:
        path = np.array(
            [[p.position.x, p.position.y] for p in msg.poses], dtype=np.float64
        ) if msg.poses else np.empty((0, 2))
        # The planner occasionally repeats a waypoint. The solver's spline reference
        # needs strictly increasing arc length and rejects such a path outright, so
        # drop zero-length steps here rather than lose the tick.
        if len(path) > 1:
            keep = np.concatenate(([True], np.any(np.diff(path, axis=0) != 0.0, axis=1)))
            path = path[keep]
        self._path = path
        self._path_stamp = self.get_clock().now()   # GAP C6: arrival time, no real header

    def _pose_cb(self, msg: Pose) -> None:
        # x,y in position; yaw (rad) is stuffed into orientation.w (repo convention).
        now = self.get_clock().now()
        new_yaw = float(msg.orientation.w)

        # GAP A3 fallback: finite-difference yaw across ticks when car_odom
        # has no publisher. Noisy and one tick delayed by construction — see
        # NMPC_INTEGRATION_GAPS.md A3 for why this is a bring-up aid only.
        if not self._fresh(self._odom_stamp) and self._prev_yaw is not None \
                and self._prev_yaw_time is not None:
            dt_s = (now - self._prev_yaw_time).nanoseconds * 1e-9
            if dt_s > 1e-3:
                raw_rate = _wrap(new_yaw - self._prev_yaw) / dt_s
                # Light low-pass so a single noisy VO yaw sample doesn't spike r.
                alpha = 0.3
                self._yaw_rate_est += alpha * (raw_rate - self._yaw_rate_est)
        self._prev_yaw = new_yaw
        self._prev_yaw_time = now

        self._car_pos = np.array([msg.position.x, msg.position.y])
        self._car_yaw = new_yaw
        self._pose_stamp = now   # GAP A4: arrival time, no real header
        self._have_pose = True

    def _odom_cb(self, msg: Odometry) -> None:
        # Body-frame velocity (x forward, y left), the REP 103 convention.
        # Highest-priority source for v_x/v_y/yaw_rate while fresh, see
        # _resolve_state().
        if self._odom_velocity_source == 'pose_diff':
            vel = self._odom_pose_diff(msg)
            if vel is None:
                return
            vx, vy, r = vel
        else:
            v = msg.twist.twist.linear
            vx, vy, r = float(v.x), float(v.y), float(msg.twist.twist.angular.z)
        self._have_odom = True
        self._odom_stamp = self.get_clock().now()
        self._odom_vx, self._odom_vy, self._odom_r = vx, vy, r

    def _odom_pose_diff(self, msg: Odometry):
        """(v_x, v_y, r) from two consecutive stamped odometry poses, or
        None until two usable samples exist. Uses the message's own header
        stamp, not arrival time, so transport jitter does not show up as
        speed noise. The displacement is rotated into the body frame at the
        mid-interval heading. A gap over 0.5 s restarts the estimate rather
        than averaging across it."""
        t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        pos = msg.pose.pose.position
        q = msg.pose.pose.orientation
        yaw = math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))
        prev = self._odom_prev
        self._odom_prev = (t, pos.x, pos.y, yaw)
        if prev is None:
            return None
        dt_s = t - prev[0]
        if dt_s <= 1e-3 or dt_s > 0.5:
            self._odom_filt = None
            return None
        dyaw = _wrap(yaw - prev[3])
        yaw_mid = prev[3] + 0.5 * dyaw
        dx, dy = pos.x - prev[1], pos.y - prev[2]
        c, s = math.cos(yaw_mid), math.sin(yaw_mid)
        raw = np.array([(c * dx + s * dy) / dt_s, (-s * dx + c * dy) / dt_s, dyaw / dt_s])
        if self._odom_filt is None:
            self._odom_filt = raw
        else:
            self._odom_filt = self._odom_filt + self._odom_diff_lp * (raw - self._odom_filt)
        return tuple(float(v) for v in self._odom_filt)

    def _imu_cb(self, msg: Imu) -> None:
        self._imu_r = self._imu_yaw_rate_sign * float(msg.angular_velocity.z)
        self._imu_stamp = self.get_clock().now()

    def _fresh(self, stamp) -> bool:
        return (stamp is not None
                and (self.get_clock().now() - stamp).nanoseconds * 1e-9 <= self._state_timeout_s)

    def _curr_vel_cb(self, msg: AckermannDriveStamped) -> None:
        self._have_curr_vel = True
        self._curr_vel_speed = float(msg.drive.speed)

    def _drive_status_cb(self, msg: AckermannDriveStamped) -> None:
        self._have_drive_status = True
        self._drive_status_speed = float(msg.drive.speed)

    def _cone_cb(self, msg: ConeDetection) -> None:
        pts = [[p.x, p.y] for p in msg.blue] + [[p.x, p.y] for p in msg.yellow]
        self._cones_local = np.array(pts, dtype=np.float64) if pts else np.empty((0, 2))

    # ------------------------------------------------------------------
    # State resolution (GAP A1/A2/A3/A7)
    # ------------------------------------------------------------------

    def _resolve_state(self):
        """
        Single priority ladder for v_x/v_y/yaw_rate, so every degradation is
        auditable in one place instead of scattered across the control step.
        Returns (v_x, v_y, yaw_rate, source_name).
        """
        imu_fresh = self._fresh(self._imu_stamp)
        if self._have_odom and self._fresh(self._odom_stamp):
            v_y = self._odom_vy if self._use_measured_vy else 0.0
            yaw_rate = self._imu_r if imu_fresh else self._odom_r
            return self._odom_vx, v_y, yaw_rate, 'car_odom+imu' if imu_fresh else 'car_odom'
        # v_y has no fallback source at all (GAP A2) — defaults to 0.0
        # regardless of which v_x/yaw_rate source below is active.
        v_y = 0.0
        # GAP A3 finite-difference fallback, unless the IMU is live.
        yaw_rate = self._imu_r if imu_fresh else self._yaw_rate_est
        if self._have_curr_vel:
            return self._curr_vel_speed, v_y, yaw_rate, 'curr_vel'
        if self._have_drive_status:
            return self._drive_status_speed, v_y, yaw_rate, 'drive_status'
        return self._open_loop_speed, v_y, yaw_rate, 'last_cmd (open-loop)'

    def _path_direction_ok(self, path: np.ndarray) -> bool:
        """GAP C7: reject a path pointing away from the car's own heading."""
        if len(path) < 2:
            return True
        seg = path[min(2, len(path) - 1)] - path[0]
        seg_len = float(np.linalg.norm(seg))
        if seg_len < 1e-3:
            return True   # too short to judge; don't false-trigger on noise
        path_yaw = math.atan2(seg[1], seg[0])
        return abs(_wrap(path_yaw - self._car_yaw)) < PATH_DIRECTION_MAX_ERROR_RAD

    def _check_cone_proximity(self, car_speed: float) -> bool:
        """True if a cone sits inside the dynamic forward braking corridor."""
        if len(self._cones_local) == 0:
            return False
        x_car = self._cones_local[:, 0]   # forward (+)
        y_car = self._cones_local[:, 1]   # left    (+)
        dynamic_brake_dist = float(np.clip(car_speed * 0.25, 0.6, CONE_BRAKE_DIST))
        return bool(np.any(
            (x_car > 0.2) & (x_car < dynamic_brake_dist) & (np.abs(y_car) < CONE_BRAKE_WIDTH)
        ))

    # ------------------------------------------------------------------
    # Publish helpers
    # ------------------------------------------------------------------

    def _publish_safe(self, reason: str) -> None:
        """GAP B6: an explicit zero command, published rather than skipped —
        ack_to_can silently latches the LAST frame on any rejected field, so
        never publishing is worse than publishing an honest stop."""
        msg = AckermannDriveStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        # Lets a downstream consumer (joystick_teleop's NMPC steering mode)
        # tell an honest stop apart from a commanded straight-ahead.
        msg.header.frame_id = 'nmpc_safe_stop'
        msg.drive.speed = 0.0
        msg.drive.steering_angle = 0.0
        msg.drive.acceleration = 0.0
        msg.drive.jerk = 0.0
        msg.drive.steering_angle_velocity = 0.0
        self.pub_cmd.publish(msg)
        self._open_loop_speed = 0.0
        self.get_logger().warn(f'NMPC safe-stop: {reason}', throttle_duration_sec=1.0)

    def _publish_nmpc_prediction(self, xy: np.ndarray) -> None:
        """RViz visualisation only — see pub_nmpc_prediction's own comment."""
        msg = PoseArray()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'map'
        for x, y in xy:
            p = Pose()
            p.position.x = float(x)
            p.position.y = float(y)
            p.orientation.w = 1.0
            msg.poses.append(p)
        self.pub_nmpc_prediction.publish(msg)

    def _publish_telemetry(self, vx_source: str) -> None:
        """GUI-consumption only (nmpc_telemetry_gui.py), gated by
        NMPCParams.nmpc_publish_telemetry_enabled -- see pub_telemetry's own
        comment. last_telemetry is already all-float; vx_source and the
        car's own pose are added since the GUI needs them and they don't
        belong inside NMPCController's own telemetry dict (control-node
        state, not solver state)."""
        tel = dict(self._mpc.last_telemetry)
        tel['vx_source'] = vx_source
        tel['car_x'] = float(self._car_pos[0])
        tel['car_y'] = float(self._car_pos[1])
        tel['car_yaw'] = float(self._car_yaw)
        msg = String()
        msg.data = json.dumps(tel)
        self.pub_telemetry.publish(msg)

    # ------------------------------------------------------------------
    # Control step (fixed 20 Hz)
    # ------------------------------------------------------------------

    def _control_step(self) -> None:
        _t_loop0 = time.perf_counter()

        # ── Phase 1: emergency brake/reset on stale/missing/bad path or pose ──
        path_stale = (
            self._path_stamp is None
            or (self.get_clock().now() - self._path_stamp).nanoseconds * 1e-9 > PATH_TIMEOUT
        )
        path_direction_bad = self._have_pose and len(self._path) >= 2 and not self._path_direction_ok(self._path)
        if not self._have_pose or len(self._path) < 2 or path_stale or path_direction_bad:
            self._mpc.reset()
            self._delta_filt = None
            self._v_des_prev = None
            self._gate_prev = None
            reason = (
                'no pose yet' if not self._have_pose else
                'path too short' if len(self._path) < 2 else
                'path stale' if path_stale else
                'path direction sanity check failed (GAP C7)'
            )
            self._publish_safe(reason)
            return

        # ── Phase 2: resolve v_x/v_y/yaw_rate (GAP A1/A2/A3) ─────────────
        car_speed, car_vy, car_yaw_rate, vx_source = self._resolve_state()
        if vx_source != self._active_vx_source:
            self.get_logger().warn(
                f'v_x source changed: {self._active_vx_source} -> {vx_source}'
            )
            self._active_vx_source = vx_source

        # ── Speed target: path curvature, tracking-error gate, rise-rate limiter ──
        path_ahead = self._path
        if len(path_ahead) > 2:
            i_near = int(np.argmin(np.linalg.norm(path_ahead - self._car_pos, axis=1)))
            if i_near < len(path_ahead) - 2:
                path_ahead = path_ahead[i_near:]
        v_curv = curvature_speed(path_ahead, v_max=self._v_max, v_min=self._v_min)

        tel = self._mpc.last_telemetry
        raw_gate = tracking_error_speed_gate(tel.get('e_y', 0.0), tel.get('e_psi', 0.0))
        if self._gate_prev is not None:
            max_step = GATE_RATE_LIMIT / CONTROL_HZ
            raw_gate = float(np.clip(raw_gate, self._gate_prev - max_step, self._gate_prev + max_step))
        self._gate_prev = raw_gate
        desired_speed = max(self._v_min, v_curv * raw_gate)

        if self._v_des_prev is None:
            self._v_des_prev = car_speed
        desired_speed = min(desired_speed, self._v_des_prev + SPEED_TARGET_RISE_RATE / CONTROL_HZ)
        # Stop ramping once the target has run this far ahead of the car; see
        # SPEED_TARGET_DEFICIT_MAX. Never DROPS the target (max against the
        # previous value), so a car that is merely slow does not get the target
        # dragged down to meet it, and a genuine brake request still passes
        # through the min() above untouched.
        if desired_speed - car_speed > SPEED_TARGET_DEFICIT_MAX:
            desired_speed = min(desired_speed,
                                max(self._v_des_prev,
                                    car_speed + SPEED_TARGET_DEFICIT_MAX))
        # End of path. Applied last, after the v_min floor, so the target can reach 0.
        # This lowers the speed the cost tracks (q_e_v); it is not a constraint, so the
        # solver plans the braking itself within its acceleration limits.
        v_end = path_end_speed_cap(
            self._path, self._car_pos, car_speed, self._path_end_decel,
            self._path_end_margin_m, self._path_end_lag_s)
        if v_end < desired_speed:
            desired_speed = v_end
            self.get_logger().info(
                f'Near the end of the path: speed target capped at {v_end:.2f} m/s',
                throttle_duration_sec=1.0)
        self._v_des_prev = desired_speed

        # GAP A4: pose_age_s measures age since ARRIVAL, not since capture —
        # under-counts true staleness by the perception pipeline's own
        # latency, since /fsae/slam/car_position carries no header.
        pose_age_s = (self.get_clock().now() - self._pose_stamp).nanoseconds * 1e-9

        # ── Phase 3: NMPC solve, guarded (GAP B6) ────────────────────────
        try:
            # compute() returns early without touching last_telemetry when it cannot
            # solve: fewer than 3 path points, or a path PathReference rejects (the
            # planner sends occasional 4-point paths that do this). Clear it first so
            # an early return reads as a failed solve here, not as last tick's command
            # published again as if it were fresh.
            self._mpc.last_telemetry = {}
            self._mpc.last_prediction_xy = None
            self._mpc.compute(
                path=self._path, car_pos=self._car_pos, car_yaw=self._car_yaw,
                car_speed=car_speed, desired_speed=desired_speed,
                car_yaw_rate=car_yaw_rate, pose_age_s=pose_age_s, car_vy=car_vy,
            )
            delta_cmd = float(self._mpc.last_telemetry.get('delta_cmd', math.nan))
            a_cmd = float(self._mpc.last_telemetry.get('a_cmd', math.nan))
            solve_ok = math.isfinite(delta_cmd) and math.isfinite(a_cmd)
            if self._mpc.last_prediction_xy is not None:
                self._publish_nmpc_prediction(self._mpc.last_prediction_xy)
        except Exception as exc:   # noqa: BLE001 — any solver failure must fail safe, not crash the node
            self.get_logger().error(f'NMPC compute() raised: {exc}', throttle_duration_sec=1.0)
            delta_cmd, a_cmd, solve_ok = 0.0, 0.0, False

        if solve_ok:
            self._consecutive_solve_fails = 0
        else:
            self._consecutive_solve_fails += 1

        if not solve_ok or self._consecutive_solve_fails >= WATCHDOG_MAX_CONSECUTIVE_FAILS:
            self._publish_safe(
                f'solve failed or non-finite output '
                f'({self._consecutive_solve_fails} consecutive)'
            )
            return

        # Telemetry publish is skipped on the safe-stop path above (return),
        # not zeroed-and-published — nmpc_telemetry_gui.py's own staleness
        # check covers the display side, and a frozen last-known reading is
        # more useful than a screenful of zeros during a safe-stop.
        if self._nmpc_publish_telemetry_enabled:
            self._publish_telemetry(vx_source)

        # Output steering low-pass (matches stanley_controller.py's own EMA
        # convention). 1.0 disables.
        if self._delta_filt is None or self._steer_lp >= 1.0:
            self._delta_filt = delta_cmd
        else:
            self._delta_filt += self._steer_lp * (delta_cmd - self._delta_filt)
        delta_cmd_filtered = self._delta_filt

        # ── Phase 5: command adapter ──────────────────────────────────────
        # GAP B4: clamp before publish, never after — ack_to_can rejects (and
        # silently latches the previous frame for) anything outside its
        # range, so the published value must already respect the tighter of
        # the solver's own limit and max_steer_angle.
        # GAP A5: sign convention (+ve = left, matching delta_cmd) is
        # unverified against the physical rack — resolve at bring-up rung 2
        # (jacked up, steering only) before trusting this on the ground.
        steer_deg = float(np.clip(
            math.degrees(delta_cmd_filtered), -self._max_steer_deg, self._max_steer_deg))

        # GAP B3: the CAN frame carries a speed, not the NMPC's own
        # acceleration output — integrate forward over a short fixed horizon.
        # v_meas is the resolved v_x from Phase 2, not desired_speed, so a
        # solver that's currently failing to track speed doesn't compound
        # that error into the conversion.
        v_cmd = float(np.clip(
            car_speed + a_cmd * self._accel_to_speed_horizon_s, 0.0, self._v_max))

        # ── Phase 4: cone-proximity brake override (speed only, not steering) ──
        if self._check_cone_proximity(car_speed):
            v_cmd = 0.0
            self._cone_brake_duration += 1.0 / CONTROL_HZ
            if self._cone_brake_duration >= CONE_RESET_THRESHOLD and not self._cone_reset_done:
                self._mpc.reset()
                self._v_des_prev = None
                self._gate_prev = None
                self._cone_reset_done = True
            self.get_logger().warn(
                f'Cone proximity brake active ({self._cone_brake_duration:.2f} s).',
                throttle_duration_sec=0.5,
            )
        else:
            self._cone_brake_duration = 0.0
            self._cone_reset_done = False

        if not (math.isfinite(steer_deg) and math.isfinite(v_cmd)):
            self._publish_safe('non-finite command after adapter (GAP B6)')
            return

        msg = AckermannDriveStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'nmpc_controller'
        msg.drive.speed = v_cmd
        msg.drive.steering_angle = steer_deg
        # GAP B7: ack_to_can drops the WHOLE message if either of these is
        # outside [0, 1] — set explicitly, exactly as stanley_controller.py
        # already does, rather than leaving them at the message default.
        msg.drive.acceleration = 0.0
        msg.drive.jerk = 0.0
        msg.drive.steering_angle_velocity = 0.0
        self.pub_cmd.publish(msg)
        # Open-loop v_x estimate for the next tick, used only when no speed source is
        # live: integrate a_cmd over one tick from this tick's v_x. Do not store v_cmd
        # here. v_cmd already leads v_x by a_cmd * accel_to_speed_horizon_s, so feeding
        # it back as next tick's v_x adds that lead again every tick and the estimate
        # climbs at (horizon / dt) = 5x the planned acceleration, reaching v_max within
        # a fraction of a second while the vehicle has not sped up. A short gap in the
        # odometry is enough to trigger it.
        self._open_loop_speed = 0.0 if v_cmd == 0.0 else float(np.clip(
            car_speed + a_cmd / CONTROL_HZ, 0.0, self._v_max))

        # GAP B1: raw signed acceleration, published so it is not silently
        # discarded. Nothing subscribes to this topic today.
        accel_msg = AckermannDriveStamped()
        accel_msg.header.stamp = msg.header.stamp
        accel_msg.drive.acceleration = a_cmd
        accel_msg.drive.speed = v_cmd
        self.pub_accel.publish(accel_msg)

        self.get_logger().info(
            f'NMPC v_x_src={vx_source} speed={v_cmd:.2f}/{desired_speed:.2f} m/s '
            f'steer={steer_deg:.2f} deg a_cmd={a_cmd:.2f} '
            f'solve_ms={tel.get("solve_ms", 0.0):.1f} '
            f'cmd_latency_ms={(time.perf_counter() - _t_loop0) * 1e3:.1f}',
            throttle_duration_sec=1.0,
        )


def main(args=None):
    rclpy.init(args=args)
    node = NMPCControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

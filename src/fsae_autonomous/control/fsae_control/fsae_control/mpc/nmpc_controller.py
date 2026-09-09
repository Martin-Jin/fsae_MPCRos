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
    in   /fsae/slam/car_odom                 nav_msgs/Odometry              PLACEHOLDER, GAP A1/A2/A3/A7 --
                                                                             no publisher exists yet; preferred
                                                                             v_x/v_y/yaw_rate source when present
    in   /fsae/hardware/curr_vel             AckermannDriveStamped          PLACEHOLDER, GAP A1 -- this topic
                                                                             already exists in the repo's naming
                                                                             convention with 2 subscribers and 0
                                                                             publishers; 2nd-choice v_x source
    in   /fsae/hardware/drive_status         AckermannDriveStamped          can_decoder's decoded speed (1 m/s
                                                                             CAN-byte resolution); 3rd-choice
                                                                             v_x source, GAP A1
    in   /fsae/perception/cone_detection     fsae_interfaces/ConeDetection  proximity e-brake, car-local frame
    out  /fsae/control/cmd_vel               ackermann_msgs/AckermannDriveStamped  speed (m/s) + steer (deg)
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
from std_msgs.msg import String

from fsae_control.control_utils import (
    curvature_speed, dynamic_speed_cap, load_path_profile_csv,
    load_path_heading_profile_csv,
    load_speed_profile_csv, precomputed_speed_at, tracking_error_speed_gate,
)
from fsae_control.mpc.control_limits import MAX_STEER_RAD as NMPC_MAX_STEER_RAD
from fsae_control.mpc.nmpc_core import NMPCController
from fsae_control.mpc.mpc_params import declare_mpc_params, mpc_params_from_node
from fsae_control.mpc.nmpc_params import declare_nmpc_params, nmpc_params_from_node

CONTROL_HZ = 20.0   # must match NMPCController(dt=0.05); dt = 1 / CONTROL_HZ

CONE_BRAKE_DIST      = 2.0    # m — forward corridor depth for cone proximity brake
CONE_BRAKE_WIDTH     = 0.18   # m — lateral half-width of braking corridor (36 cm total)
CONE_RESET_THRESHOLD = 0.3    # s — continuous cone-brake duration before one NMPC reset
PATH_TIMEOUT         = 0.5    # s — reset the NMPC if no fresh trajectory within this window

# Max rate (m/s^2) at which the speed TARGET may rise. Mirrors the sim tree's
# mpc_controller.py / sim/rollout_core.SPEED_TARGET_RISE_RATE — keep in sync
# if either changes. Decreases are never rate-limited; delaying a genuine
# brake request is the failure this is meant to prevent.
SPEED_TARGET_RISE_RATE = 7.0
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
                ('enable_dynamic_speed_cap', True),
                ('dynamic_cap_a_lat_max', 3.2),   # m/s^2
                ('dynamic_cap_safety', 0.9),
                # GAP B4: tighter of this and the solver's own control_limits.
                # MAX_STEER_RAD wins. Neither is verified against the real
                # rack yet — see NMPC_INTEGRATION_GAPS.md.
                ('max_steer_angle', 30.0),   # degrees
                # GAP B3: the CAN frame carries a speed, not an acceleration.
                # v_cmd = clip(v_meas + a_cmd * this, 0, v_max). Starting
                # value, not a validated constant -- expect to retune on the
                # rig.
                ('accel_to_speed_horizon_s', 0.25),   # s
                ('map_path', ''),       # '' -> live curvature_speed() (default);
                                        # see GAP C2 -- inert until a track CSV
                                        # exists for this repo.
                ('path_map_path', ''),  # '' -> live /fsae/planning/selected_trajectory
                                        # (default); see GAP C2.
                ('use_precomputed_heading_profile', False),
            ],
        )
        self._v_max = self.get_parameter('v_max').get_parameter_value().double_value
        self._v_min = self.get_parameter('v_min').get_parameter_value().double_value
        self._steer_lp = self.get_parameter('steer_lp').get_parameter_value().double_value
        self._enable_dynamic_speed_cap = self.get_parameter(
            'enable_dynamic_speed_cap').get_parameter_value().bool_value
        self._dynamic_cap_a_lat_max = self.get_parameter(
            'dynamic_cap_a_lat_max').get_parameter_value().double_value
        self._dynamic_cap_safety = self.get_parameter(
            'dynamic_cap_safety').get_parameter_value().double_value
        max_steer_deg = self.get_parameter('max_steer_angle').get_parameter_value().double_value
        # GAP B4: the tighter of the two limits, so the published command can
        # never exceed either the solver's own assumption or ack_to_can's
        # hard-rejection threshold.
        self._max_steer_deg = min(max_steer_deg, math.degrees(NMPC_MAX_STEER_RAD))
        self._accel_to_speed_horizon_s = self.get_parameter(
            'accel_to_speed_horizon_s').get_parameter_value().double_value

        declare_mpc_params(self)
        mpc_params = mpc_params_from_node(self)
        declare_nmpc_params(self)
        nmpc_params = nmpc_params_from_node(self)
        if not nmpc_params.use_nmpc:
            self.get_logger().warn(
                'nmpc_controller launched with use_nmpc=false — this node '
                'always runs the NMPC regardless of that flag (there is no '
                'LTV-QP fallback in this repo); the flag is declared only '
                'for MPCParams/NMPCParams field-name parity with the sim '
                'tree. Set it true to silence this warning.'
            )

        self._speed_profile = None  # (path_X, path_Y, path_V) or None — GAP C2
        map_path = self.get_parameter('map_path').get_parameter_value().string_value
        if map_path:
            try:
                self._speed_profile = load_speed_profile_csv(map_path)
                self.get_logger().info(
                    f'Loaded precomputed speed profile ({len(self._speed_profile[0])} pts) '
                    f'from {map_path} — using it instead of live curvature_speed().'
                )
            except (OSError, ValueError) as exc:
                self.get_logger().error(
                    f'Failed to load map_path={map_path}: {exc}. '
                    'Falling back to live curvature_speed().'
                )

        self._static_path: np.ndarray | None = None  # GAP C2
        path_map_path = self.get_parameter('path_map_path').get_parameter_value().string_value
        if path_map_path:
            try:
                self._static_path = load_path_profile_csv(path_map_path)
                self.get_logger().info(
                    f'Loaded precomputed path ({len(self._static_path)} pts) from '
                    f'{path_map_path} — planner output on /fsae/planning/selected_trajectory '
                    'will be ignored.'
                )
            except (OSError, ValueError) as exc:
                self.get_logger().error(
                    f'Failed to load path_map_path={path_map_path}: {exc}. '
                    'Falling back to the live planner topic.'
                )

        self._heading_profile: np.ndarray | None = None
        use_precomputed_heading_profile = self.get_parameter(
            'use_precomputed_heading_profile').get_parameter_value().bool_value
        if use_precomputed_heading_profile and path_map_path:
            try:
                self._heading_profile = load_path_heading_profile_csv(path_map_path)
            except (OSError, ValueError) as exc:
                self.get_logger().error(
                    f'Failed to load heading profile from path_map_path='
                    f'{path_map_path}: {exc}. Falling back to geometric heading.'
                )

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
        # this exact topic/type (matching the sim tree's own contract) needs
        # no change here.
        self.create_subscription(Odometry, '/fsae/slam/car_odom', self._odom_cb, sensor_qos)
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

        self.pub_cmd = self.create_publisher(AckermannDriveStamped, '/fsae/control/cmd_vel', 5)
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

        self._path: np.ndarray = (
            self._static_path if self._static_path is not None else np.empty((0, 2))
        )
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
        self._odom_vx = 0.0
        self._odom_vy = 0.0
        self._odom_r = 0.0
        self._have_curr_vel = False
        self._curr_vel_speed = 0.0
        self._have_drive_status = False
        self._drive_status_speed = 0.0
        self._last_cmd_speed = 0.0       # last-resort v_x fallback (open-loop)
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
        )
        if self._static_path is not None:
            if self._speed_profile is not None:
                sp_x, sp_y, sp_v = self._speed_profile
                self._mpc.set_static_path(
                    self._static_path,
                    path_v_xy=np.column_stack([sp_x, sp_y]), path_v=sp_v,
                )
            else:
                self._mpc.set_static_path(self._static_path)
        if self._heading_profile is not None:
            self._mpc.set_heading_profile(self._heading_profile)   # no-op on NMPC, kept for parity

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
        if self._static_path is not None:
            return
        self._path = np.array(
            [[p.position.x, p.position.y] for p in msg.poses], dtype=np.float64
        ) if msg.poses else np.empty((0, 2))
        self._path_stamp = self.get_clock().now()   # GAP C6: arrival time, no real header

    def _pose_cb(self, msg: Pose) -> None:
        # x,y in position; yaw (rad) is stuffed into orientation.w (repo convention).
        now = self.get_clock().now()
        new_yaw = float(msg.orientation.w)

        # GAP A3 fallback: finite-difference yaw across ticks when car_odom
        # has no publisher. Noisy and one tick delayed by construction — see
        # NMPC_INTEGRATION_GAPS.md A3 for why this is a bring-up aid only.
        if not self._have_odom and self._prev_yaw is not None and self._prev_yaw_time is not None:
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
        # PLACEHOLDER (GAP A1/A2/A3/A7): body-frame twist, same convention as
        # the sim tree's sim_perception.py. Highest-priority source for all
        # three of v_x/v_y/yaw_rate the moment this topic has a publisher.
        v = msg.twist.twist.linear
        self._have_odom = True
        self._odom_vx = float(v.x)
        self._odom_vy = float(v.y)
        self._odom_r = float(msg.twist.twist.angular.z)

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
        if self._have_odom:
            return self._odom_vx, self._odom_vy, self._odom_r, 'car_odom'
        # v_y has no fallback source at all (GAP A2) — defaults to 0.0
        # regardless of which v_x/yaw_rate source below is active.
        v_y = 0.0
        yaw_rate = self._yaw_rate_est   # GAP A3 finite-difference fallback
        if self._have_curr_vel:
            return self._curr_vel_speed, v_y, yaw_rate, 'curr_vel'
        if self._have_drive_status:
            return self._drive_status_speed, v_y, yaw_rate, 'drive_status'
        return self._last_cmd_speed, v_y, yaw_rate, 'last_cmd (open-loop)'

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
        msg.drive.speed = 0.0
        msg.drive.steering_angle = 0.0
        msg.drive.acceleration = 0.0
        msg.drive.jerk = 0.0
        msg.drive.steering_angle_velocity = 0.0
        self.pub_cmd.publish(msg)
        self._last_cmd_speed = 0.0
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
        if self._static_path is not None:
            path_stale = False
        else:
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

        # ── Speed target: curvature/oracle profile, tracking-error gate,
        #    rise-rate limiter — identical derivation to the sim tree ──────
        if self._speed_profile is not None:
            path_X, path_Y, path_V = self._speed_profile
            v_curv = precomputed_speed_at(self._car_pos, path_X, path_Y, path_V)
            if self._enable_dynamic_speed_cap:
                path_ahead = self._path
                if len(path_ahead) > 2:
                    i_near = int(np.argmin(np.linalg.norm(path_ahead - self._car_pos, axis=1)))
                    if i_near < len(path_ahead) - 2:
                        path_ahead = path_ahead[i_near:]
                v_cap = dynamic_speed_cap(
                    path_ahead, v_max=self._v_max, v_min=self._v_min,
                    a_lat_max=self._dynamic_cap_a_lat_max,
                    safety=self._dynamic_cap_safety,
                )
                v_curv = min(v_curv, v_cap)
        else:
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
        self._v_des_prev = desired_speed

        # GAP A4: pose_age_s measures age since ARRIVAL, not since capture —
        # under-counts true staleness by the perception pipeline's own
        # latency, since /fsae/slam/car_position carries no header.
        pose_age_s = (self.get_clock().now() - self._pose_stamp).nanoseconds * 1e-9

        # ── Phase 3: NMPC solve, guarded (GAP B6) ────────────────────────
        try:
            self._mpc.compute(
                path=self._path, car_pos=self._car_pos, car_yaw=self._car_yaw,
                car_speed=car_speed, desired_speed=desired_speed,
                car_yaw_rate=car_yaw_rate, pose_age_s=pose_age_s, car_vy=car_vy,
            )
            delta_cmd = float(self._mpc.last_telemetry.get('delta_cmd', 0.0))
            a_cmd = float(self._mpc.last_telemetry.get('a_cmd', 0.0))
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
        msg.drive.speed = v_cmd
        msg.drive.steering_angle = steer_deg
        # GAP B7: ack_to_can drops the WHOLE message if either of these is
        # outside [0, 1] — set explicitly, exactly as stanley_controller.py
        # already does, rather than leaving them at the message default.
        msg.drive.acceleration = 0.0
        msg.drive.jerk = 0.0
        msg.drive.steering_angle_velocity = 0.0
        self.pub_cmd.publish(msg)
        self._last_cmd_speed = v_cmd

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

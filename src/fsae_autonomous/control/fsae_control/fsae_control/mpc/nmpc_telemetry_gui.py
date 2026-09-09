#!/usr/bin/python3
"""
nmpc_telemetry_gui -- a small live matplotlib dashboard for the NMPC
controller: a bird's-eye view (triangle car marker, planner path, predicted
trajectory) plus scrolling e_y/e_psi/steering strip charts and a stat panel.

WORKS IDENTICALLY IN BENCH AND LIVE MODE. This file subscribes to exactly
five topics below and does no mock-vs-live branching at all -- possible
because /fsae/planning/selected_trajectory and /fsae/slam/car_position are
ALREADY genuinely live-published in the real stack (by the active planner
node and cone_detection_node respectively), not mock-only. See
MPC_NODE_DOCS.md's "Live telemetry GUI" section for the exact launch
commands in each mode.

    /fsae/planning/selected_trajectory   geometry_msgs/PoseArray        centerline for the bird's-eye view
    /fsae/slam/car_position              geometry_msgs/Pose             car position/yaw for the triangle marker
    /fsae/viz/nmpc_prediction_raw        geometry_msgs/PoseArray        predicted-path overlay
    /fsae/viz/nmpc_telemetry             std_msgs/String (JSON)         stat panel + vx_source (see nmpc_controller.py)
    /fsae/control/cmd_vel                ackermann_msgs/AckermannDriveStamped  actual post-clamp command

FALLBACK/PLACEHOLDER FIELDS: nmpc_controller.py's own v_x fallback ladder
(_resolve_state, see docs/NMPC_INTEGRATION_GAPS.md GAP A1/A2/A3/A7) is a
PRE-EXISTING, already-documented gap, not something new introduced by this
GUI -- car_odom/curr_vel have no publisher in EITHER bench or live mode
today. This GUI surfaces the controller's own already-computed choice
(vx_source, folded into the telemetry JSON) directly, colour-coded, rather
than silently showing stale numbers or re-deriving the fallback itself.

REQUIRES nmpc_publish_telemetry_enabled:=true on nmpc_controller (default
off) or the stat panel/strip charts stay on their "NO TELEMETRY" banner --
see TELEMETRY_STALE_S below.

NOT UNIT-TESTABLE: this is an interactive matplotlib app with a live ROS2
graph dependency. Verification is manual bring-up only (see
MPC_NODE_DOCS.md), the same posture mock_pose_path_publisher.py's own
module docstring already takes for itself.
"""
import collections
import json
import math
import threading

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Polygon
from matplotlib.transforms import Affine2D

import numpy as np
import rclpy
from rclpy.node import Node

from ackermann_msgs.msg import AckermannDriveStamped
from geometry_msgs.msg import Pose, PoseArray
from std_msgs.msg import String

ROLLING_WINDOW_S = 15.0
TELEMETRY_HZ_ASSUMED = 20.0   # matches nmpc_controller.py's CONTROL_HZ
ROLLING_N = int(ROLLING_WINDOW_S * TELEMETRY_HZ_ASSUMED)

AXES_HALF_WIDTH_M = 15.0      # bird's-eye view half-width, close-up not full-track
TELEMETRY_STALE_S = 1.0       # no telemetry msg within this window -> banner, not stale numbers

# Car triangle, local frame, nose along +X, roughly car-proportioned (metres).
_CAR_TRIANGLE = np.array([[0.6, 0.0], [-0.4, 0.3], [-0.4, -0.3]])

_VX_SOURCE_COLOR = {
    'car_odom': 'tab:green',
    'curr_vel': 'tab:orange',
    'drive_status': 'tab:orange',
}
_VX_SOURCE_DEFAULT_COLOR = 'tab:red'   # last_cmd (open-loop) or unknown


class NMPCTelemetryGUI(Node):
    def __init__(self):
        super().__init__('nmpc_telemetry_gui')

        self._latest_telemetry: dict | None = None
        self._latest_telemetry_t = None
        self._latest_path_xy: np.ndarray | None = None
        self._latest_prediction_xy: np.ndarray | None = None
        self._latest_car_pose = None    # (x, y, yaw)
        self._latest_cmd = None         # (speed_mps, steer_deg)

        self._t_hist = collections.deque(maxlen=ROLLING_N)
        self._ey_hist = collections.deque(maxlen=ROLLING_N)
        self._epsi_hist = collections.deque(maxlen=ROLLING_N)
        self._steer_hist = collections.deque(maxlen=ROLLING_N)
        self._t0 = self.get_clock().now()

        self.create_subscription(
            PoseArray, '/fsae/planning/selected_trajectory', self._path_cb, 10)
        self.create_subscription(Pose, '/fsae/slam/car_position', self._pose_cb, 10)
        self.create_subscription(
            PoseArray, '/fsae/viz/nmpc_prediction_raw', self._prediction_cb, 10)
        self.create_subscription(String, '/fsae/viz/nmpc_telemetry', self._telemetry_cb, 10)
        self.create_subscription(
            AckermannDriveStamped, '/fsae/control/cmd_vel', self._cmd_cb, 10)

    def _now_s(self) -> float:
        return (self.get_clock().now() - self._t0).nanoseconds * 1e-9

    # Every callback below only REPLACES a whole attribute (rebinds a name
    # to a new object) -- never in-place-mutates a container the animation
    # callback might be mid-read on. A single attribute rebind is atomic
    # under the GIL, so the animation callback always sees either the fully
    # old or fully new object, never a torn one -- no lock needed for this
    # access pattern. If a future change appended to a shared container
    # in place instead, a lock would become necessary; this comment is the
    # reason it isn't here today.

    def _path_cb(self, msg: PoseArray) -> None:
        self._latest_path_xy = np.array(
            [[p.position.x, p.position.y] for p in msg.poses])

    def _prediction_cb(self, msg: PoseArray) -> None:
        self._latest_prediction_xy = np.array(
            [[p.position.x, p.position.y] for p in msg.poses])

    def _pose_cb(self, msg: Pose) -> None:
        # yaw (rad) in orientation.w -- repo convention, not a real quaternion.
        self._latest_car_pose = (msg.position.x, msg.position.y, msg.orientation.w)

    def _cmd_cb(self, msg: AckermannDriveStamped) -> None:
        self._latest_cmd = (msg.drive.speed, msg.drive.steering_angle)

    def _telemetry_cb(self, msg: String) -> None:
        try:
            tel = json.loads(msg.data)
        except json.JSONDecodeError:
            return
        self._latest_telemetry = tel
        self._latest_telemetry_t = self._now_s()
        t = self._latest_telemetry_t
        self._t_hist.append(t)
        self._ey_hist.append(tel.get('e_y', 0.0))
        self._epsi_hist.append(tel.get('e_psi', 0.0))
        self._steer_hist.append(math.degrees(tel.get('delta_cmd', 0.0)))


def _build_figure():
    fig = plt.figure(figsize=(11, 6), constrained_layout=True)
    gs = fig.add_gridspec(3, 2, width_ratios=[1.3, 1.0])

    ax_map = fig.add_subplot(gs[:, 0])
    ax_map.set_aspect('equal')
    ax_map.set_title('Bird\'s-eye view')

    ax_ey = fig.add_subplot(gs[0, 1])
    ax_ey.set_ylabel('e_y (m)')
    ax_epsi = fig.add_subplot(gs[1, 1], sharex=ax_ey)
    ax_epsi.set_ylabel('e_psi (rad)')
    ax_steer = fig.add_subplot(gs[2, 1], sharex=ax_ey)
    ax_steer.set_ylabel('steer (deg)')
    ax_steer.set_xlabel('t (s)')

    path_line, = ax_map.plot([], [], '-', color='0.6', lw=1.5, label='path')
    pred_line, = ax_map.plot([], [], '-', color='tab:orange', lw=2.0, label='prediction')
    car_tri = Polygon(_CAR_TRIANGLE, closed=True, facecolor='tab:blue', edgecolor='k', zorder=5)
    ax_map.add_patch(car_tri)
    ax_map.legend(loc='upper right', fontsize=8)

    ey_line, = ax_ey.plot([], [], color='tab:blue')
    epsi_line, = ax_epsi.plot([], [], color='tab:purple')
    steer_line, = ax_steer.plot([], [], color='tab:green')

    stat_text = ax_map.text(
        0.02, 0.98, '', transform=ax_map.transAxes, va='top', ha='left',
        fontsize=8, family='monospace',
        bbox=dict(facecolor='white', alpha=0.8, edgecolor='0.7'))

    artists = {
        'ax_map': ax_map, 'ax_ey': ax_ey, 'ax_epsi': ax_epsi, 'ax_steer': ax_steer,
        'path_line': path_line, 'pred_line': pred_line, 'car_tri': car_tri,
        'ey_line': ey_line, 'epsi_line': epsi_line, 'steer_line': steer_line,
        'stat_text': stat_text,
    }
    return fig, artists


def _update(_frame, node: NMPCTelemetryGUI, artists: dict):
    a = artists

    if node._latest_path_xy is not None and len(node._latest_path_xy) > 0:
        a['path_line'].set_data(node._latest_path_xy[:, 0], node._latest_path_xy[:, 1])
    if node._latest_prediction_xy is not None and len(node._latest_prediction_xy) > 0:
        a['pred_line'].set_data(
            node._latest_prediction_xy[:, 0], node._latest_prediction_xy[:, 1])

    if node._latest_car_pose is not None:
        x, y, yaw = node._latest_car_pose
        a['car_tri'].set_transform(
            Affine2D().rotate(yaw).translate(x, y) + a['ax_map'].transData)
        a['ax_map'].set_xlim(x - AXES_HALF_WIDTH_M, x + AXES_HALF_WIDTH_M)
        a['ax_map'].set_ylim(y - AXES_HALF_WIDTH_M, y + AXES_HALF_WIDTH_M)

    if node._t_hist:
        t_arr = np.array(node._t_hist)
        a['ey_line'].set_data(t_arr, node._ey_hist)
        a['epsi_line'].set_data(t_arr, node._epsi_hist)
        a['steer_line'].set_data(t_arr, node._steer_hist)
        for ax, series in ((a['ax_ey'], node._ey_hist), (a['ax_epsi'], node._epsi_hist),
                           (a['ax_steer'], node._steer_hist)):
            ax.set_xlim(t_arr[0], max(t_arr[-1], t_arr[0] + 1.0))
            lo, hi = min(series), max(series)
            pad = max(0.1, (hi - lo) * 0.1)
            ax.set_ylim(lo - pad, hi + pad)

    stale = (
        node._latest_telemetry_t is None
        or node._now_s() - node._latest_telemetry_t > TELEMETRY_STALE_S
    )
    if stale:
        a['stat_text'].set_text(
            'NO TELEMETRY\nis nmpc_controller running with\n'
            'nmpc_publish_telemetry_enabled:=true?')
    else:
        tel = node._latest_telemetry
        vx_source = tel.get('vx_source', 'unknown')
        color = _VX_SOURCE_COLOR.get(vx_source, _VX_SOURCE_DEFAULT_COLOR)
        flag = '  [PLACEHOLDER]' if vx_source == 'last_cmd (open-loop)' else ''
        cmd_speed, cmd_steer = node._latest_cmd if node._latest_cmd else (0.0, 0.0)
        a['stat_text'].set_text(
            f"v_x source: {vx_source}{flag}\n"
            f"e_y={tel.get('e_y', 0.0):+.2f} m  e_psi={tel.get('e_psi', 0.0):+.2f} rad\n"
            f"kappa={tel.get('kappa', 0.0):+.3f} 1/m\n"
            f"steer={cmd_steer:+.1f} deg  speed={cmd_speed:.2f} m/s\n"
            f"throttle={tel.get('throttle', 0.0):.2f}  brake={tel.get('brake', 0.0):.2f}\n"
            f"solve_ms={tel.get('solve_ms', 0.0):.1f}"
        )
        a['stat_text'].set_bbox(dict(facecolor=color, alpha=0.25, edgecolor=color))

    return tuple(a.values())


def _spin_thread(node: NMPCTelemetryGUI) -> None:
    rclpy.spin(node)


def main(args=None):
    rclpy.init(args=args)
    node = NMPCTelemetryGUI()

    thread = threading.Thread(target=_spin_thread, args=(node,), daemon=True)
    thread.start()

    fig, artists = _build_figure()
    # interval=100 ms (10 Hz) redraw, deliberately below the 20 Hz data rate
    # -- a dashboard doesn't need to redraw faster than perceptible, and it
    # halves matplotlib's own CPU cost. cache_frame_data=False avoids
    # FuncAnimation's default unbounded frame cache for this indefinite-
    # length animation.
    anim = FuncAnimation(   # noqa: F841 -- must stay referenced or it's garbage collected mid-run
        fig, _update, fargs=(node, artists), interval=100, cache_frame_data=False)

    try:
        plt.show()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

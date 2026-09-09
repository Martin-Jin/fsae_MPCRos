"""
mock_pose_path_publisher -- hardware-free bench stimulus for nmpc_controller

Publishes a reference path on /fsae/planning/selected_trajectory and a car
pose on /fsae/slam/car_position, so nmpc_controller can be exercised (and its
/fsae/control/cmd_vel response, and, with nmpc_publish_prediction_enabled,
its predicted trajectory in RViz, watched) with no car, camera, CAN bus, or
perception/planning/SLAM node running at all -- see nmpc_bench.launch.py.

WHAT THIS IS NOT: a closed-loop plant simulation. The mocked pose is an
open-loop scripted trajectory, not a function of the controller's own output
-- nothing consumes /fsae/control/cmd_vel to move the mocked car. This
validates only "does the controller react correctly to a given instantaneous
state," not the full closed loop. It also does not replace
test_nmpc_signs_magnitudes.py's automated pytest sign/magnitude checks (those
call NMPCController.compute() directly, no ROS graph); this is the live,
ROS-topic-level, human-in-the-loop counterpart for manual bring-up/demo/
debugging.

SCENARIOS (see bench_scenarios.py for the path geometry itself):
  scenario=straight (default): kappa = 0 everywhere, so any steering response
  is attributable to e_y alone, not a curvature feed-forward term -- the
  original isolation this rig was built around, unchanged.
  scenario=gentle_turn/sharp_turn/s_curve: a curved reference, to watch the
  NMPC's curvature-tracking response instead. See sweep_on_curve below for
  how the car's pose behaves on these.

SWEEP_ON_CURVE: on the straight scenario (its declared default here is True,
so an unset launch behaves exactly as before this scenario library existed),
the car's y sweeps sinusoidally in the WORLD frame -- valid only because the
straight path is horizontal. On a curved scenario, nmpc_bench.launch.py
defaults this to False instead (see that file), so the car instead drives
ALONG the path with zero e_y, isolating pure curvature-tracking -- the mirror
image of the straight scenario's own e_y isolation. Set True explicitly on a
curved scenario to keep the old sine sweep, now applied perpendicular to the
path's local tangent (via PathReference.xy_at, not raw world-y).

RANDOMIZE_START: an orthogonal axis, independent of scenario -- offsets the
car's initial (y, yaw) from the path's own start pose by a bounded random
amount (see bench_scenarios.random_start_offset), to bench-test convergence
from an initial tracking error instead of starting on the path exactly.

Yaw is held at the path's own local heading (not the sweep's instantaneous
velocity vector), which would otherwise inject a simultaneously-varying
e_psi on top of e_y and confound the isolation either scenario relies on.
car_position's yaw convention (this repo's own, not a real quaternion) is
orientation.w = yaw_rad -- see nmpc_controller.py's module docstring.
"""
import math

import numpy as np
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Pose, PoseArray

from fsae_control.mpc import bench_scenarios as scen
from fsae_control.mpc.nmpc_core import PathReference

_SCENARIO_BUILDERS = {
    'straight': lambda p: scen.straight_path(p.path_length_m, p.path_spacing_m),
    'gentle_turn': lambda p: scen.turn_path(
        p.turn_radius_m, p.turn_arc_deg, spacing_m=p.path_spacing_m),
    'sharp_turn': lambda p: scen.turn_path(
        p.turn_radius_m, p.turn_arc_deg, spacing_m=p.path_spacing_m),
    's_curve': lambda p: scen.s_curve_path(
        p.turn_radius_m, p.turn_arc_deg, spacing_m=p.path_spacing_m),
}


class MockPosePathPublisher(Node):
    def __init__(self):
        super().__init__('mock_pose_path_publisher')

        self.declare_parameters(namespace='', parameters=[
            ('amplitude_m', 1.0),
            ('period_s', 8.0),
            ('forward_speed_mps', 3.0),
            ('path_length_m', 100.0),
            ('path_spacing_m', 0.5),
            ('scenario', 'straight'),
            ('sweep_on_curve', True),
            ('randomize_start', False),
            ('randomize_start_seed', 0),
            ('randomize_start_max_lateral_m', 1.0),
            ('randomize_start_max_heading_deg', 15.0),
            ('turn_radius_m', 15.0),
            ('turn_arc_deg', 45.0),
        ])
        self.amplitude_m = self.get_parameter('amplitude_m').get_parameter_value().double_value
        self.period_s = self.get_parameter('period_s').get_parameter_value().double_value
        self.forward_speed_mps = self.get_parameter(
            'forward_speed_mps').get_parameter_value().double_value
        self.path_length_m = self.get_parameter('path_length_m').get_parameter_value().double_value
        self.path_spacing_m = self.get_parameter(
            'path_spacing_m').get_parameter_value().double_value
        self.scenario = self.get_parameter('scenario').get_parameter_value().string_value
        self.sweep_on_curve = self.get_parameter(
            'sweep_on_curve').get_parameter_value().bool_value
        self.turn_radius_m = self.get_parameter('turn_radius_m').get_parameter_value().double_value
        self.turn_arc_deg = self.get_parameter('turn_arc_deg').get_parameter_value().double_value

        builder = _SCENARIO_BUILDERS.get(self.scenario)
        if builder is None:
            self.get_logger().warn(
                f"Unknown scenario '{self.scenario}', falling back to 'straight'.")
            self.scenario = 'straight'
            builder = _SCENARIO_BUILDERS['straight']
        path_xy = builder(self)

        # Real per-point heading, not the old hardcoded 0.0 -- only valid on
        # a horizontal path. atan2(dy, dx) per segment; the last point
        # repeats the second-to-last segment's heading (no segment past it).
        seg = np.diff(path_xy, axis=0)
        seg_psi = np.arctan2(seg[:, 1], seg[:, 0])
        path_psi = np.concatenate([seg_psi, seg_psi[-1:]]) if len(seg_psi) else np.zeros(1)

        self._path_msg = PoseArray()
        for (x, y), psi in zip(path_xy, path_psi):
            p = Pose()
            p.position.x = float(x)
            p.position.y = float(y)
            p.orientation.w = float(psi)
            self._path_msg.poses.append(p)

        # Reused for both the along-path drive (sweep_on_curve=False) and
        # the perpendicular-offset sweep (sweep_on_curve=True) below --
        # exactly the Frenet (s, e_y) -> Cartesian conversion nmpc_core.py's
        # own PathReference.xy_at() already implements, not reinvented here.
        self._ref = PathReference(path_xy)

        self._start_offset = (0.0, 0.0, 0.0)
        if self.get_parameter('randomize_start').get_parameter_value().bool_value:
            seed = self.get_parameter(
                'randomize_start_seed').get_parameter_value().integer_value
            max_lat = self.get_parameter(
                'randomize_start_max_lateral_m').get_parameter_value().double_value
            max_head = self.get_parameter(
                'randomize_start_max_heading_deg').get_parameter_value().double_value
            rng = np.random.default_rng(seed)
            self._start_offset = scen.random_start_offset(max_lat, max_head, rng)
            self.get_logger().info(
                f'randomize_start: sampled dy={self._start_offset[1]:.2f} m, '
                f'dyaw={math.degrees(self._start_offset[2]):.1f} deg (seed={seed})')

        self.path_pub = self.create_publisher(
            PoseArray, '/fsae/planning/selected_trajectory', 10)
        self.pose_pub = self.create_publisher(Pose, '/fsae/slam/car_position', 10)

        self._t0 = self.get_clock().now()
        self.create_timer(1.0 / 20.0, self._tick)  # matches nmpc_controller.py's CONTROL_HZ
        self.get_logger().info(
            f'mock_pose_path_publisher started: scenario={self.scenario}, '
            f'sweep_on_curve={self.sweep_on_curve}, amplitude={self.amplitude_m} m, '
            f'period={self.period_s} s, forward_speed={self.forward_speed_mps} m/s'
        )

    def _tick(self) -> None:
        stamp = self.get_clock().now()
        t = (stamp - self._t0).nanoseconds * 1e-9

        self.path_pub.publish(self._path_msg)

        s = self.forward_speed_mps * t
        if self.sweep_on_curve:
            e_y = self.amplitude_m * math.sin(2.0 * math.pi * t / self.period_s)
        else:
            e_y = 0.0
        x, y = self._ref.xy_at(s, e_y)
        yaw = float(self._ref.psi_ref_at(s))

        dx, dy, dyaw = self._start_offset
        cos_d, sin_d = math.cos(dyaw), math.sin(dyaw)
        x_off = x * cos_d - y * sin_d + dx
        y_off = x * sin_d + y * cos_d + dy

        pose = Pose()
        pose.position.x = float(x_off)
        pose.position.y = float(y_off)
        pose.orientation.w = yaw + dyaw   # yaw convention: radians in orientation.w, see module docstring
        self.pose_pub.publish(pose)


def main(args=None):
    rclpy.init(args=args)
    node = MockPosePathPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

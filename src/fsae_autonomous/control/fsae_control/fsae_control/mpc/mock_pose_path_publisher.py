"""
mock_pose_path_publisher -- hardware-free bench stimulus for nmpc_controller

Publishes a fixed straight reference path on /fsae/planning/selected_trajectory
and a car pose on /fsae/slam/car_position whose lateral offset sweeps back and
forth, so nmpc_controller can be exercised (and its /fsae/control/cmd_vel
response, and, with nmpc_publish_prediction_enabled, its predicted trajectory
in RViz, watched) with no car, camera, CAN bus, or perception/planning/SLAM
node running at all -- see nmpc_bench.launch.py.

WHAT THIS IS NOT: a closed-loop plant simulation. The mocked pose is an
open-loop scripted trajectory, not a function of the controller's own output
-- nothing consumes /fsae/control/cmd_vel to move the mocked car. This
validates only "does the controller react correctly to a given instantaneous
state," not the full closed loop. It also does not replace
test_nmpc_signs_magnitudes.py's automated pytest sign/magnitude checks (those
call NMPCController.compute() directly, no ROS graph); this is the live,
ROS-topic-level, human-in-the-loop counterpart for manual bring-up/demo/
debugging.

Path is a straight line (kappa = 0 everywhere) so any steering response is
attributable to e_y alone, not a curvature feed-forward term -- isolating the
one thing this rig exists to exercise. Yaw is held fixed at the path's own
heading (0 rad) rather than following the sweep's instantaneous velocity
vector, which would otherwise inject a simultaneously-varying e_psi on top of
e_y and confound the isolation. car_position's yaw convention (this repo's
own, not a real quaternion) is orientation.w = yaw_rad -- see
nmpc_controller.py's module docstring.
"""
import math

import numpy as np
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Pose, PoseArray


class MockPosePathPublisher(Node):
    def __init__(self):
        super().__init__('mock_pose_path_publisher')

        self.declare_parameters(namespace='', parameters=[
            ('amplitude_m', 1.0),
            ('period_s', 8.0),
            ('forward_speed_mps', 3.0),
            ('path_length_m', 100.0),
            ('path_spacing_m', 0.5),
        ])
        self.amplitude_m = self.get_parameter('amplitude_m').get_parameter_value().double_value
        self.period_s = self.get_parameter('period_s').get_parameter_value().double_value
        self.forward_speed_mps = self.get_parameter(
            'forward_speed_mps').get_parameter_value().double_value
        path_length_m = self.get_parameter('path_length_m').get_parameter_value().double_value
        path_spacing_m = self.get_parameter('path_spacing_m').get_parameter_value().double_value

        n_pts = max(2, int(path_length_m / path_spacing_m) + 1)
        xs = np.linspace(0.0, path_length_m, n_pts)
        self._path_msg = PoseArray()
        for x in xs:
            p = Pose()
            p.position.x = float(x)
            p.position.y = 0.0
            p.orientation.w = 0.0   # path heading is implicit (straight, +X); not read by name
            self._path_msg.poses.append(p)

        self.path_pub = self.create_publisher(
            PoseArray, '/fsae/planning/selected_trajectory', 10)
        self.pose_pub = self.create_publisher(Pose, '/fsae/slam/car_position', 10)

        self._t0 = self.get_clock().now()
        self.create_timer(1.0 / 20.0, self._tick)  # matches nmpc_controller.py's CONTROL_HZ
        self.get_logger().info(
            f'mock_pose_path_publisher started: amplitude={self.amplitude_m} m, '
            f'period={self.period_s} s, forward_speed={self.forward_speed_mps} m/s'
        )

    def _tick(self) -> None:
        stamp = self.get_clock().now()
        t = (stamp - self._t0).nanoseconds * 1e-9

        self.path_pub.publish(self._path_msg)

        pose = Pose()
        pose.position.x = self.forward_speed_mps * t
        pose.position.y = self.amplitude_m * math.sin(2.0 * math.pi * t / self.period_s)
        pose.orientation.w = 0.0   # yaw held at the path's fixed heading -- see module docstring
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

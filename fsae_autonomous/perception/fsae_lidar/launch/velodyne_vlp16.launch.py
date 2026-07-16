"""Bring up the Velodyne VLP-16 driver + pointcloud converter.

Thin wrapper around the stock ``velodyne`` metapackage launch, which starts:
  - velodyne_driver_node      (reads UDP packets from the sensor)
  - velodyne_transform_node   (converts packets -> /velodyne_points, frame_id 'velodyne')

REQUIRES the Velodyne packages to be installed from apt, e.g.:
    sudo apt install ros-$ROS_DISTRO-velodyne
(They are NOT vendored in this workspace — they're standard ROS packages
available on both humble (Jetson) and jazzy (dev box).)

The driver's default frame_id is 'velodyne', matching the URDF lidar frame and
the fusion node's lidar_frame param, so no remap is needed.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description() -> LaunchDescription:
    velodyne_share = get_package_share_directory('velodyne')
    vlp16_launch = os.path.join(
        velodyne_share, 'launch', 'velodyne-all-nodes-VLP16-launch.py')

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(vlp16_launch)),
    ])

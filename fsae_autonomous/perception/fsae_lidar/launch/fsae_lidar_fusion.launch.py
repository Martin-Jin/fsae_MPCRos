"""Launch the camera-LiDAR fusion node with parameters from params/lidar_fusion.yaml.

This launches ONLY the fusion node. It needs, at runtime:
  - the camera publishing /fsae/perception/cone_detection,
  - the Velodyne publishing /velodyne_points (see velodyne_vlp16.launch.py),
  - the TF camera_link -> velodyne (run fsae_description/description.launch.py,
    which loads the trolley URDF by default).
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    package_name = 'fsae_lidar'
    params_file = os.path.join(
        get_package_share_directory(package_name), 'params', 'lidar_fusion.yaml')

    return LaunchDescription([
        Node(
            package=package_name,
            executable='fusion_node',
            name='lidar_fusion',
            output='screen',
            parameters=[params_file],
        ),
    ])

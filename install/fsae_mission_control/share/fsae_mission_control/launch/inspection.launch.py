import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


# Interim per-package launch; full composition lives in fsae_bringup at Stage 3.
def generate_launch_description():
    config = os.path.join(get_package_share_directory('fsae_bringup'), 'config', 'fsae_params.yaml')
    return LaunchDescription([
        Node(
            package='fsae_mission_control',
            executable='inspection_mission_node',
            name='inspection_mission_node',
            output='screen',
            parameters=[config],
        ),
    ])

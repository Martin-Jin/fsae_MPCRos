import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


# Scrutineering / inspection: runs the scripted inspection routine (mission_control) over
# the CAN layer. Command source = inspection_mission_node (NOT autonomous driving).
# Mirrors the old gocart_bringup scrutineering.launch (base CAN + inspection).
#
# Args:
#   use_perception : false (default) | true  - bring up the camera too (dynamic inspections)
def generate_launch_description():
    launch_dir = os.path.join(get_package_share_directory('fsae_bringup'), 'launch')
    config = os.path.join(get_package_share_directory('fsae_bringup'), 'config', 'fsae_params.yaml')
    use_perception = LaunchConfiguration('use_perception')

    return LaunchDescription([
        DeclareLaunchArgument('use_perception', default_value='false'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(launch_dir, 'can.launch.py'))),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(launch_dir, 'perception.launch.py')),
            condition=IfCondition(use_perception)),
        Node(
            package='fsae_mission_control',
            executable='inspection_mission_node',
            name='inspection_mission_node',
            output='screen',
            parameters=[config],
        ),
    ])

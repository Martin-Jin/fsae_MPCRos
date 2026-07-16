import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


# Bench test: CAN layer + mock_stimulus (the bench command source) [+ viz]. No car /
# perception - drives /fsae/control/cmd_vel from mock params to verify ack_to_can -> CAN.
def generate_launch_description():
    launch_dir = os.path.join(get_package_share_directory('fsae_bringup'), 'launch')
    config = os.path.join(get_package_share_directory('fsae_bringup'), 'config', 'fsae_params.yaml')
    use_viz = LaunchConfiguration('use_viz')

    return LaunchDescription([
        DeclareLaunchArgument('use_viz', default_value='false'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(launch_dir, 'can.launch.py'))),
        Node(
            package='fsae_can_bridge',
            executable='mock_stimulus',
            name='mock_stimulus',
            output='screen',
            parameters=[config],
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(launch_dir, 'viz.launch.py')),
            condition=IfCondition(use_viz)),
    ])

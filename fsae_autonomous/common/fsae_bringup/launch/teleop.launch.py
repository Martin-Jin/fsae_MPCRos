import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


# Manual driving: PS4 joystick over the CAN layer. Command source = joystick_teleop.
# Needs the pyPS4Controller pip package and a paired controller at /dev/input/js0.
def generate_launch_description():
    launch_dir = os.path.join(get_package_share_directory('fsae_bringup'), 'launch')
    config = os.path.join(get_package_share_directory('fsae_bringup'), 'config', 'fsae_params.yaml')

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(launch_dir, 'can.launch.py'))),
        Node(
            package='fsae_can_bridge',
            executable='joystick_teleop',
            name='joystick_teleop',
            output='screen',
            parameters=[config],
        ),
    ])

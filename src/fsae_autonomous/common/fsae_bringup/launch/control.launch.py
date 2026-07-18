import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


# Control subsystem: Stanley lateral controller. Publishes /fsae/control/cmd_vel - this is
# the autonomous command source (see can.launch.py for the CAN bridge that consumes it).
def generate_launch_description():
    config = os.path.join(get_package_share_directory('fsae_bringup'), 'config', 'fsae_params.yaml')
    return LaunchDescription([
        Node(
            package='fsae_control',
            executable='controller',
            name='stanley_controller',
            output='screen',
            parameters=[config],
        ),
    ])

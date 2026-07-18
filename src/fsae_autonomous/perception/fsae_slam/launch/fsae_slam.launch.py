import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


# Launches the working Python SLAM node (cone_mapper). The C++ cone_landmark_mapper is
# a stub and is not launched by default.
def generate_launch_description():
    config = os.path.join(get_package_share_directory('fsae_bringup'), 'config', 'fsae_params.yaml')
    return LaunchDescription([
        Node(
            package='fsae_slam',
            executable='cone_mapper.py',
            name='cone_mapper',
            output='screen',
            parameters=[config],
        ),
    ])

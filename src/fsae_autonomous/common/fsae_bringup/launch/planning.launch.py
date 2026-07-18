import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


# Planning subsystem: launches ONE planner, selected by the `planner` arg.
#   fasttube                 - production (uses /fsae/slam/*_track, needs SLAM)
#   fasttube_without_kalman  - SLAM fallback (reads /fsae/perception/cone_detection)
#   centerline_planner       - centerline
# Node name == executable == config key, so params load from fsae_params.yaml.
def generate_launch_description():
    config = os.path.join(get_package_share_directory('fsae_bringup'), 'config', 'fsae_params.yaml')
    planner = LaunchConfiguration('planner')

    return LaunchDescription([
        DeclareLaunchArgument(
            'planner',
            default_value='fasttube',
            description='which planner to run: fasttube | fasttube_without_kalman | centerline_planner'),
        Node(
            package='fsae_planning',
            executable=planner,
            name=planner,
            output='screen',
            parameters=[config],
        ),
    ])

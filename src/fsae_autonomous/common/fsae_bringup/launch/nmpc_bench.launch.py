import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


# NMPC bench test: mock_pose_path_publisher (synthetic e_y sweep, see its own
# module docstring) + control.launch.py pinned to controller:=nmpc [+ viz].
# No car / camera / CAN / perception / planning / SLAM — deliberately does
# NOT include perception.launch.py / slam.launch.py / planning.launch.py /
# can.launch.py, that absence is the entire point. Watch /fsae/control/cmd_vel
# react live to a swept lateral offset. NOT a closed-loop plant simulation —
# see mock_pose_path_publisher.py.
def generate_launch_description():
    launch_dir = os.path.join(get_package_share_directory('fsae_bringup'), 'launch')
    config = os.path.join(get_package_share_directory('fsae_bringup'), 'config', 'fsae_params.yaml')
    use_viz = LaunchConfiguration('use_viz')

    return LaunchDescription([
        DeclareLaunchArgument('use_viz', default_value='false'),
        DeclareLaunchArgument('amplitude_m', default_value='1.0'),
        DeclareLaunchArgument('period_s', default_value='8.0'),
        DeclareLaunchArgument('forward_speed_mps', default_value='3.0'),
        DeclareLaunchArgument('path_length_m', default_value='100.0'),
        DeclareLaunchArgument('path_spacing_m', default_value='0.5'),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(launch_dir, 'control.launch.py')),
            launch_arguments={'controller': 'nmpc'}.items()),

        Node(
            package='fsae_control',
            executable='mock_pose_path_publisher',
            name='mock_pose_path_publisher',
            output='screen',
            parameters=[config, {
                'amplitude_m': LaunchConfiguration('amplitude_m'),
                'period_s': LaunchConfiguration('period_s'),
                'forward_speed_mps': LaunchConfiguration('forward_speed_mps'),
                'path_length_m': LaunchConfiguration('path_length_m'),
                'path_spacing_m': LaunchConfiguration('path_spacing_m'),
            }],
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(launch_dir, 'viz.launch.py')),
            condition=IfCondition(use_viz)),
    ])

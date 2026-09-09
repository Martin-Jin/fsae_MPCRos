import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import FileContent, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


# NMPC bench test: mock_pose_path_publisher (synthetic e_y sweep, see its own
# module docstring) + control.launch.py pinned to controller:=nmpc [+ viz +
# rviz2 itself, pre-configured to show the planner path and the NMPC's
# predicted trajectory]. No car / camera / CAN / perception / planning /
# SLAM — deliberately does NOT include perception.launch.py /
# slam.launch.py / planning.launch.py / can.launch.py, that absence is the
# entire point. Watch /fsae/control/cmd_vel react live to a swept lateral
# offset. NOT a closed-loop plant simulation — see mock_pose_path_publisher.py.
#
# One command gets the whole bench running, no separate terminals needed:
#   ros2 launch fsae_bringup nmpc_bench.launch.py use_viz:=true
def generate_launch_description():
    launch_dir = os.path.join(get_package_share_directory('fsae_bringup'), 'launch')
    config = os.path.join(get_package_share_directory('fsae_bringup'), 'config', 'fsae_params.yaml')
    rviz_config = os.path.join(
        get_package_share_directory('fsae_control'), 'mpc', 'nmpc_bench.rviz')
    use_viz = LaunchConfiguration('use_viz')

    return LaunchDescription([
        DeclareLaunchArgument('use_viz', default_value='false'),
        # Default true: use_viz's whole point is watching the predicted
        # trajectory, so opting into viz opts into publishing it too. Still
        # independently overridable (e.g. use_viz:=true
        # nmpc_publish_prediction_enabled:=false to watch cmd_vel only).
        DeclareLaunchArgument('nmpc_publish_prediction_enabled', default_value=use_viz),
        DeclareLaunchArgument('amplitude_m', default_value='1.0'),
        DeclareLaunchArgument('period_s', default_value='8.0'),
        DeclareLaunchArgument('forward_speed_mps', default_value='3.0'),
        DeclareLaunchArgument('path_length_m', default_value='100.0'),
        DeclareLaunchArgument('path_spacing_m', default_value='0.5'),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(launch_dir, 'control.launch.py')),
            launch_arguments={
                'controller': 'nmpc',
                'nmpc_publish_prediction_enabled':
                    LaunchConfiguration('nmpc_publish_prediction_enabled'),
            }.items()),

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

        # Renders an actual car body (not just a bare TF frame) at the live
        # map -> base_link transform cone_map_viz (started by viz.launch.py
        # above) broadcasts from /fsae/slam/car_position. gocartv1.urdf.xml's
        # root link is literally named "base_link", so no static offset is
        # needed. Every joint in this URDF is fixed, so robot_state_publisher
        # needs no JointState input -- see fsae_description's own
        # urdf_model.launch.py for the same pattern.
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            condition=IfCondition(use_viz),
            parameters=[{
                'robot_description': ParameterValue(
                    FileContent(os.path.join(
                        get_package_share_directory('fsae_description'),
                        'urdf', 'gocartv1.urdf.xml')),
                    value_type=str),
            }],
        ),

        ExecuteProcess(
            cmd=['rviz2', '-d', rviz_config],
            output='screen',
            condition=IfCondition(use_viz),
        ),
    ])

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


# Full autonomous pipeline:
#   description + perception + slam + planning + control + can [+ viz] [+ gui]
# Command source = stanley_controller (control). This is the "drive the track" launch.
#
# Args:
#   planner  : fasttube (default) | fasttube_without_kalman | centerline_planner
#   use_viz  : false (default) | true   - bring up RViz visualisation nodes
#   use_gui  : false (default) | true   - bring up nmpc_telemetry_gui.py (matplotlib
#              dashboard). Only meaningful with controller:=nmpc also passed — see
#              MPC_NODE_DOCS.md's "Live telemetry GUI" section.
#
# SLAM is skipped automatically when planner:=fasttube_without_kalman (that planner reads
# raw camera detections instead of SLAM tracks - the SLAM-broken fallback path).
def generate_launch_description():
    launch_dir = os.path.join(get_package_share_directory('fsae_bringup'), 'launch')
    planner = LaunchConfiguration('planner')
    use_viz = LaunchConfiguration('use_viz')
    use_gui = LaunchConfiguration('use_gui')

    def include(name, **kwargs):
        return IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(launch_dir, name)), **kwargs)

    run_slam = IfCondition(PythonExpression(["'", planner, "' != 'fasttube_without_kalman'"]))

    return LaunchDescription([
        DeclareLaunchArgument('planner', default_value='fasttube'),
        DeclareLaunchArgument('use_viz', default_value='false'),
        DeclareLaunchArgument('use_gui', default_value='false'),
        # Opting into the GUI opts into the telemetry topic it needs, same
        # pattern nmpc_bench.launch.py uses for its own use_gui. control.
        # launch.py auto-generates this arg from NMPCParams — no change
        # needed there, see nmpc_params.py's nmpc_publish_telemetry_enabled.
        DeclareLaunchArgument(
            'nmpc_publish_telemetry_enabled', default_value=use_gui),

        include('description.launch.py'),
        include('perception.launch.py'),
        include('slam.launch.py', condition=run_slam),
        include('planning.launch.py', launch_arguments={'planner': planner}.items()),
        include('control.launch.py', launch_arguments={
            'nmpc_publish_telemetry_enabled':
                LaunchConfiguration('nmpc_publish_telemetry_enabled'),
        }.items()),
        include('can.launch.py'),
        include('viz.launch.py', condition=IfCondition(use_viz)),

        Node(
            package='fsae_control',
            executable='nmpc_telemetry_gui',
            name='nmpc_telemetry_gui',
            output='screen',
            condition=IfCondition(use_gui),
        ),
    ])

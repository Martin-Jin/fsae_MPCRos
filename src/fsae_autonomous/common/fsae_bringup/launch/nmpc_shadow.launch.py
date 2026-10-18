import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


# NMPC shadow mode: debugging only. The NMPC NEVER drives.
#
# Run this alongside a normal launch that is already driving (Stanley on the kart, or
# teleop). It starts only nmpc_controller plus RViz and the telemetry dashboard. The NMPC
# reads the same live topics the driving stack produces (planner path, SLAM pose, ZED
# odometry and IMU) and publishes its command on /fsae/control/nmpc_shadow_cmd, which
# nothing consumes. So you can watch what the NMPC would do without it touching the kart.
#
#   ros2 launch fsae_bringup nmpc_shadow.launch.py                 # RViz + dashboard
#   ros2 launch fsae_bringup nmpc_shadow.launch.py use_gui:=false  # RViz only
#
# It does not start perception, SLAM, a planner, the pad, the serial bridge or the URDF:
# the driving launch provides those. If nothing publishes /fsae/planning/selected_trajectory
# and /fsae/slam/car_position, the NMPC sits in safe-stop and RViz shows nothing from it.
#
# Do NOT run it next to nmpc_gokart.launch.py: both start a node called nmpc_controller.
#
# Vehicle model: the same kart values as nmpc_gokart.launch.py (see that file and
# docs/NMPC_GOKART_GROUND_TEST.md). lf comes from a CAD wheelbase and is UNVERIFIED.
def generate_launch_description():
    config = os.path.join(get_package_share_directory('fsae_bringup'), 'config', 'fsae_params.yaml')
    rviz_config = os.path.join(
        get_package_share_directory('fsae_control'), 'mpc', 'nmpc_shadow.rviz')
    shadow_cmd = '/fsae/control/nmpc_shadow_cmd'
    use_rviz = LaunchConfiguration('use_rviz')
    use_gui = LaunchConfiguration('use_gui')

    def float_arg(name):
        return ParameterValue(LaunchConfiguration(name), value_type=float)

    return LaunchDescription([
        DeclareLaunchArgument('use_rviz', default_value='true'),
        DeclareLaunchArgument('use_gui', default_value='true',
                              description='matplotlib NMPC telemetry dashboard'),
        DeclareLaunchArgument('use_base_tf', default_value='true',
                              description='publish the identity map -> odom TF RViz needs; '
                                          'set false if the driving launch already runs viz.launch.py'),
        DeclareLaunchArgument('v_max', default_value='3.0'),
        DeclareLaunchArgument('v_min', default_value='1.0'),
        DeclareLaunchArgument('plant_lf', default_value='0.86'),
        DeclareLaunchArgument('plant_lr', default_value='0.14'),
        DeclareLaunchArgument('plant_max_steer_deg', default_value='25.0'),

        Node(
            package='fsae_control',
            executable='nmpc_controller',
            name='nmpc_controller',
            output='screen',
            parameters=[config, {
                'cmd_topic': shadow_cmd,
                'odom_topic': '/zed/zed_node/odom',
                'odom_velocity_source': 'pose_diff',
                'use_measured_vy': False,
                'imu_topic': '/zed/zed_node/imu/data',
                # Odometry arrives in bursts on the Jetson: by arrival time, gaps over
                # 0.3 s covered 7-43 % of logged laps (worse with more load), although
                # the stamps are evenly spaced at 15 Hz. At the 0.3 s default the
                # v_x source then flips to the open-loop estimate for much of the lap.
                # 1.0 s covers the longest logged gap (0.84 s); at kart speeds a
                # second-old speed is close enough.
                'state_timeout_s': 1.0,
                # Standstill steering damping (nmpc_standstill_*): the default band,
                # full damping below 0.5 m/s fading out by 3.0 m/s, covers the kart's
                # whole ground-test speed range (0.5-1.1 m/s on logged laps). Replaying
                # those laps, it cut the NMPC's steering to about 7 % of what the path
                # curvature needs (0.7 deg median against 8.7 deg). Narrowed to the
                # moment of launch, which brings it to about 75-80 %. UNVERIFIED on
                # the kart: check the launch for an early steer.
                'nmpc_standstill_speed': 0.1,
                'nmpc_standstill_fade_speed': 0.3,
                'v_max': float_arg('v_max'),
                'v_min': float_arg('v_min'),
                'plant_lf': float_arg('plant_lf'),
                'plant_lr': float_arg('plant_lr'),
                'plant_v_blend_lo': 8.0,
                'plant_v_blend_hi': 9.0,
                'plant_max_steer_deg': float_arg('plant_max_steer_deg'),
                'nmpc_publish_prediction_enabled': True,
                'nmpc_publish_telemetry_enabled': True,
            }],
            # The raw acceleration output is renamed too, so nothing on the driving
            # stack can ever pick it up.
            remappings=[('/fsae/control/accel_cmd', '/fsae/control/nmpc_shadow_accel_cmd')],
        ),

        Node(package='fsae_visualization', executable='base_tf',
             name='nmpc_shadow_base_tf', output='screen',
             condition=IfCondition(LaunchConfiguration('use_base_tf'))),
        # A private path_viz copy whose steering arrow shows the NMPC's (unsent) command
        # instead of the one actually driving the kart.
        Node(package='fsae_visualization', executable='path_viz',
             name='nmpc_shadow_viz', output='screen',
             remappings=[('/fsae/control/cmd_vel', shadow_cmd),
                         ('/fsae/viz/steering_arrow', '/fsae/viz/nmpc_shadow_steering_arrow')],
             condition=IfCondition(use_rviz)),
        ExecuteProcess(cmd=['rviz2', '-d', rviz_config], output='screen',
                       condition=IfCondition(use_rviz)),
        # The dashboard reads cmd_vel for its command panel; point it at the shadow command.
        Node(package='fsae_control', executable='nmpc_telemetry_gui',
             name='nmpc_telemetry_gui', output='screen',
             remappings=[('/fsae/control/cmd_vel', shadow_cmd)],
             condition=IfCondition(use_gui)),
    ])

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


# Go-kart NMPC ground test: STEERING ONLY. The NMPC steers, the driver keeps the throttle
# on the pad trigger. The ECU firmware's brake actuator is disabled, so L2 does not slow
# the kart. See docs/NMPC_GOKART_GROUND_TEST.md before running it.
#
#   description + perception + slam + planning      (same stack as autonomous.launch.py)
#   nmpc_controller  -> /fsae/control/nmpc_cmd       (NOT cmd_vel; nothing else reads it)
#   joy + joystick_teleop (NMPC steering mode)       -> /fsae/control/actuator_cmd
#   serial_bridge    -> hub Arduino ECU over USB serial
#   [use_rviz] base_tf + path_viz + rviz2            [use_gui] nmpc_telemetry_gui
#
# Pad (PS4): hold X = deadman (manual steering, triggers drive). Hold X + R1 = NMPC steers,
# triggers still drive. Release X = neutral frames. Pad lost = ECU failsafe. Go handshake:
# hold X and the brake, stick centred, throttle off, for 3 s, then let go of the brake.
#
# Not launched on purpose:
#   - stanley_controller / control.launch.py: one steering source only.
#   - can.launch.py: the kart is on the serial path (teleop.launch.py's bench_rig:=true).
#   - cone_map_viz: it broadcasts map -> base_link, but base_link already has a parent
#     (odom -> zed_camera_link -> base_link from the ZED wrapper + URDF). TF allows one.
#
# Vehicle model (plant_* below): the pose on /fsae/slam/car_position is the ZED left lens,
# 0.14 m ahead of the rear axle (gocartv2.urdf.xml, tape-measured). The wheelbase, 1.00 m,
# is read off the CAD mesh go_cart_base.stl (tyre contact patches at x = 0.00 and 0.995 m);
# UNVERIFIED, not tape-measured. So lr = 0.14, lf = 1.00 - 0.14 = 0.86.
# v_blend_lo/hi are raised so the model stays purely kinematic at ground-test speeds,
# where it needs only the wheelbase; the tyre constants (m, Iz, Cf, Cr) are the built-in
# defaults for a simulated car, not the kart's (UNVERIFIED), and are never used below 8 m/s.
def generate_launch_description():
    launch_dir = os.path.join(get_package_share_directory('fsae_bringup'), 'launch')
    config = os.path.join(get_package_share_directory('fsae_bringup'), 'config', 'fsae_params.yaml')
    rviz_config = os.path.join(
        get_package_share_directory('fsae_control'), 'mpc', 'nmpc_gokart.rviz')
    use_rviz = LaunchConfiguration('use_rviz')
    use_gui = LaunchConfiguration('use_gui')

    def include(name, **kwargs):
        return IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(launch_dir, name)), **kwargs)

    def bool_arg(name):
        return ParameterValue(LaunchConfiguration(name), value_type=bool)

    def float_arg(name):
        return ParameterValue(LaunchConfiguration(name), value_type=float)

    return LaunchDescription([
        DeclareLaunchArgument('planner', default_value='fasttube',
                              description='fasttube | centerline_planner'),
        DeclareLaunchArgument('use_rviz', default_value='true'),
        DeclareLaunchArgument('use_gui', default_value='false',
                              description='matplotlib NMPC telemetry dashboard'),
        DeclareLaunchArgument('v_max', default_value='3.0',
                              description='m/s; the speed the NMPC plans for (the driver sets the real one)'),
        DeclareLaunchArgument('v_min', default_value='1.0'),
        DeclareLaunchArgument('button_auto_steer', default_value='5',
                              description='Joy button held (with X) for NMPC steering. 5 = R1 on '
                                          'the DS4 under hid-sony; check with ros2 topic echo /joy'),
        # +S steers RIGHT on the kart (measured on the Stanley steering test);
        # the NMPC is + = LEFT, hence -1.
        DeclareLaunchArgument('auto_steer_sign', default_value='-1.0',
                              description='+1 if +S steers left, -1 if +S steers right'),
        DeclareLaunchArgument('auto_steer_scale_left', default_value='1.0',
                              description='ECU S per road-wheel degree, left (UNMEASURED)'),
        DeclareLaunchArgument('auto_steer_scale_right', default_value='1.0',
                              description='ECU S per road-wheel degree, right (UNMEASURED)'),
        DeclareLaunchArgument('plant_lf', default_value='0.86'),
        DeclareLaunchArgument('plant_lr', default_value='0.14'),
        DeclareLaunchArgument('plant_max_steer_deg', default_value='25.0',
                              description='road-wheel steering limit; kart lock not yet measured'),

        include('description.launch.py'),
        include('perception.launch.py', launch_arguments={'publish_car_position': 'false'}.items()),
        include('slam.launch.py'),
        include('planning.launch.py', launch_arguments={'planner': LaunchConfiguration('planner')}.items()),

        Node(
            package='fsae_control',
            executable='nmpc_controller',
            name='nmpc_controller',
            output='screen',
            parameters=[config, {
                'cmd_topic': '/fsae/control/nmpc_cmd',
                # ZED visual-inertial odometry: the stamped pose is differentiated for
                # v_x, because the wrapper's twist has not been checked on this rig.
                'odom_topic': '/zed/zed_node/odom',
                'odom_velocity_source': 'pose_diff',
                'use_measured_vy': False,
                # ZED 2i IMU for yaw rate. The camera is pitched 7.7 deg down, which
                # scales the z-axis reading by cos(7.7 deg) = 0.991; not corrected.
                'imu_topic': '/zed/zed_node/imu/data',
                'v_max': float_arg('v_max'),
                'v_min': float_arg('v_min'),
                'plant_lf': float_arg('plant_lf'),
                'plant_lr': float_arg('plant_lr'),
                'plant_v_blend_lo': 8.0,
                'plant_v_blend_hi': 9.0,
                'plant_max_steer_deg': float_arg('plant_max_steer_deg'),
                'nmpc_publish_prediction_enabled': bool_arg('use_rviz'),
                'nmpc_publish_telemetry_enabled': bool_arg('use_gui'),
            }],
        ),

        Node(
            package='joy',
            executable='joy_node',
            name='joy_node',
            output='screen',
            parameters=[{'device_id': 0, 'deadzone': 0.0, 'autorepeat_rate': 20.0}],
        ),
        Node(
            package='fsae_can_bridge',
            executable='joystick_teleop',
            name='joystick_teleop',
            output='screen',
            parameters=[config, {
                'auto_steer_topic': '/fsae/control/nmpc_cmd',
                'button_auto_steer': ParameterValue(
                    LaunchConfiguration('button_auto_steer'), value_type=int),
                'auto_steer_sign': float_arg('auto_steer_sign'),
                'auto_steer_scale_left': float_arg('auto_steer_scale_left'),
                'auto_steer_scale_right': float_arg('auto_steer_scale_right'),
            }],
        ),
        Node(
            package='fsae_serial_bridge',
            executable='serial_bridge_node',
            name='serial_bridge',
            output='screen',
            parameters=[config],
        ),

        Node(package='fsae_visualization', executable='base_tf',
             name='static_transform_publisher', output='screen',
             condition=IfCondition(use_rviz)),
        Node(package='fsae_visualization', executable='path_viz',
             name='publish_path_planning_msgs', output='screen',
             condition=IfCondition(use_rviz)),
        ExecuteProcess(cmd=['rviz2', '-d', rviz_config], output='screen',
                       condition=IfCondition(use_rviz)),
        Node(package='fsae_control', executable='nmpc_telemetry_gui',
             name='nmpc_telemetry_gui', output='screen',
             condition=IfCondition(use_gui)),
    ])

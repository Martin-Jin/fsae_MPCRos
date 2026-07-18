from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import FileContent, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


# NOTE (port): the old launch referenced a non-existent package 'urdf_gocart' and an
# incorrect urdf path. Corrected to this package (fsae_description) and the installed
# urdf/ subdir so it actually resolves.
#
# The 'urdf' arg selects the platform. Default is the TROLLEY ('trolly.urdf.xml')
# because that is the rig autonomy is currently tested on; pass urdf:=gocartv1.urdf.xml
# for the go-kart. robot_state_publisher publishes the static sensor frames
# (base_link -> camera_link / velodyne / zed_camera_optical_frame) from whichever URDF.
def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    urdf_file = LaunchConfiguration('urdf', default='trolly.urdf.xml')
    urdf = FileContent(
        PathJoinSubstitution([FindPackageShare('fsae_description'), 'urdf', urdf_file]))
    # robot_description must be an explicit string param. Without value_type=str,
    # launch tries to parse the URDF XML as YAML and the launch aborts.
    robot_description = ParameterValue(urdf, value_type=str)

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation (Gazebo) clock if true'),
        DeclareLaunchArgument(
            'urdf',
            default_value='trolly.urdf.xml',
            description='URDF filename in fsae_description/urdf to load '
                        '(trolly.urdf.xml = trolley test rig, gocartv1.urdf.xml = go-kart)'),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time, 'robot_description': robot_description}]),
        Node(
            package='fsae_description',
            executable='state_publisher',
            name='state_publisher',
            output='screen'),
    ])

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


# Perception subsystem: the official zed_ros2_wrapper (owns the ZED 2i camera + SDK) plus
# our cone-detection node (fsae_camera), which subscribes to the wrapper's image/depth/
# camera_info/pose topics, plus the LiDAR pipeline (Velodyne VLP-16 driver + camera-LiDAR
# fusion). Jetson-only (CUDA + TensorRT). The LiDAR halves reuse fsae_lidar's own launch
# files, so they can still be brought up standalone (`ros2 launch fsae_lidar ...`) exactly
# as before; here they just come up together with the camera by default.
def generate_launch_description():
    config = os.path.join(get_package_share_directory('fsae_bringup'), 'config', 'fsae_params.yaml')
    lidar_launch = os.path.join(get_package_share_directory('fsae_lidar'), 'launch')

    # The wrapper node — this is what actually talks to the camera hardware via the ZED SDK.
    # Its SDK-param overrides (depth_mode, resolution, etc.) live in fsae_params.yaml under
    # the '/zed/zed_node' key and are fed in via ros_params_override_path; the wrapper appends
    # this LAST, so those keys win over its own common_stereo.yaml. To record a rosbag for
    # off-car playback, run this launch alone and `ros2 bag record` the /zed/... topics.
    zed = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('zed_wrapper'), 'launch', 'zed_camera.launch.py')),
        launch_arguments={
            'camera_model': 'zed2i',
            'ros_params_override_path': config,
        }.items(),
    )

    # Velodyne VLP-16 driver — reads UDP packets off eno1 and publishes /velodyne_points
    # (frame_id 'velodyne'). Thin include of fsae_lidar's stock-velodyne wrapper; requires
    # the ros-$ROS_DISTRO-velodyne apt packages (see fsae_lidar/package.xml).
    velodyne = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(lidar_launch, 'velodyne_vlp16.launch.py')))

    # Camera-LiDAR fusion — consumes /fsae/perception/cone_detection (cone node, above) and
    # /velodyne_points (driver, above); needs the camera_link -> velodyne TF from
    # description.launch.py. Params from fsae_lidar/params/lidar_fusion.yaml.
    lidar_fusion = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(lidar_launch, 'fsae_lidar_fusion.launch.py')))

    return LaunchDescription([
        zed,
        Node(
            package='fsae_camera',
            executable='cone_detection_node',
            name='cone_detection_node',
            output='screen',
            parameters=[config],
        ),
        velodyne,
        lidar_fusion,
    ])

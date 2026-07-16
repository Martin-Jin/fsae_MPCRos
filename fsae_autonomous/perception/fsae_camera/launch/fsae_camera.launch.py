import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


# Launches ONLY our cone-detection node. The ZED camera itself is driven by the official
# zed_ros2_wrapper node, launched separately and composed with this one at the bringup
# layer (fsae_bringup/launch/perception.launch.py). SVO recording is the wrapper's job
# now, so the old recording_name argument is gone.
def generate_launch_description():
    # Central config (provides engine_path, conf_threshold, topic names etc.). Node name
    # must match the config key ('cone_detection_node' - the node's internal name) for
    # params to load.
    config = os.path.join(get_package_share_directory('fsae_bringup'), 'config', 'fsae_params.yaml')

    camera_node = Node(
        package='fsae_camera',
        executable='cone_detection_node',
        name='cone_detection_node',
        output='screen',
        parameters=[config],
    )

    return LaunchDescription([
        camera_node,
    ])

from launch import LaunchDescription
from launch_ros.actions import Node


# Visualization layer (RViz MarkerArray + TF). Optional - run for monitoring, skip on the
# headless car. These nodes have no tunable params (no config needed).
def generate_launch_description():
    return LaunchDescription([
        Node(package='fsae_visualization', executable='cone_map_viz', name='cone_publisher', output='screen'),
        Node(package='fsae_visualization', executable='path_viz', name='publish_path_planning_msgs', output='screen'),
        Node(package='fsae_visualization', executable='pursuit_viz', name='publish_pure_pursuit_msgs', output='screen'),
        Node(package='fsae_visualization', executable='base_tf', name='static_transform_publisher', output='screen'),
    ])

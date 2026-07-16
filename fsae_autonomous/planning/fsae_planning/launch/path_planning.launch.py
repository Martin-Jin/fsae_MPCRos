import os

from ament_index_python import get_package_prefix
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import OpaqueFunction
from launch.actions.declare_launch_argument import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


# NOTE: interim per-package launcher for testing a single planner in isolation.
# Full system composition is rewritten in fsae_bringup at Stage 3.
def generate_launch_description() -> LaunchDescription:
    package_name = 'fsae_planning'
    package_dir = os.path.join(get_package_prefix(package_name), 'lib', package_name)   # directory of installed node names
    planners = os.listdir(package_dir)  # retrieves installed node names

    launch_descriptions = [
        # launch arguments
        DeclareLaunchArgument(
            'node_name',
            default_value='fasttube',
            description='which node from this package to launch'
        ),
    ]

    nodes = OpaqueFunction(function=get_node, args=[package_name, planners])    # get a list of actions
    launch_descriptions.append(nodes)

    return LaunchDescription(launch_descriptions)

def get_node(context, package_name, planners):
    NODES = []
    node_2_run = LaunchConfiguration('node_name').perform(context)  # get runtime value of argument

    # central config (single source of truth) from fsae_bringup
    config = os.path.join(get_package_share_directory('fsae_bringup'), 'config', 'fsae_params.yaml')

    for node_name in planners:
        if node_name == node_2_run:
            _ = Node(
                package=package_name,
                executable=node_name,
                name=node_name,
                parameters=[config]
            )

            NODES.append(_)

    if len(NODES) == 0:
        raise Exception(f"selected node {node_2_run} does not exist!")

    return NODES

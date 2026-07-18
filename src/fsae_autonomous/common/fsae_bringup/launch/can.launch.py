import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


# CAN / hardware layer: Ackermann->CAN, CAN decode, and AS status.
# Included by every on-car mission. NOTE: CanTalk (the actual CAN bus interface that
# bridges hardware <-> the /fsae/hardware/can_tx and can_rx topics) is now VENDORED as
# candapter_node (fsae_can_bridge.candapter) but left COMMENTED OUT below - it opens the
# CANdapter USB-serial device, so it should only run on the Jetson with the adapter present.
# Uncomment the block at the bottom to enable it on-car. See CANTALK_INTEGRATION.md.
def generate_launch_description():
    config = os.path.join(get_package_share_directory('fsae_bringup'), 'config', 'fsae_params.yaml')
    return LaunchDescription([
        Node(
            package='fsae_can_bridge',
            executable='ack_to_can_node',
            name='ackermann_to_can',
            output='screen',
            parameters=[config],
        ),
        Node(
            package='fsae_can_bridge',
            executable='can_decoder',
            name='can_decoder',
            output='screen',
            parameters=[config],
        ),
        Node(
            package='fsae_can_bridge',
            executable='as_status_node',
            name='autonomous_sys_status',
            output='screen',
            parameters=[config],
        ),
        # CAN hardware bridge (ported from CanTalk). Subscribes /fsae/hardware/can_tx,
        # publishes /fsae/hardware/can_rx. Commented out: it opens the CANdapter serial
        # device, so only enable it on the Jetson with the adapter plugged in.
        # Node(
        #     package='fsae_can_bridge',
        #     executable='candapter_node',
        #     name='candapter_node',
        #     output='screen',
        #     parameters=[config],
        # ),
    ])

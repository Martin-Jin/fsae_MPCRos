import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster


# NOTE (port): the old base_tf node was non-functional - its TransformBroadcaster was
# commented out, so it only published a TransformStamped to a dead 'base_tf' topic, with
# invalid frame names ('global frame' / 'local frame' contain spaces, which TF rejects)
# and an arbitrary (1,0,0) translation. There was no real behaviour to preserve.
#
# Reimplemented as an actual /tf broadcaster publishing a PLACEHOLDER static map->odom
# identity transform to complete the locked TF tree (map -> odom -> base_link; cone_map
# broadcasts map->base_link from the ego pose). TODO: replace with the real static
# transforms (map->odom, and sensor mounts base_link->zed_camera_link / ->lidar_link)
# once the team confirms the frame geometry.
class StaticTransformPublisher(Node):
    def __init__(self):
        super().__init__('static_transform_publisher')
        self.broadcaster = TransformBroadcaster(self)
        self.timer = self.create_timer(1.0, self.publish_transform)

    def publish_transform(self):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'map'
        t.child_frame_id = 'odom'

        # identity placeholder (see class note)
        t.transform.translation.x = 0.0
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.0

        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0

        self.broadcaster.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    node = StaticTransformPublisher()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()

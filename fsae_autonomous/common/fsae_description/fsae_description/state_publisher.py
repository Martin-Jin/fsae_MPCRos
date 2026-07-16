from math import sin, cos, pi
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from geometry_msgs.msg import Quaternion
from sensor_msgs.msg import JointState
from tf2_ros import TransformBroadcaster, TransformStamped


class StatePublisher(Node):
    def __init__(self):
        super().__init__("state_publisher")
        qos_profile = QoSProfile(depth=10)

        # Publishers
        self.broadcaster = TransformBroadcaster(self, qos=qos_profile)

        # Create a timer to run the update loop at 30Hz
        self.timer = self.create_timer(1 / 30.0, self.update_callback)

        self.angle = 0.0
        self.get_logger().info("Go-cart State Publisher Started")

    def update_callback(self):
        now = self.get_clock().now()

        # Update transform from odom -> base_link
        t = TransformStamped()
        t.header.stamp = now.to_msg()
        t.header.frame_id = "odom"
        t.child_frame_id = "base_link"  # Matches your URDF

        t.transform.translation.x = 0.0
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.0

        # Identity rotation. Was `t.transform.rotation = 0.0`, which assigned a
        # float to a Quaternion field and crashed on the first tick. This is a
        # placeholder odom->base_link (car fixed at the odom origin) until real
        # odometry is wired in.
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0

        # Actually broadcast it — the original never called this, so odom->base_link
        # was never published even before the crash.
        self.broadcaster.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)
    node = StatePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

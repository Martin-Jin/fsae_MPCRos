from pyPS4Controller.controller import Controller
import rclpy
from rclpy.node import Node
from ackermann_msgs.msg import AckermannDrive, AckermannDriveStamped
from std_msgs.msg import Header
import numpy as np

# R3 right and left buttons max is 32767 when pressed and -32767 when fully released
# L3/left joystick goes up,down when fully pushed up is -32767 and positive when down
# L3/left joystick goes right and down when fully pushed is 32767 when pushed fully right and negative when fully left
class joystick_teleop(Node):
    def __init__(self):
        # publisher
        super().__init__("joystick_teleop")
        self.get_logger().info("joystick teleoperation node started")

        self.declare_parameters(
            namespace='',
            parameters=[
            ('max_speed', 2.0),
            ('max_angle', 22.0),
            ('use_ds4drv', True),
            ('verbose', False),
            ]
        )

        # get parameter values
        max_speed = self.get_parameter("max_speed").get_parameter_value().double_value
        max_angle = self.get_parameter("max_angle").get_parameter_value().double_value
        use_ds4drv = self.get_parameter("use_ds4drv").get_parameter_value().bool_value
        verbose = self.get_parameter("verbose").get_parameter_value().bool_value
        # now make sure the controller is paired over the Bluetooth and turn on the listener
        joystick = MyController(max_speed = max_speed,
                                min_speed = 0,
                                max_angle = max_angle,
                                min = -32767,
                                max = 32767,
                                speed = 0,
                                previous_value = -32767,
                                previous_value2 = -32767,
                                publisher=self.create_publisher(AckermannDriveStamped, "/fsae/control/cmd_vel", 10),
                                use_ds4drv=use_ds4drv,
                                verbose=verbose,
                                interface="/dev/input/js0",
                                connecting_using_ds4drv=use_ds4drv
                                )
        joystick.listen()

class MyController(Controller):  # create a custom class for your controller and subclass Controller
    """
    If we want to bind an action to the X button on the controller, we need to override its respective methods.

    Some of the buttons have a binary On/Off state. For example the X, Circle, Square, and Triangle buttons.
    When overriding their respective methods there are no args in the function signature.

    Some controls like the L2, L3, R2 and R3 have a variable On state.
    When overriding their respective method, there is a value argument in the function signature
    which indicates the degree of the input.

    You can put any custom code inside the functions bellow. I have put print statements in there just so you
    can copy/paste the code, connect controller, play with the inputs and see the result.

    All of  the functions that you can override are listed in this script.
    """
    def __init__(self, max_speed, min_speed, max_angle, min, max, speed, previous_value, previous_value2,
                publisher, use_ds4drv, verbose, **kwargs):
        Controller.__init__(self, **kwargs)
        self.max_speed = max_speed
        self.min_speed = min_speed
        self.max_angle = max_angle
        self.min = min
        self.max = max
        self.speed = speed
        self.angle = 0
        self.joystick_teleop_pub = publisher
        self.ds4drv = use_ds4drv
        self.verbose = verbose

    def get_ackerman(self):
        args = {
            'steering_angle': float(np.round(self.angle,2)),
            'steering_angle_velocity': 0.0,
            'speed': float(np.round(self.speed,2)),
            'acceleration': 0.0,
            'jerk': 0.0,
        }

        return AckermannDrive(**args)

    def get_ackerman_stamped(self, ackerman_msg):
        args = {"header": Header(stamp=Node("joystick_teleop").get_clock().now().to_msg(),
                                  frame_id="joystick_teleop"),
                "drive": ackerman_msg}

        return AckermannDriveStamped(**args)

    def on_L3_left(self, value):
        """steer left"""
        self.angle = (value/self.max) * self.max_angle
        # publish msg
        msg = self.get_ackerman_stamped(self.get_ackerman())
        self.joystick_teleop_pub.publish(msg)

        if self.verbose: print(f"angle = {self.angle}")

    def on_L3_right(self, value):
        """steer right"""
        self.angle = (value/self.max) * self.max_angle
        # publish msg
        msg = self.get_ackerman_stamped(self.get_ackerman())
        self.joystick_teleop_pub.publish(msg)

        if self.verbose: print(f"angle = {self.angle}")

    def on_L3_at_rest(self):
        """reset steering to 0"""
        self.angle = 0
        # publish msg
        msg = self.get_ackerman_stamped(self.get_ackerman())
        self.joystick_teleop_pub.publish(msg)

        if self.verbose: print(f"angle = {self.angle}")

    def on_R2_press(self, value):
        if not self.ds4drv: return

        """acceleration"""
        self.speed = (value-self.min)/(self.max-self.min) * (self.max_speed-self.min_speed)
        # publish msg
        msg = self.get_ackerman_stamped(self.get_ackerman())
        self.joystick_teleop_pub.publish(msg)

        if self.verbose: print(f"speed = {self.speed}")

    def on_R2_release(self):
        if not self.ds4drv: return

        """acceleration released"""
        self.speed = 0
        # publish msg
        msg = self.get_ackerman_stamped(self.get_ackerman())
        self.joystick_teleop_pub.publish(msg)

        if self.verbose: print(f"speed = {self.speed}")

    def on_L2_press(self, value):
        if not self.ds4drv: return

        """deceleration"""
        self.speed = (-value-self.min)/(self.max-self.min) * (self.speed-self.min_speed)
        # publish msg
        msg = self.get_ackerman_stamped(self.get_ackerman())
        self.joystick_teleop_pub.publish(msg)

        if self.verbose: print(f"speed = {self.speed}")


    ## if ds4drv is False
    """acceleration"""
    def on_R3_up(self, value):
        if self.ds4drv: return

        range = (self.max_speed - self.min_speed)/2
        proportion = 1 - (value/self.min)
        self.speed = proportion * range
        # publish msg
        msg = self.get_ackerman_stamped(self.get_ackerman())
        self.joystick_teleop_pub.publish(msg)

        if self.verbose: print(f"speed = {self.speed}")

    def on_R3_down(self, value):
        if self.ds4drv: return

        range = (self.max_speed - self.min_speed)/2
        proportion = value/self.max
        self.speed = (self.max_speed/2) + (proportion * range)
        # publish msg
        msg = self.get_ackerman_stamped(self.get_ackerman())
        self.joystick_teleop_pub.publish(msg)

        if self.verbose: print(f"speed = {self.speed}")

    """deceleration"""
    def on_R3_left(self, value):
        if self.ds4drv: return

        range = (self.speed - self.min_speed)/2
        proportion = value/self.min
        self.speed = max(0,self.speed - (proportion * range))
        # publish msg
        msg = self.get_ackerman_stamped(self.get_ackerman())
        self.joystick_teleop_pub.publish(msg)

        if self.verbose: print(f"speed = {self.speed}")

    def on_R3_right(self, value):
        if self.ds4drv: return

        range = (self.max_speed - self.min_speed)/2
        proportion = value/self.max
        self.speed = max(0,self.speed - (proportion * range))
        # publish msg
        msg = self.get_ackerman_stamped(self.get_ackerman())
        self.joystick_teleop_pub.publish(msg)

        if self.verbose: print(f"speed = {self.speed}")


def main(args=None):
    rclpy.init(args=args)

    node = joystick_teleop()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()

import rclpy
from rclpy.node import Node

# import all msg types needed
from fsae_interfaces.msg import CANStamped
from sensor_msgs.msg import BatteryState # https://docs.ros2.org/foxy/api/sensor_msgs/msg/BatteryState.html
from ackermann_msgs.msg import AckermannDriveStamped # http://docs.ros.org/en/api/ackermann_msgs/html/msg/AckermannDriveStamped.html


class CANDecoderJNano(Node):
    def __init__(self) -> None:
        super().__init__("can_decoder")

        # CAN IDs and message counts extracted to config (fsae_bringup/config/fsae_params.yaml).
        self.declare_parameters(
            namespace='',
            parameters=[
                ('battery_main_id', 0x6b0),   # current/voltage
                ('battery_cells_id', 0x6b3),  # cell count
                ('battery_temp_id', 0x6b4),   # temperature
                ('drive_speed_id', 0x604),
                ('drive_steer_id', 0x605),
                ('glv_id', 0x602),
                ('battery_msg_count', 4),     # frames to collect before publishing battery state
                ('drive_msg_count', 3),       # frames to collect before publishing drive state
            ]
        )
        self.battery_main_id = self.get_parameter('battery_main_id').get_parameter_value().integer_value
        self.battery_cells_id = self.get_parameter('battery_cells_id').get_parameter_value().integer_value
        self.battery_temp_id = self.get_parameter('battery_temp_id').get_parameter_value().integer_value
        self.drive_speed_id = self.get_parameter('drive_speed_id').get_parameter_value().integer_value
        self.drive_steer_id = self.get_parameter('drive_steer_id').get_parameter_value().integer_value
        self.glv_id = self.get_parameter('glv_id').get_parameter_value().integer_value
        self.battery_msg_count = self.get_parameter('battery_msg_count').get_parameter_value().integer_value
        self.drive_msg_count = self.get_parameter('drive_msg_count').get_parameter_value().integer_value

        self.battery_count = 0
        self.drive_count  = 0

        # subscribe to raw can data from CAN_interface
        self.can_sub = self.create_subscription(
            CANStamped,
            "/fsae/hardware/can_rx",
            self.callback_can_data,
            10
        )

        # publish different status msgs
        self.battery_status_pub = self.create_publisher(BatteryState, "/fsae/hardware/battery_state", 10)
        self.drive_status_pub = self.create_publisher(AckermannDriveStamped, "/fsae/hardware/drive_status", 10)
        # self.steering_status_pub = self.create_publisher()
        self.glv_status_pub = self.create_publisher(BatteryState, "/fsae/hardware/glv_state", 10)
        # self.motor_temp_pub = self.create_publisher(BatteryState, "/fsae/hardware/glv_state", 10)

    def callback_can_data(self, msg: CANStamped):

        # it is assumed that different can msgs are published seperatly
        # however a better design strategy would be for it to be published as an array

        # switch case for different can ids
        # TODO make sure that the can id is accessed correctly
        # TODO make sure high byte + low byte done correctly

        # BATTERY STATUS

        # need to make sure all battery msgs are received before publishing
        if self.battery_count == 0 and (msg.can.id == self.battery_main_id or msg.can.id == self.battery_cells_id or msg.can.id == self.battery_temp_id):
            self.battery_msg = BatteryState()
            self.battery_count += 1

        if self.battery_count != 0:
            if msg.can.id == self.battery_main_id:
                self.battery_msg.present = True
                self.battery_msg.current = float(msg.can.data[0] + msg.can.data[1])
                self.battery_msg.voltage = float(msg.can.data[2] + msg.can.data[3])
                self.battery_count += 1

            if msg.can.id == self.battery_cells_id:
                self.battery_msg.cell_voltage = [float('nan') for _ in range(int(msg.can.data[6]))]
                self.battery_msg.cell_temperature = [float('nan') for _ in range(int(msg.can.data[6]))]
                self.battery_count += 1

            if msg.can.id == self.battery_temp_id:
                self.battery_msg.temperature = float(msg.can.data[2] + msg.can.data[3])
                self.battery_count += 1

        if self.battery_count == self.battery_msg_count:         # dont know which order it gets published
            self.battery_msg.header.stamp = self.get_clock().now().to_msg()         # not sure if this is needed
            self.battery_status_pub.publish(self.battery_msg)
            self.battery_count = 0


        # DRIVE STATUS
        if self.drive_count == 0 and (msg.can.id == self.drive_speed_id or msg.can.id == self.drive_steer_id):
            self.drive_status_msg = AckermannDriveStamped()
            self.drive_count += 1

        if self.drive_count != 0:
            if msg.can.id == self.drive_speed_id:
                self.drive_status_msg.drive.speed = float(msg.can.data[4])     # are we sure it is in binary
                self.drive_count += 1

            if msg.can.id == self.drive_steer_id:
                self.drive_status_msg.drive.steering_angle = float(msg.can.data[0])
                self.drive_count += 1

        if self.drive_count == self.drive_msg_count:
            self.drive_status_msg.header.stamp = self.get_clock().now().to_msg()         # not sure if this is needed
            self.drive_status_pub.publish(self.drive_status_msg)
            self.drive_count = 0

        # GLV STATUS
        if msg.can.id == self.glv_id:
            glv_status_msg = BatteryState()
            glv_status_msg.header.stamp = self.get_clock().now().to_msg()
            glv_status_msg.present = True
            glv_status_msg.percentage = float(msg.can.data[0])      # make sure SOC is stored as percentage 0 - 1.
                                                                    # also do we need this in the battery status
            glv_status_msg.voltage = float(msg.can.data[2] + msg.can.data[1])
            glv_status_msg.current = float(msg.can.data[4] + msg.can.data[3])
            self.glv_status_pub.publish(glv_status_msg)


        # MOTOR STATUS


        # ERROR STATUS

def main(args=None):
    rclpy.init(args=args)

    CAN_decoder = CANDecoderJNano()

    rclpy.spin(CAN_decoder)
    CAN_decoder.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

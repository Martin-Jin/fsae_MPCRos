#!/usr/bin/env python3
# CAN hardware bridge - ported from the old CanTalk submodule
# (github.com/UOA-FSAE/CanTalk, `nightly`). Bridges the physical CAN bus (a CANdapter
# USB-serial adapter) <-> ROS:
#   subscribes /fsae/hardware/can_tx  (outbound frames from ack_to_can)  -> writes to bus
#   publishes  /fsae/hardware/can_rx  (frames read off the bus)          -> can_decoder
#
# Faithful port + light hardening only:
#   - TX/RX split onto the two /fsae/hardware topics (old code used one shared 'can' topic).
#   - serial open wrapped so a missing/wrong device logs and idles instead of crashing.
#   - guarded the empty-serial-read IndexError.
# TODO (unverified, preserved as-was): serial.Serial(port) opens at pyserial's default
#       line speed (9600); confirm the CANdapter's required USB-serial baud on the Jetson.
#       `baud_rate` below sets the CAN bitrate (the Sx command), NOT the serial line speed.
import rclpy
from rclpy.node import Node
import serial
import threading
from std_msgs.msg import Header
from fsae_interfaces.msg import CANStamped
import re


def clean_can_frame(data):
    frames = re.sub(r'[^a-zA-Z0-9]', '', data)
    frames = frames.split('t')
    frames.remove('')
    return frames


def parse_can_frame(frame):
    """Parses a CAN frame and returns a tuple of ID, length, data.

    Args:
      frame: A CAN frame in hex format.

    Returns:
      A tuple of ID, length, data, where data is a list of bytes.
    """
    id = int(frame[:3], 16)
    length = int(frame[3:4], 16)
    data = [int(frame[4 + i:4 + i + 2], 16) if i + 4 < len(frame) else 0 for i in range(8)]

    return id, length, data


def get_baud_rate_command(rate: int):
    command = b'S5'

    if rate == 10:
        command = b'S0'
    elif rate == 20:
        command = b'S1'
    elif rate == 50:
        command = b'S2'
    elif rate == 100:
        command = b'S3'
    elif rate == 125:
        command = b'S4'
    elif rate == 250:
        command = b'S5'
    elif rate == 500:
        command = b'S6'
    elif rate == 800:
        command = b'S7'
    elif rate == 1000:
        command = b'S8'

    return command


class CanDapter(Node):
    def __init__(self):
        super().__init__('candapter_node')

        self.declare_parameters(
            namespace='',
            parameters=[
                ('port', '/dev/ttyUSB0'),
                ('baud_rate', 250),
            ]
        )

        self.port = self.get_parameter('port').get_parameter_value().string_value
        self.baud_rate = self.get_parameter('baud_rate').get_parameter_value().integer_value

        # Light hardening: don't crash the node if the adapter isn't present (off-car / wrong
        # device). Open lazily; if it fails, log and run idle (no hardware link).
        try:
            self.serial_port = serial.Serial(self.port)
        except (serial.SerialException, OSError) as e:
            self.serial_port = None
            self.get_logger().error(
                f'Could not open CAN serial port {self.port}: {e}. '
                f'Node will idle - no hardware CAN link.')

        # TX/RX split (old code used one shared 'can' topic remapped to pub_raw_can):
        self.can_subscription = self.create_subscription(
            CANStamped,
            '/fsae/hardware/can_tx',     # outbound frames from ack_to_can -> write to bus
            self.can_send_callback,
            10
        )

        self.can_publisher = self.create_publisher(
            CANStamped,
            '/fsae/hardware/can_rx',     # frames read off the bus -> can_decoder
            10
        )

        if self.serial_port is not None:
            self.send_command_with_response(b'C')  # restart can dapter

            while not self.send_command_with_response(
                    get_baud_rate_command(self.baud_rate)
            ):
                pass

            while not self.send_command_with_response(b'O'):  # start can dapter
                pass

            self.serial_thread = threading.Thread(target=self.read_serial)
            self.serial_thread.daemon = True
            self.serial_thread.start()

    def can_send_callback(self, msg):
        # No device (hardware absent) -> nothing to write. (The old frame_id self-filter is
        # no longer needed now TX and RX are separate topics.)
        if self.serial_port is None:
            return

        self.send_command(
            f'T{msg.can.id:03X}'
            f'{len(msg.can.data):01X}'
            f'{"".join(["%02X" % byte for byte in msg.can.data])}'
            .encode())

    def read_serial(self):
        while True:
            if self.serial_port.in_waiting > 0:
                data = self.serial_port.read_until(b'\r') \
                    .decode() \
                    .strip()

                try:
                    index_of_t = data.index('t')
                    data = data[index_of_t:]
                except ValueError:
                    pass

                if data and data[0] == 't':
                    cleaned_data_list = clean_can_frame(data)
                    for cleaned_data in cleaned_data_list:
                        try:
                            frame = parse_can_frame(cleaned_data)
                            msg = self.can_frame_to_can_stamped(frame)
                            self.can_publisher.publish(msg)

                        except:
                            self.get_logger().error(f'Message failed to be received: {cleaned_data}')

    def send_command(self, command: bytes):
        if self.serial_port is None or not self.serial_port.is_open:
            return False

        msg = b'\015' + command + b'\015'
        self.serial_port.write(msg)
        return True

    def can_frame_to_can_stamped(self, frame):
        """Converts a CAN frame data to a ROS 2 Humble CANStamped message.

      Args:
        frame: A CAN frame data tuple in the format (id, length, data).

      Returns:
        A ROS 2 Humble CANStamped message.
      """

        can_stamped = CANStamped()
        can_stamped.header.frame_id = 'candapter_node'
        can_stamped.header.stamp = self.get_clock().now().to_msg()
        can_stamped.can.id = frame[0]
        can_stamped.can.data = frame[2]

        return can_stamped

    def send_command_with_response(self, command: bytes):
        # NOTE DO NOT RUN THIS IF YOU HAVE READING THREAD OPEN
        if self.serial_port is None or not self.serial_port.is_open:
            return False

        msg = b'\015' + command + b'\015'
        self.serial_port.write(msg)
        response = self.serial_port.read()

        self.get_logger().info(f'Sent cmd: {command} | Response: {response}')
        return response == b'\x06'


def main(args=None):
    rclpy.init(args=args)
    node = CanDapter()
    rclpy.spin(node)
    node.send_command(b'C')
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

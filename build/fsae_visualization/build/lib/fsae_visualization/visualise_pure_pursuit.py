#!/usr/bin/python3
# Reimplemented from foxglove SceneUpdate to RViz MarkerArray (foxglove dropped).
# All geometry/transform logic is unchanged; only the publish layer differs.
# NOTE (faithful): in the old code the trajectory LINE append was commented out, so only
# the next-destination sphere actually rendered. That disabled state is preserved here.
from geometry_msgs.msg import Point, Quaternion, Pose, Vector3, PoseArray
from visualization_msgs.msg import Marker, MarkerArray
from std_msgs.msg import ColorRGBA
from ackermann_msgs.msg import AckermannDrive
import math

from builtin_interfaces.msg import Time, Duration

import rclpy
from rclpy.node import Node
import numpy as np

LINE_WIDTH_SCALE = 0.05


class pure_pursuit_visualizer(Node):
    def __init__(self):
        super().__init__("publish_pure_pursuit_msgs")
        self.get_logger().info("pure pursuit visulisation node started")

        self.next_destination_marker = None

        self.pubviz = self.create_publisher(MarkerArray, '/fsae/viz/control', 5)
        # selected path
        self.chosen_path = self.create_subscription(AckermannDrive, "/fsae/control/drive_vis", self.show_drive_path, 5)
        self.next_destination = self.create_subscription(Pose, "/fsae/planning/track_point", self.save_pursue_destination, 5)
        self.cone_map_sub = self.create_subscription(Pose, "/fsae/slam/car_position", self.get_transformations, 5)

        self.id = 1

    def show_drive_path(self, msg: AckermannDrive):
        steering_angle = msg.steering_angle
        if steering_angle == 0:
            steering_angle = 1e-9
        steering_radius = 1 / steering_angle
        trajectory_from_steer = self.single_trajectory_generator(steering_radius)
        self.show_chosen_path(trajectory_from_steer)

    def single_trajectory_generator(self, steering_radius):
        # https://dingyan89.medium.com/simple-understanding-of-kinematic-bicycle-model-81cac6420357 is used for
        # bicycle steering
        R = steering_radius
        t_range = np.arange(0, np.pi/2, 0.01);
        trajectory_output = PoseArray();
        if hasattr(self, "position_vector") and hasattr(self, "rotation_matrix_l2g") and hasattr(self, "rotation_matrix_g2l"):
            for individual_t in t_range:
                pose_input = Pose();
                x_pre_trans = np.cos(individual_t) * R - R
                y_pre_trans = abs(np.sin(individual_t) * R)
                post_trans_point = self.apply_transformation(self.position_vector, self.rotation_matrix_l2g, x_pre_trans, y_pre_trans);
                pose_input.position.x = post_trans_point[0][0]
                pose_input.position.y = post_trans_point[1][0]
                trajectory_output.poses.append(pose_input)
        else:
            self.get_logger().info("Warning: Transformation data not acquired, no trajectory produced")
        return trajectory_output

    def apply_transformation(self, position_vector, rotation_matrix, point_x, point_y):
        point = np.array([[point_x], [point_y]])
        transformed_point = np.matmul(rotation_matrix, point) + position_vector
        return transformed_point

    def get_transformations(self, msg: Pose):
        # Update car's current location and update transformation matrix
        self.car_pose = msg
        self.position_vector, self.rotation_matrix_l2g, self.rotation_matrix_g2l = self.convert_to_transformation_matrix(self.car_pose.position.x, self.car_pose.position.y, self.car_pose.orientation.w)

    # Coordinate tranformer
    def convert_to_transformation_matrix(self, x: float, y: float, theta: float) -> (
            np.array, np.array, np.array):
        '''Convert state and list_of_cones input into position vector, rotation matrix (DCM) and the matrix of list of cones

        Args:
            x: x position specified in float
            y: y position specified in float
            theta: theta orientation specified in float
            list_of_cones: np.array (numpy array) for matrix of cone positions in 2 by n matrix (n is number of cones recorded in input))

        Returns:
            position_vector: np.array of position vector of cart
            rotation_matrix: np.array DCM matrix to convert reading from local frame into global frame
            list_of_cones: np.array 2 x n matrix of the list of cones measured in global frame

        Raises:
            None
        '''
        position_vector = np.array([[x], [y]])
        rotation_matrix_l2g = np.array(
            [[math.cos(theta), -math.sin(theta)],
             [math.sin(theta), math.cos(theta)]])  # local coordinate to global coordinate matrix
        rotation_matrix_g2l = np.array(
            [[math.cos(theta), math.sin(theta)],
             [-math.sin(theta), math.cos(theta)]])  # global coordinate to local coordinate matrix

        return position_vector, rotation_matrix_l2g, rotation_matrix_g2l

    def get_track_point_in_local_frame(self, track_point_in_global_frame: Pose):
        if hasattr(self, "position_vector") and hasattr(self, "rotation_matrix_l2g") and hasattr(self, "rotation_matrix_g2l"):
            track_point_in_local_frame = Pose()
            position_input = np.array(
                [[track_point_in_global_frame.position.x], [track_point_in_global_frame.position.y]])
            position_output = np.matmul(self.rotation_matrix_g2l, (position_input - self.position_vector))
            track_point_in_local_frame.position.x = float(position_output[0])
            track_point_in_local_frame.position.y = float(position_output[1])
            return track_point_in_local_frame
        else:
            self.get_logger.info("Warning: Local pose message not transformed to global frame")
            return track_point_in_global_frame

    def get_track_point_in_global_frame(self, track_point_in_local_frame: Pose):
        if hasattr(self, "position_vector") and hasattr(self, "rotation_matrix_l2g") and hasattr(self, "rotation_matrix_g2l"):
            track_point_in_global_frame = Pose()
            position_input = np.array(
                [[track_point_in_local_frame.position.x], [track_point_in_local_frame.position.y]])
            position_output = np.matmul(self.rotation_matrix_l2g, position_input) + self.position_vector
            track_point_in_global_frame.position.x = float(position_output[0])
            track_point_in_global_frame.position.y = float(position_output[1])
            return track_point_in_global_frame
        else:
            self.get_logger.info("Warning: Local pose message not transformed to global frame")
            return track_point_in_local_frame

    # Show pursued path to follow
    def show_chosen_path(self, msg: PoseArray):
        markers = MarkerArray()

        # (faithful) the trajectory line was disabled in the old code - the LinePrimitive
        # was never appended. Kept disabled here:
        # pts = [msg.poses[j].position for j in range(len(msg.poses))]
        # markers.markers.append(self.make_line_marker(self.id, pts,
        #         ColorRGBA(r=0.0, g=1.0, b=0.0, a=1.0), 2.0))

        # next-destination sphere (the only thing the old node actually rendered)
        if self.next_destination_marker is not None:
            self.next_destination_marker.header.stamp = self.get_clock().now().to_msg()
            self.next_destination_marker.id = self.id
            markers.markers.append(self.next_destination_marker)

        self.pubviz.publish(markers)
        #self.get_logger().info("Published msg")

        self.id += 1

    def make_line_marker(self, id, points, color, thickness):
        marker = Marker()
        marker.header.frame_id = "map"
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = "control"
        marker.id = id
        marker.type = Marker.LINE_STRIP
        marker.action = Marker.ADD
        marker.pose = Pose(position=Point(x=0.0, y=0.0, z=0.0),
                           orientation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0))
        marker.scale = Vector3(x=thickness * LINE_WIDTH_SCALE, y=0.0, z=0.0)
        marker.color = color
        marker.points = points
        marker.lifetime = Duration(sec=3, nanosec=0)
        return marker

    def save_pursue_destination(self, msg : Pose):
        marker = Marker()
        marker.header.frame_id = "map"
        marker.ns = "destination"
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD
        marker.pose = msg
        marker.scale = Vector3(x=1.0, y=1.0, z=1.0)
        marker.color = ColorRGBA(r=1.0, g=1.0, b=0.0, a=1.0)  # yellow (was foxglove 255,255,0)
        marker.lifetime = Duration(sec=3, nanosec=0)
        self.next_destination_marker = marker


def main():
    rclpy.init()
    nde = pure_pursuit_visualizer()
    rclpy.spin(nde)
    nde.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()

#!/usr/bin/python3
# Reimplemented from foxglove SceneUpdate/LinePrimitive to RViz MarkerArray (foxglove dropped).
# The trajectory-selection logic and colours are unchanged; only the publish layer differs.
from geometry_msgs.msg import Point, Quaternion, Pose, Vector3, PoseArray
from visualization_msgs.msg import Marker, MarkerArray
from fsae_interfaces.msg import AllTrajectories
from ackermann_msgs.msg import AckermannDrive

from builtin_interfaces.msg import Time, Duration
from std_msgs.msg import Int16, Int32MultiArray, ColorRGBA

import rclpy
from rclpy.node import Node
import numpy as np

# foxglove LinePrimitive thickness was screen-pixels (scale_invariant); RViz LINE_STRIP
# scale.x is line width in metres. Scale down so widths are sensible on a real track.
LINE_WIDTH_SCALE = 0.05


class pub_viz(Node):
    def __init__(self):
        super().__init__("publish_path_planning_msgs")
        self.get_logger().info("path planning visulisation node started")

        self.next_destination_vis = []

        self.pubviz = self.create_publisher(MarkerArray, '/fsae/viz/trajectories', 10)
        # sub to all trajectories points and states
        self.create_subscription(AllTrajectories, "/fsae/planning/inbound_trajectories", self.set_inbound_trajectories, 10)
        self.create_subscription(AllTrajectories, "/fsae/planning/trajectories", self.show_paths, 10)
        self.create_subscription(Int16, "/fsae/planning/best_trajectory_index", self.get_chosen_trajectory, 10)

        # The three current planners publish a single chosen path as a PoseArray here, not the
        # multi-trajectory AllTrajectories interface that show_paths() above expects.
        self.create_subscription(PoseArray, "/fsae/planning/selected_trajectory", self.show_centerline, 10)

        # center line publisher
        self.centerline_pub = self.create_publisher(MarkerArray, "/fsae/viz/centerline", 10)

        # NMPC's own predicted trajectory (nmpc_controller.py, gated behind
        # nmpc_publish_prediction_enabled, default off) -- same "republish a
        # raw PoseArray as a line" shape as show_centerline above, just drawn
        # as a LINE_STRIP instead of per-point cubes.
        self.create_subscription(
            PoseArray, "/fsae/viz/nmpc_prediction_raw", self.show_nmpc_prediction, 10)
        self.nmpc_prediction_pub = self.create_publisher(
            MarkerArray, "/fsae/viz/nmpc_prediction", 10)

        self.id = 1


    def get_chosen_trajectory(self, msg: Int16) -> None:
        print(f"chosen idx got={msg.data}")
        self.chosen_trajectory = msg.data

    def set_inbound_trajectories(self, msg: AllTrajectories) -> None:
        self.inbounds = msg

    def show_paths(self, msg: AllTrajectories):
        if hasattr(self,"chosen_trajectory") and hasattr(self, "inbounds"):
            traj_markers = MarkerArray()
            traj_markers.markers.append(self.delete_all_lines())
            paths = msg.trajectories
            paths.append(self.inbounds.trajectories[-1]) # append center line

            for i in range(len(paths)-1):
                # choose color (RViz ColorRGBA is 0-1, not foxglove's 0-255)
                # chosen
                if i == self.chosen_trajectory:
                    # green
                    tcols = ColorRGBA(r=0.0, g=1.0, b=0.0, a=1.0)
                    thickness = 5.0
                # center line
                elif i == len(paths) - 1:
                    # blue
                    # tcols = ColorRGBA(r=0.0, g=0.0, b=1.0, a=1.0)
                    # thickness = 3.0
                    # self.get_logger().info(f"center pts: {len(pths[i].poses)}")
                    break
                # other lines
                else:
                    tcols = ColorRGBA(r=1.0, g=1.0, b=1.0, a=0.8)
                    thickness = 1.0

                # get points
                points = []
                for j in range(len(paths[i].poses)):
                    points.append(paths[i].poses[j].position)

                traj_markers.markers.append(self.make_line_marker(i, points, tcols, thickness))


            # show centerline
            centerline_markers = []
            centerline_markers.append(self.delete_all_markers())
            idt = 0
            for pose in paths[-1].poses:
                centerline_markers.append(self.get_marker_from_pose(idt, pose))
                idt += 1

            self.pubviz.publish(traj_markers)
            self.centerline_pub.publish(MarkerArray(markers=centerline_markers))
            self.get_logger().info("Published msg")

            self.id += 1
            return

        self.get_logger().info("attributes not initialized")
        return

    def show_centerline(self, msg: PoseArray):
        centerline_markers = [self.delete_all_markers()]
        for idt, pose in enumerate(msg.poses):
            pose.orientation.w = 1.0  # planner leaves orientation zeroed; RViz rejects a 0-norm quaternion
            centerline_markers.append(self.get_marker_from_pose(idt, pose))
        self.centerline_pub.publish(MarkerArray(markers=centerline_markers))

    def show_nmpc_prediction(self, msg: PoseArray):
        points = [Point(x=p.position.x, y=p.position.y, z=0.0) for p in msg.poses]
        line = self.make_line_marker(
            0, points, ColorRGBA(r=1.0, g=0.6, b=0.0, a=1.0), thickness=2.0)
        self.nmpc_prediction_pub.publish(MarkerArray(markers=[self.delete_all_lines(), line]))

    def make_line_marker(self, id, points, color, thickness):
        marker = Marker()
        marker.header.frame_id = "map"
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = "trajectories"
        marker.id = id
        marker.type = Marker.LINE_STRIP
        marker.action = Marker.ADD
        marker.pose = Pose(position=Point(x=0.0, y=0.0, z=0.0),
                           orientation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0))
        marker.scale = Vector3(x=thickness * LINE_WIDTH_SCALE, y=0.0, z=0.0)  # LINE_STRIP uses scale.x for width
        marker.color = color
        marker.points = points
        marker.lifetime = Duration(sec=0, nanosec=500000000)
        return marker

    def get_marker_from_pose(self, id, pose):
        marker = Marker()
        marker.header.frame_id = "map"  # Adjust the frame ID as needed
        marker.header.stamp = self.get_clock().now().to_msg()

        marker.ns = "map"
        marker.id = id
        marker.type = Marker.CUBE
        marker.action = Marker.ADD
        marker.pose = pose
        marker.scale = Vector3(x=0.3,y=0.3,z=0.3)
        marker.color = ColorRGBA(r=1.0,g=0.0,b=0.0,a=1.0)
        marker.lifetime.sec = 0

        return marker

    def delete_all_markers(self):
        marker = Marker()
        marker.header.frame_id = "map"  # Adjust the frame ID as needed
        marker.header.stamp = self.get_clock().now().to_msg()

        marker.ns = "map"
        marker.id = -1
        marker.type = Marker.CUBE
        marker.action = Marker.DELETEALL

        marker.pose.position.x = 0.0
        marker.pose.position.y = 0.0
        marker.pose.position.z = 0.0

        marker.pose.orientation.x = 0.0
        marker.pose.orientation.y = 0.0
        marker.pose.orientation.z = 0.0
        marker.pose.orientation.w = 1.0

        marker.scale = Vector3(x=0.3, y=0.3, z=0.3)

        marker.color.r = 1.0
        marker.color.g = 0.0
        marker.color.b = 0.0
        marker.color.a = 1.0  # Alpha (opacity)

        marker.lifetime.sec = 0

        return marker

    def delete_all_lines(self):
        marker = Marker()
        marker.header.frame_id = "map"
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = "trajectories"
        marker.id = -1
        marker.type = Marker.LINE_STRIP
        marker.action = Marker.DELETEALL
        return marker

def main():
    rclpy.init()
    nde = pub_viz()
    rclpy.spin(nde)
    nde.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()

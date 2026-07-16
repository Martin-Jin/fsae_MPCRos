/*
OVERVIEW:
  Entry point for the FSAE cone-detection node. Since the zed_ros2_wrapper migration this
  file is trivial: the official Stereolabs wrapper node owns the camera hardware (launched
  separately — see fsae_bringup/launch/perception.launch.py), and ZedLaunchNode is a pure
  ROS subscriber, so main() just initialises ROS and spins the node.

DEPENDENCIES:
  - rclcpp (ROS 2 C++ client library)
  - zed_launch.hpp (node definition; callbacks implemented in cone_detection/cone_detection.cpp)
*/

#include <rclcpp/rclcpp.hpp>
#include "zed_launch.hpp"

int main(int argc, char * argv[])
{
  /*
  This forces the program to print std::cout messages to your terminal immediately,
  rather than storing them up in a buffer, to not miss an error message.
  */
  setvbuf(stdout, NULL, _IONBF, BUFSIZ);

  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ZedLaunchNode>()); // No camera argument — the wrapper owns the hardware now.
  rclcpp::shutdown();

  return 0;
}

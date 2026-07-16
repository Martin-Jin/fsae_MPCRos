cmake_minimum_required(VERSION 3.8)
project(fsae_slam)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(fsae_interfaces REQUIRED)

# C++ SLAM node - STUB (empty callback). The working implementation is the Python
# node below (scripts/cone_mapper.py). This builds as a runnable no-op skeleton for a
# future production rewrite.
add_executable(cone_landmark_mapper src/cone_landmark_mapper.cpp)
ament_target_dependencies(cone_landmark_mapper rclcpp std_msgs geometry_msgs fsae_interfaces)
install(TARGETS cone_landmark_mapper DESTINATION lib/${PROJECT_NAME})

# Working SLAM node (Python reference). Installed as a runnable executable:
#   ros2 run fsae_slam cone_mapper.py
# Needs the `kdtree` pip package at runtime (not in rosdep).
install(PROGRAMS
  scripts/cone_mapper.py
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
  OPTIONAL
)

ament_package()

cmake_minimum_required(VERSION 3.5)
project(fsae_camera)
set(CMAKE_POLICY_DEFAULT_CMP0072 NEW)

# ROS 2 Humble requires C++17 (rclcpp headers use C++17 features).
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

#############################################
# Dependencies
# NOTE: no ZED SDK — since the zed_ros2_wrapper migration this package only needs
# CUDA + TensorRT (for the YOLO engine) + OpenCV/cv_bridge + ROS. The wrapper node
# (package `zed_wrapper`, exec_depend in package.xml) owns the camera at runtime.
find_package(OpenCV 4 REQUIRED)
find_package(CUDA REQUIRED)
find_package(cv_bridge REQUIRED)

find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(fsae_interfaces REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

###############################################################################
# INCLUDES and LIBS
include_directories(${OpenCV_INCLUDE_DIRS})
include_directories(${CUDA_INCLUDE_DIRS})
include_directories(${cv_bridge_INCLUDE_DIRS})
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

link_directories(${CUDA_LIBRARY_DIRS})
link_directories(${OpenCV_LIBRARY_DIRS})

# cuda
include_directories(/usr/local/cuda/include)
link_directories(/usr/local/cuda/lib64)
# tensorrt
# --- Detect Architecture for TensorRT/CUDA paths ---
if(CMAKE_SYSTEM_PROCESSOR STREQUAL "x86_64")
    # Desktop PC Paths
    include_directories(/usr/include/x86_64-linux-gnu/)
    link_directories(/usr/lib/x86_64-linux-gnu/)
    message(STATUS "Configuring for x86_64 Desktop")
elseif(CMAKE_SYSTEM_PROCESSOR STREQUAL "aarch64")
    # Jetson / ARM Paths
    include_directories(/usr/include/aarch64-linux-gnu/)
    link_directories(/usr/lib/aarch64-linux-gnu/)
    message(STATUS "Configuring for aarch64 Jetson")
endif()

FILE(GLOB_RECURSE SRC_FILES cone_detection/cone_detection.cpp cone_detection/yolo.cpp zed_launch/zed_launch.cpp)
FILE(GLOB_RECURSE HDR_FILES cone_detection/*.h* zed_launch/*.h*)

cuda_add_executable(cone_detection_node ${HDR_FILES} ${SRC_FILES})
add_definitions(-O3 -D_MWAITXINTRIN_H_INCLUDED -Wno-deprecated-declarations)

SET(SPECIAL_OS_LIBS "")
SET(TRT_LIBS nvinfer nvonnxparser)

target_link_libraries(cone_detection_node
                        ${TRT_LIBS}
                        ${SPECIAL_OS_LIBS}
                        ${CUDA_LIBRARIES}
                        ${OpenCV_LIBRARIES}
)

add_executable(cone_subscriber cone_detection/cone_subscriber.cpp)
ament_target_dependencies(cone_subscriber
  rclcpp
  std_msgs
  fsae_interfaces
  geometry_msgs
)

add_executable(localisation_subscriber localisation/localisation_subscriber.cpp)
ament_target_dependencies(localisation_subscriber
  rclcpp
  std_msgs
  fsae_interfaces
  geometry_msgs
)

ament_target_dependencies(cone_detection_node
  rclcpp
  cv_bridge
  OpenCV
  std_msgs
  fsae_interfaces
  geometry_msgs
  sensor_msgs
)

install(TARGETS
  cone_detection_node
  cone_subscriber
  localisation_subscriber
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}/
)

ament_package()

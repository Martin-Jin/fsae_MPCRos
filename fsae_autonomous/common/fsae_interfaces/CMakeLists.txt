cmake_minimum_required(VERSION 3.8)
project(fsae_interfaces)

find_package(ament_cmake REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# Ported from old fsae_interfaces. Detections.msg renamed to ConeDetection.msg.
# Stage 4: pruned 8 unused msgs (AllStates, BoundaryStamped, OccupancyGrid, Pulse,
# and the Cone/ConeMap/ConeMapStamped/ConeStamped family) + srv/CANSendReq, all of
# which had zero live references. Dropping AllStates also removed the ackermann_msgs dep.
set(msg_files
  "msg/AllTrajectories.msg"
  "msg/CAN.msg"
  "msg/CANStamped.msg"
  "msg/ConeDetection.msg"
  "msg/HardwareStates.msg"
  "msg/HardwareStatesStamped.msg"
  "msg/MissionStates.msg"
  "msg/MissionStatesStamped.msg"
  "msg/Track.msg"
)

rosidl_generate_interfaces(${PROJECT_NAME}
  ${msg_files}
  DEPENDENCIES std_msgs geometry_msgs
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()

// generated from rosidl_typesupport_fastrtps_c/resource/idl__rosidl_typesupport_fastrtps_c.h.em
// with input from fsae_interfaces:msg/ConeDetection.idl
// generated code does not contain a copyright notice
#ifndef FSAE_INTERFACES__MSG__DETAIL__CONE_DETECTION__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_
#define FSAE_INTERFACES__MSG__DETAIL__CONE_DETECTION__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_


#include <stddef.h>
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_interface/macros.h"
#include "fsae_interfaces/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "fsae_interfaces/msg/detail/cone_detection__struct.h"
#include "fastcdr/Cdr.h"

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
bool cdr_serialize_fsae_interfaces__msg__ConeDetection(
  const fsae_interfaces__msg__ConeDetection * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
bool cdr_deserialize_fsae_interfaces__msg__ConeDetection(
  eprosima::fastcdr::Cdr &,
  fsae_interfaces__msg__ConeDetection * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
size_t get_serialized_size_fsae_interfaces__msg__ConeDetection(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
size_t max_serialized_size_fsae_interfaces__msg__ConeDetection(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
bool cdr_serialize_key_fsae_interfaces__msg__ConeDetection(
  const fsae_interfaces__msg__ConeDetection * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
size_t get_serialized_size_key_fsae_interfaces__msg__ConeDetection(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
size_t max_serialized_size_key_fsae_interfaces__msg__ConeDetection(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, fsae_interfaces, msg, ConeDetection)();

#ifdef __cplusplus
}
#endif

#endif  // FSAE_INTERFACES__MSG__DETAIL__CONE_DETECTION__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_

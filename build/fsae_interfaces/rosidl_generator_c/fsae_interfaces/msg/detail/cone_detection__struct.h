// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from fsae_interfaces:msg/ConeDetection.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/cone_detection.h"


#ifndef FSAE_INTERFACES__MSG__DETAIL__CONE_DETECTION__STRUCT_H_
#define FSAE_INTERFACES__MSG__DETAIL__CONE_DETECTION__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"
// Member 'car_pose'
#include "geometry_msgs/msg/detail/pose__struct.h"
// Member 'yellow'
// Member 'blue'
// Member 'small_orange'
// Member 'big_orange'
#include "geometry_msgs/msg/detail/point__struct.h"

/// Struct defined in msg/ConeDetection in the package fsae_interfaces.
typedef struct fsae_interfaces__msg__ConeDetection
{
  std_msgs__msg__Header header;
  geometry_msgs__msg__Pose car_pose;
  geometry_msgs__msg__Point__Sequence yellow;
  geometry_msgs__msg__Point__Sequence blue;
  geometry_msgs__msg__Point__Sequence small_orange;
  geometry_msgs__msg__Point__Sequence big_orange;
} fsae_interfaces__msg__ConeDetection;

// Struct for a sequence of fsae_interfaces__msg__ConeDetection.
typedef struct fsae_interfaces__msg__ConeDetection__Sequence
{
  fsae_interfaces__msg__ConeDetection * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} fsae_interfaces__msg__ConeDetection__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // FSAE_INTERFACES__MSG__DETAIL__CONE_DETECTION__STRUCT_H_

// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from fsae_interfaces:msg/AllTrajectories.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/all_trajectories.h"


#ifndef FSAE_INTERFACES__MSG__DETAIL__ALL_TRAJECTORIES__STRUCT_H_
#define FSAE_INTERFACES__MSG__DETAIL__ALL_TRAJECTORIES__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

// Include directives for member types
// Member 'trajectories'
#include "geometry_msgs/msg/detail/pose_array__struct.h"

/// Struct defined in msg/AllTrajectories in the package fsae_interfaces.
typedef struct fsae_interfaces__msg__AllTrajectories
{
  uint16_t id;
  geometry_msgs__msg__PoseArray__Sequence trajectories;
} fsae_interfaces__msg__AllTrajectories;

// Struct for a sequence of fsae_interfaces__msg__AllTrajectories.
typedef struct fsae_interfaces__msg__AllTrajectories__Sequence
{
  fsae_interfaces__msg__AllTrajectories * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} fsae_interfaces__msg__AllTrajectories__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // FSAE_INTERFACES__MSG__DETAIL__ALL_TRAJECTORIES__STRUCT_H_

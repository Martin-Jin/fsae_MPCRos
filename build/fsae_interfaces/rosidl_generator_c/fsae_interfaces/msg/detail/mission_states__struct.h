// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from fsae_interfaces:msg/MissionStates.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/mission_states.h"


#ifndef FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES__STRUCT_H_
#define FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

/// Struct defined in msg/MissionStates in the package fsae_interfaces.
typedef struct fsae_interfaces__msg__MissionStates
{
  uint8_t mission_selected;
  uint8_t mission_finished;
} fsae_interfaces__msg__MissionStates;

// Struct for a sequence of fsae_interfaces__msg__MissionStates.
typedef struct fsae_interfaces__msg__MissionStates__Sequence
{
  fsae_interfaces__msg__MissionStates * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} fsae_interfaces__msg__MissionStates__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES__STRUCT_H_

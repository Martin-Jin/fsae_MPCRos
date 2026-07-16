// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from fsae_interfaces:msg/MissionStatesStamped.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/mission_states_stamped.h"


#ifndef FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES_STAMPED__STRUCT_H_
#define FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES_STAMPED__STRUCT_H_

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
// Member 'mission_states'
#include "fsae_interfaces/msg/detail/mission_states__struct.h"

/// Struct defined in msg/MissionStatesStamped in the package fsae_interfaces.
typedef struct fsae_interfaces__msg__MissionStatesStamped
{
  std_msgs__msg__Header header;
  fsae_interfaces__msg__MissionStates mission_states;
} fsae_interfaces__msg__MissionStatesStamped;

// Struct for a sequence of fsae_interfaces__msg__MissionStatesStamped.
typedef struct fsae_interfaces__msg__MissionStatesStamped__Sequence
{
  fsae_interfaces__msg__MissionStatesStamped * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} fsae_interfaces__msg__MissionStatesStamped__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES_STAMPED__STRUCT_H_

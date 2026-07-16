// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from fsae_interfaces:msg/HardwareStates.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/hardware_states.h"


#ifndef FSAE_INTERFACES__MSG__DETAIL__HARDWARE_STATES__STRUCT_H_
#define FSAE_INTERFACES__MSG__DETAIL__HARDWARE_STATES__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

/// Struct defined in msg/HardwareStates in the package fsae_interfaces.
typedef struct fsae_interfaces__msg__HardwareStates
{
  uint8_t ebs_active;
  uint8_t ts_active;
  uint8_t in_gear;
  uint8_t master_switch_on;
  uint8_t asb_ready;
  uint8_t brakes_engaged;
} fsae_interfaces__msg__HardwareStates;

// Struct for a sequence of fsae_interfaces__msg__HardwareStates.
typedef struct fsae_interfaces__msg__HardwareStates__Sequence
{
  fsae_interfaces__msg__HardwareStates * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} fsae_interfaces__msg__HardwareStates__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // FSAE_INTERFACES__MSG__DETAIL__HARDWARE_STATES__STRUCT_H_

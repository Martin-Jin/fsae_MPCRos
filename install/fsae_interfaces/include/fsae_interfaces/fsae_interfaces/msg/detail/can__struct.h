// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from fsae_interfaces:msg/CAN.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/can.h"


#ifndef FSAE_INTERFACES__MSG__DETAIL__CAN__STRUCT_H_
#define FSAE_INTERFACES__MSG__DETAIL__CAN__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

/// Struct defined in msg/CAN in the package fsae_interfaces.
typedef struct fsae_interfaces__msg__CAN
{
  uint16_t id;
  bool is_rtr;
  uint8_t data[8];
} fsae_interfaces__msg__CAN;

// Struct for a sequence of fsae_interfaces__msg__CAN.
typedef struct fsae_interfaces__msg__CAN__Sequence
{
  fsae_interfaces__msg__CAN * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} fsae_interfaces__msg__CAN__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // FSAE_INTERFACES__MSG__DETAIL__CAN__STRUCT_H_

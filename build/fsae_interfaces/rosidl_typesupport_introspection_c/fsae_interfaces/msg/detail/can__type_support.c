// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from fsae_interfaces:msg/CAN.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "fsae_interfaces/msg/detail/can__rosidl_typesupport_introspection_c.h"
#include "fsae_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "fsae_interfaces/msg/detail/can__functions.h"
#include "fsae_interfaces/msg/detail/can__struct.h"


#ifdef __cplusplus
extern "C"
{
#endif

void fsae_interfaces__msg__CAN__rosidl_typesupport_introspection_c__CAN_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  fsae_interfaces__msg__CAN__init(message_memory);
}

void fsae_interfaces__msg__CAN__rosidl_typesupport_introspection_c__CAN_fini_function(void * message_memory)
{
  fsae_interfaces__msg__CAN__fini(message_memory);
}

size_t fsae_interfaces__msg__CAN__rosidl_typesupport_introspection_c__size_function__CAN__data(
  const void * untyped_member)
{
  (void)untyped_member;
  return 8;
}

const void * fsae_interfaces__msg__CAN__rosidl_typesupport_introspection_c__get_const_function__CAN__data(
  const void * untyped_member, size_t index)
{
  const uint8_t * member =
    (const uint8_t *)(untyped_member);
  return &member[index];
}

void * fsae_interfaces__msg__CAN__rosidl_typesupport_introspection_c__get_function__CAN__data(
  void * untyped_member, size_t index)
{
  uint8_t * member =
    (uint8_t *)(untyped_member);
  return &member[index];
}

void fsae_interfaces__msg__CAN__rosidl_typesupport_introspection_c__fetch_function__CAN__data(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const uint8_t * item =
    ((const uint8_t *)
    fsae_interfaces__msg__CAN__rosidl_typesupport_introspection_c__get_const_function__CAN__data(untyped_member, index));
  uint8_t * value =
    (uint8_t *)(untyped_value);
  *value = *item;
}

void fsae_interfaces__msg__CAN__rosidl_typesupport_introspection_c__assign_function__CAN__data(
  void * untyped_member, size_t index, const void * untyped_value)
{
  uint8_t * item =
    ((uint8_t *)
    fsae_interfaces__msg__CAN__rosidl_typesupport_introspection_c__get_function__CAN__data(untyped_member, index));
  const uint8_t * value =
    (const uint8_t *)(untyped_value);
  *item = *value;
}

static rosidl_typesupport_introspection_c__MessageMember fsae_interfaces__msg__CAN__rosidl_typesupport_introspection_c__CAN_message_member_array[3] = {
  {
    "id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT16,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces__msg__CAN, id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "is_rtr",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces__msg__CAN, is_rtr),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "data",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    true,  // is array
    8,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces__msg__CAN, data),  // bytes offset in struct
    NULL,  // default value
    fsae_interfaces__msg__CAN__rosidl_typesupport_introspection_c__size_function__CAN__data,  // size() function pointer
    fsae_interfaces__msg__CAN__rosidl_typesupport_introspection_c__get_const_function__CAN__data,  // get_const(index) function pointer
    fsae_interfaces__msg__CAN__rosidl_typesupport_introspection_c__get_function__CAN__data,  // get(index) function pointer
    fsae_interfaces__msg__CAN__rosidl_typesupport_introspection_c__fetch_function__CAN__data,  // fetch(index, &value) function pointer
    fsae_interfaces__msg__CAN__rosidl_typesupport_introspection_c__assign_function__CAN__data,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers fsae_interfaces__msg__CAN__rosidl_typesupport_introspection_c__CAN_message_members = {
  "fsae_interfaces__msg",  // message namespace
  "CAN",  // message name
  3,  // number of fields
  sizeof(fsae_interfaces__msg__CAN),
  false,  // has_any_key_member_
  fsae_interfaces__msg__CAN__rosidl_typesupport_introspection_c__CAN_message_member_array,  // message members
  fsae_interfaces__msg__CAN__rosidl_typesupport_introspection_c__CAN_init_function,  // function to initialize message memory (memory has to be allocated)
  fsae_interfaces__msg__CAN__rosidl_typesupport_introspection_c__CAN_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t fsae_interfaces__msg__CAN__rosidl_typesupport_introspection_c__CAN_message_type_support_handle = {
  0,
  &fsae_interfaces__msg__CAN__rosidl_typesupport_introspection_c__CAN_message_members,
  get_message_typesupport_handle_function,
  &fsae_interfaces__msg__CAN__get_type_hash,
  &fsae_interfaces__msg__CAN__get_type_description,
  &fsae_interfaces__msg__CAN__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_fsae_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, fsae_interfaces, msg, CAN)() {
  if (!fsae_interfaces__msg__CAN__rosidl_typesupport_introspection_c__CAN_message_type_support_handle.typesupport_identifier) {
    fsae_interfaces__msg__CAN__rosidl_typesupport_introspection_c__CAN_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &fsae_interfaces__msg__CAN__rosidl_typesupport_introspection_c__CAN_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

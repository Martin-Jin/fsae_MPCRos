// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from fsae_interfaces:msg/HardwareStates.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "fsae_interfaces/msg/detail/hardware_states__rosidl_typesupport_introspection_c.h"
#include "fsae_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "fsae_interfaces/msg/detail/hardware_states__functions.h"
#include "fsae_interfaces/msg/detail/hardware_states__struct.h"


#ifdef __cplusplus
extern "C"
{
#endif

void fsae_interfaces__msg__HardwareStates__rosidl_typesupport_introspection_c__HardwareStates_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  fsae_interfaces__msg__HardwareStates__init(message_memory);
}

void fsae_interfaces__msg__HardwareStates__rosidl_typesupport_introspection_c__HardwareStates_fini_function(void * message_memory)
{
  fsae_interfaces__msg__HardwareStates__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember fsae_interfaces__msg__HardwareStates__rosidl_typesupport_introspection_c__HardwareStates_message_member_array[6] = {
  {
    "ebs_active",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces__msg__HardwareStates, ebs_active),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "ts_active",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces__msg__HardwareStates, ts_active),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "in_gear",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces__msg__HardwareStates, in_gear),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "master_switch_on",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces__msg__HardwareStates, master_switch_on),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "asb_ready",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces__msg__HardwareStates, asb_ready),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "brakes_engaged",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces__msg__HardwareStates, brakes_engaged),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers fsae_interfaces__msg__HardwareStates__rosidl_typesupport_introspection_c__HardwareStates_message_members = {
  "fsae_interfaces__msg",  // message namespace
  "HardwareStates",  // message name
  6,  // number of fields
  sizeof(fsae_interfaces__msg__HardwareStates),
  false,  // has_any_key_member_
  fsae_interfaces__msg__HardwareStates__rosidl_typesupport_introspection_c__HardwareStates_message_member_array,  // message members
  fsae_interfaces__msg__HardwareStates__rosidl_typesupport_introspection_c__HardwareStates_init_function,  // function to initialize message memory (memory has to be allocated)
  fsae_interfaces__msg__HardwareStates__rosidl_typesupport_introspection_c__HardwareStates_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t fsae_interfaces__msg__HardwareStates__rosidl_typesupport_introspection_c__HardwareStates_message_type_support_handle = {
  0,
  &fsae_interfaces__msg__HardwareStates__rosidl_typesupport_introspection_c__HardwareStates_message_members,
  get_message_typesupport_handle_function,
  &fsae_interfaces__msg__HardwareStates__get_type_hash,
  &fsae_interfaces__msg__HardwareStates__get_type_description,
  &fsae_interfaces__msg__HardwareStates__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_fsae_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, fsae_interfaces, msg, HardwareStates)() {
  if (!fsae_interfaces__msg__HardwareStates__rosidl_typesupport_introspection_c__HardwareStates_message_type_support_handle.typesupport_identifier) {
    fsae_interfaces__msg__HardwareStates__rosidl_typesupport_introspection_c__HardwareStates_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &fsae_interfaces__msg__HardwareStates__rosidl_typesupport_introspection_c__HardwareStates_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

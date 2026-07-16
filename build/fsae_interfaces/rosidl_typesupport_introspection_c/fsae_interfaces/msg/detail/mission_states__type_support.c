// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from fsae_interfaces:msg/MissionStates.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "fsae_interfaces/msg/detail/mission_states__rosidl_typesupport_introspection_c.h"
#include "fsae_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "fsae_interfaces/msg/detail/mission_states__functions.h"
#include "fsae_interfaces/msg/detail/mission_states__struct.h"


#ifdef __cplusplus
extern "C"
{
#endif

void fsae_interfaces__msg__MissionStates__rosidl_typesupport_introspection_c__MissionStates_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  fsae_interfaces__msg__MissionStates__init(message_memory);
}

void fsae_interfaces__msg__MissionStates__rosidl_typesupport_introspection_c__MissionStates_fini_function(void * message_memory)
{
  fsae_interfaces__msg__MissionStates__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember fsae_interfaces__msg__MissionStates__rosidl_typesupport_introspection_c__MissionStates_message_member_array[2] = {
  {
    "mission_selected",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces__msg__MissionStates, mission_selected),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "mission_finished",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces__msg__MissionStates, mission_finished),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers fsae_interfaces__msg__MissionStates__rosidl_typesupport_introspection_c__MissionStates_message_members = {
  "fsae_interfaces__msg",  // message namespace
  "MissionStates",  // message name
  2,  // number of fields
  sizeof(fsae_interfaces__msg__MissionStates),
  false,  // has_any_key_member_
  fsae_interfaces__msg__MissionStates__rosidl_typesupport_introspection_c__MissionStates_message_member_array,  // message members
  fsae_interfaces__msg__MissionStates__rosidl_typesupport_introspection_c__MissionStates_init_function,  // function to initialize message memory (memory has to be allocated)
  fsae_interfaces__msg__MissionStates__rosidl_typesupport_introspection_c__MissionStates_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t fsae_interfaces__msg__MissionStates__rosidl_typesupport_introspection_c__MissionStates_message_type_support_handle = {
  0,
  &fsae_interfaces__msg__MissionStates__rosidl_typesupport_introspection_c__MissionStates_message_members,
  get_message_typesupport_handle_function,
  &fsae_interfaces__msg__MissionStates__get_type_hash,
  &fsae_interfaces__msg__MissionStates__get_type_description,
  &fsae_interfaces__msg__MissionStates__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_fsae_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, fsae_interfaces, msg, MissionStates)() {
  if (!fsae_interfaces__msg__MissionStates__rosidl_typesupport_introspection_c__MissionStates_message_type_support_handle.typesupport_identifier) {
    fsae_interfaces__msg__MissionStates__rosidl_typesupport_introspection_c__MissionStates_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &fsae_interfaces__msg__MissionStates__rosidl_typesupport_introspection_c__MissionStates_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

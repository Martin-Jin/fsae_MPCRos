// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from fsae_interfaces:msg/HardwareStatesStamped.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "fsae_interfaces/msg/detail/hardware_states_stamped__rosidl_typesupport_introspection_c.h"
#include "fsae_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "fsae_interfaces/msg/detail/hardware_states_stamped__functions.h"
#include "fsae_interfaces/msg/detail/hardware_states_stamped__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"
// Member `hardware_states`
#include "fsae_interfaces/msg/hardware_states.h"
// Member `hardware_states`
#include "fsae_interfaces/msg/detail/hardware_states__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void fsae_interfaces__msg__HardwareStatesStamped__rosidl_typesupport_introspection_c__HardwareStatesStamped_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  fsae_interfaces__msg__HardwareStatesStamped__init(message_memory);
}

void fsae_interfaces__msg__HardwareStatesStamped__rosidl_typesupport_introspection_c__HardwareStatesStamped_fini_function(void * message_memory)
{
  fsae_interfaces__msg__HardwareStatesStamped__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember fsae_interfaces__msg__HardwareStatesStamped__rosidl_typesupport_introspection_c__HardwareStatesStamped_message_member_array[2] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces__msg__HardwareStatesStamped, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "hardware_states",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces__msg__HardwareStatesStamped, hardware_states),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers fsae_interfaces__msg__HardwareStatesStamped__rosidl_typesupport_introspection_c__HardwareStatesStamped_message_members = {
  "fsae_interfaces__msg",  // message namespace
  "HardwareStatesStamped",  // message name
  2,  // number of fields
  sizeof(fsae_interfaces__msg__HardwareStatesStamped),
  false,  // has_any_key_member_
  fsae_interfaces__msg__HardwareStatesStamped__rosidl_typesupport_introspection_c__HardwareStatesStamped_message_member_array,  // message members
  fsae_interfaces__msg__HardwareStatesStamped__rosidl_typesupport_introspection_c__HardwareStatesStamped_init_function,  // function to initialize message memory (memory has to be allocated)
  fsae_interfaces__msg__HardwareStatesStamped__rosidl_typesupport_introspection_c__HardwareStatesStamped_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t fsae_interfaces__msg__HardwareStatesStamped__rosidl_typesupport_introspection_c__HardwareStatesStamped_message_type_support_handle = {
  0,
  &fsae_interfaces__msg__HardwareStatesStamped__rosidl_typesupport_introspection_c__HardwareStatesStamped_message_members,
  get_message_typesupport_handle_function,
  &fsae_interfaces__msg__HardwareStatesStamped__get_type_hash,
  &fsae_interfaces__msg__HardwareStatesStamped__get_type_description,
  &fsae_interfaces__msg__HardwareStatesStamped__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_fsae_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, fsae_interfaces, msg, HardwareStatesStamped)() {
  fsae_interfaces__msg__HardwareStatesStamped__rosidl_typesupport_introspection_c__HardwareStatesStamped_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  fsae_interfaces__msg__HardwareStatesStamped__rosidl_typesupport_introspection_c__HardwareStatesStamped_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, fsae_interfaces, msg, HardwareStates)();
  if (!fsae_interfaces__msg__HardwareStatesStamped__rosidl_typesupport_introspection_c__HardwareStatesStamped_message_type_support_handle.typesupport_identifier) {
    fsae_interfaces__msg__HardwareStatesStamped__rosidl_typesupport_introspection_c__HardwareStatesStamped_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &fsae_interfaces__msg__HardwareStatesStamped__rosidl_typesupport_introspection_c__HardwareStatesStamped_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

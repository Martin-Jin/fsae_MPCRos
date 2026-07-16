// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from fsae_interfaces:msg/MissionStatesStamped.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "fsae_interfaces/msg/detail/mission_states_stamped__functions.h"
#include "fsae_interfaces/msg/detail/mission_states_stamped__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace fsae_interfaces
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void MissionStatesStamped_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) fsae_interfaces::msg::MissionStatesStamped(_init);
}

void MissionStatesStamped_fini_function(void * message_memory)
{
  auto typed_message = static_cast<fsae_interfaces::msg::MissionStatesStamped *>(message_memory);
  typed_message->~MissionStatesStamped();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember MissionStatesStamped_message_member_array[2] = {
  {
    "header",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<std_msgs::msg::Header>(),  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces::msg::MissionStatesStamped, header),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "mission_states",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<fsae_interfaces::msg::MissionStates>(),  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces::msg::MissionStatesStamped, mission_states),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers MissionStatesStamped_message_members = {
  "fsae_interfaces::msg",  // message namespace
  "MissionStatesStamped",  // message name
  2,  // number of fields
  sizeof(fsae_interfaces::msg::MissionStatesStamped),
  false,  // has_any_key_member_
  MissionStatesStamped_message_member_array,  // message members
  MissionStatesStamped_init_function,  // function to initialize message memory (memory has to be allocated)
  MissionStatesStamped_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t MissionStatesStamped_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &MissionStatesStamped_message_members,
  get_message_typesupport_handle_function,
  &fsae_interfaces__msg__MissionStatesStamped__get_type_hash,
  &fsae_interfaces__msg__MissionStatesStamped__get_type_description,
  &fsae_interfaces__msg__MissionStatesStamped__get_type_description_sources,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace fsae_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<fsae_interfaces::msg::MissionStatesStamped>()
{
  return &::fsae_interfaces::msg::rosidl_typesupport_introspection_cpp::MissionStatesStamped_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, fsae_interfaces, msg, MissionStatesStamped)() {
  return &::fsae_interfaces::msg::rosidl_typesupport_introspection_cpp::MissionStatesStamped_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

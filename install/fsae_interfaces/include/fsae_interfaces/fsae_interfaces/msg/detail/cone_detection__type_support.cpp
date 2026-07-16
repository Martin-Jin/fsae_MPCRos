// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from fsae_interfaces:msg/ConeDetection.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "fsae_interfaces/msg/detail/cone_detection__functions.h"
#include "fsae_interfaces/msg/detail/cone_detection__struct.hpp"
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

void ConeDetection_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) fsae_interfaces::msg::ConeDetection(_init);
}

void ConeDetection_fini_function(void * message_memory)
{
  auto typed_message = static_cast<fsae_interfaces::msg::ConeDetection *>(message_memory);
  typed_message->~ConeDetection();
}

size_t size_function__ConeDetection__yellow(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<geometry_msgs::msg::Point> *>(untyped_member);
  return member->size();
}

const void * get_const_function__ConeDetection__yellow(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<geometry_msgs::msg::Point> *>(untyped_member);
  return &member[index];
}

void * get_function__ConeDetection__yellow(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<geometry_msgs::msg::Point> *>(untyped_member);
  return &member[index];
}

void fetch_function__ConeDetection__yellow(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const geometry_msgs::msg::Point *>(
    get_const_function__ConeDetection__yellow(untyped_member, index));
  auto & value = *reinterpret_cast<geometry_msgs::msg::Point *>(untyped_value);
  value = item;
}

void assign_function__ConeDetection__yellow(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<geometry_msgs::msg::Point *>(
    get_function__ConeDetection__yellow(untyped_member, index));
  const auto & value = *reinterpret_cast<const geometry_msgs::msg::Point *>(untyped_value);
  item = value;
}

void resize_function__ConeDetection__yellow(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<geometry_msgs::msg::Point> *>(untyped_member);
  member->resize(size);
}

size_t size_function__ConeDetection__blue(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<geometry_msgs::msg::Point> *>(untyped_member);
  return member->size();
}

const void * get_const_function__ConeDetection__blue(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<geometry_msgs::msg::Point> *>(untyped_member);
  return &member[index];
}

void * get_function__ConeDetection__blue(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<geometry_msgs::msg::Point> *>(untyped_member);
  return &member[index];
}

void fetch_function__ConeDetection__blue(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const geometry_msgs::msg::Point *>(
    get_const_function__ConeDetection__blue(untyped_member, index));
  auto & value = *reinterpret_cast<geometry_msgs::msg::Point *>(untyped_value);
  value = item;
}

void assign_function__ConeDetection__blue(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<geometry_msgs::msg::Point *>(
    get_function__ConeDetection__blue(untyped_member, index));
  const auto & value = *reinterpret_cast<const geometry_msgs::msg::Point *>(untyped_value);
  item = value;
}

void resize_function__ConeDetection__blue(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<geometry_msgs::msg::Point> *>(untyped_member);
  member->resize(size);
}

size_t size_function__ConeDetection__small_orange(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<geometry_msgs::msg::Point> *>(untyped_member);
  return member->size();
}

const void * get_const_function__ConeDetection__small_orange(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<geometry_msgs::msg::Point> *>(untyped_member);
  return &member[index];
}

void * get_function__ConeDetection__small_orange(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<geometry_msgs::msg::Point> *>(untyped_member);
  return &member[index];
}

void fetch_function__ConeDetection__small_orange(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const geometry_msgs::msg::Point *>(
    get_const_function__ConeDetection__small_orange(untyped_member, index));
  auto & value = *reinterpret_cast<geometry_msgs::msg::Point *>(untyped_value);
  value = item;
}

void assign_function__ConeDetection__small_orange(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<geometry_msgs::msg::Point *>(
    get_function__ConeDetection__small_orange(untyped_member, index));
  const auto & value = *reinterpret_cast<const geometry_msgs::msg::Point *>(untyped_value);
  item = value;
}

void resize_function__ConeDetection__small_orange(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<geometry_msgs::msg::Point> *>(untyped_member);
  member->resize(size);
}

size_t size_function__ConeDetection__big_orange(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<geometry_msgs::msg::Point> *>(untyped_member);
  return member->size();
}

const void * get_const_function__ConeDetection__big_orange(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<geometry_msgs::msg::Point> *>(untyped_member);
  return &member[index];
}

void * get_function__ConeDetection__big_orange(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<geometry_msgs::msg::Point> *>(untyped_member);
  return &member[index];
}

void fetch_function__ConeDetection__big_orange(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const geometry_msgs::msg::Point *>(
    get_const_function__ConeDetection__big_orange(untyped_member, index));
  auto & value = *reinterpret_cast<geometry_msgs::msg::Point *>(untyped_value);
  value = item;
}

void assign_function__ConeDetection__big_orange(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<geometry_msgs::msg::Point *>(
    get_function__ConeDetection__big_orange(untyped_member, index));
  const auto & value = *reinterpret_cast<const geometry_msgs::msg::Point *>(untyped_value);
  item = value;
}

void resize_function__ConeDetection__big_orange(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<geometry_msgs::msg::Point> *>(untyped_member);
  member->resize(size);
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember ConeDetection_message_member_array[6] = {
  {
    "header",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<std_msgs::msg::Header>(),  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces::msg::ConeDetection, header),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "car_pose",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<geometry_msgs::msg::Pose>(),  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces::msg::ConeDetection, car_pose),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "yellow",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<geometry_msgs::msg::Point>(),  // members of sub message
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces::msg::ConeDetection, yellow),  // bytes offset in struct
    nullptr,  // default value
    size_function__ConeDetection__yellow,  // size() function pointer
    get_const_function__ConeDetection__yellow,  // get_const(index) function pointer
    get_function__ConeDetection__yellow,  // get(index) function pointer
    fetch_function__ConeDetection__yellow,  // fetch(index, &value) function pointer
    assign_function__ConeDetection__yellow,  // assign(index, value) function pointer
    resize_function__ConeDetection__yellow  // resize(index) function pointer
  },
  {
    "blue",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<geometry_msgs::msg::Point>(),  // members of sub message
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces::msg::ConeDetection, blue),  // bytes offset in struct
    nullptr,  // default value
    size_function__ConeDetection__blue,  // size() function pointer
    get_const_function__ConeDetection__blue,  // get_const(index) function pointer
    get_function__ConeDetection__blue,  // get(index) function pointer
    fetch_function__ConeDetection__blue,  // fetch(index, &value) function pointer
    assign_function__ConeDetection__blue,  // assign(index, value) function pointer
    resize_function__ConeDetection__blue  // resize(index) function pointer
  },
  {
    "small_orange",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<geometry_msgs::msg::Point>(),  // members of sub message
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces::msg::ConeDetection, small_orange),  // bytes offset in struct
    nullptr,  // default value
    size_function__ConeDetection__small_orange,  // size() function pointer
    get_const_function__ConeDetection__small_orange,  // get_const(index) function pointer
    get_function__ConeDetection__small_orange,  // get(index) function pointer
    fetch_function__ConeDetection__small_orange,  // fetch(index, &value) function pointer
    assign_function__ConeDetection__small_orange,  // assign(index, value) function pointer
    resize_function__ConeDetection__small_orange  // resize(index) function pointer
  },
  {
    "big_orange",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<geometry_msgs::msg::Point>(),  // members of sub message
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces::msg::ConeDetection, big_orange),  // bytes offset in struct
    nullptr,  // default value
    size_function__ConeDetection__big_orange,  // size() function pointer
    get_const_function__ConeDetection__big_orange,  // get_const(index) function pointer
    get_function__ConeDetection__big_orange,  // get(index) function pointer
    fetch_function__ConeDetection__big_orange,  // fetch(index, &value) function pointer
    assign_function__ConeDetection__big_orange,  // assign(index, value) function pointer
    resize_function__ConeDetection__big_orange  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers ConeDetection_message_members = {
  "fsae_interfaces::msg",  // message namespace
  "ConeDetection",  // message name
  6,  // number of fields
  sizeof(fsae_interfaces::msg::ConeDetection),
  false,  // has_any_key_member_
  ConeDetection_message_member_array,  // message members
  ConeDetection_init_function,  // function to initialize message memory (memory has to be allocated)
  ConeDetection_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t ConeDetection_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &ConeDetection_message_members,
  get_message_typesupport_handle_function,
  &fsae_interfaces__msg__ConeDetection__get_type_hash,
  &fsae_interfaces__msg__ConeDetection__get_type_description,
  &fsae_interfaces__msg__ConeDetection__get_type_description_sources,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace fsae_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<fsae_interfaces::msg::ConeDetection>()
{
  return &::fsae_interfaces::msg::rosidl_typesupport_introspection_cpp::ConeDetection_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, fsae_interfaces, msg, ConeDetection)() {
  return &::fsae_interfaces::msg::rosidl_typesupport_introspection_cpp::ConeDetection_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

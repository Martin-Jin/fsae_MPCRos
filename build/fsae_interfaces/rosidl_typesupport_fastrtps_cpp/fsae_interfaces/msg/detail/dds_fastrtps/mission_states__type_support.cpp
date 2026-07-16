// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__type_support.cpp.em
// with input from fsae_interfaces:msg/MissionStates.idl
// generated code does not contain a copyright notice
#include "fsae_interfaces/msg/detail/mission_states__rosidl_typesupport_fastrtps_cpp.hpp"
#include "fsae_interfaces/msg/detail/mission_states__functions.h"
#include "fsae_interfaces/msg/detail/mission_states__struct.hpp"

#include <cstddef>
#include <limits>
#include <stdexcept>
#include <string>
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_fastrtps_cpp/identifier.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_fastrtps_cpp/serialization_helpers.hpp"
#include "rosidl_typesupport_fastrtps_cpp/wstring_conversion.hpp"
#include "fastcdr/Cdr.h"


// forward declaration of message dependencies and their conversion functions

namespace fsae_interfaces
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{


bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_fsae_interfaces
cdr_serialize(
  const fsae_interfaces::msg::MissionStates & ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Member: mission_selected
  cdr << ros_message.mission_selected;

  // Member: mission_finished
  cdr << ros_message.mission_finished;

  return true;
}

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_fsae_interfaces
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  fsae_interfaces::msg::MissionStates & ros_message)
{
  // Member: mission_selected
  cdr >> ros_message.mission_selected;

  // Member: mission_finished
  cdr >> ros_message.mission_finished;

  return true;
}  // NOLINT(readability/fn_size)


size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_fsae_interfaces
get_serialized_size(
  const fsae_interfaces::msg::MissionStates & ros_message,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Member: mission_selected
  {
    size_t item_size = sizeof(ros_message.mission_selected);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: mission_finished
  {
    size_t item_size = sizeof(ros_message.mission_finished);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}


size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_fsae_interfaces
max_serialized_size_MissionStates(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;

  // Member: mission_selected
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // Member: mission_finished
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = fsae_interfaces::msg::MissionStates;
    is_plain =
      (
      offsetof(DataType, mission_finished) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_fsae_interfaces
cdr_serialize_key(
  const fsae_interfaces::msg::MissionStates & ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Member: mission_selected
  cdr << ros_message.mission_selected;

  // Member: mission_finished
  cdr << ros_message.mission_finished;

  return true;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_fsae_interfaces
get_serialized_size_key(
  const fsae_interfaces::msg::MissionStates & ros_message,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Member: mission_selected
  {
    size_t item_size = sizeof(ros_message.mission_selected);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: mission_finished
  {
    size_t item_size = sizeof(ros_message.mission_finished);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_fsae_interfaces
max_serialized_size_key_MissionStates(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;

  // Member: mission_selected
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: mission_finished
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = fsae_interfaces::msg::MissionStates;
    is_plain =
      (
      offsetof(DataType, mission_finished) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}


static bool _MissionStates__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  auto typed_message =
    static_cast<const fsae_interfaces::msg::MissionStates *>(
    untyped_ros_message);
  return cdr_serialize(*typed_message, cdr);
}

static bool _MissionStates__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  auto typed_message =
    static_cast<fsae_interfaces::msg::MissionStates *>(
    untyped_ros_message);
  return cdr_deserialize(cdr, *typed_message);
}

static uint32_t _MissionStates__get_serialized_size(
  const void * untyped_ros_message)
{
  auto typed_message =
    static_cast<const fsae_interfaces::msg::MissionStates *>(
    untyped_ros_message);
  return static_cast<uint32_t>(get_serialized_size(*typed_message, 0));
}

static size_t _MissionStates__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_MissionStates(full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}

static message_type_support_callbacks_t _MissionStates__callbacks = {
  "fsae_interfaces::msg",
  "MissionStates",
  _MissionStates__cdr_serialize,
  _MissionStates__cdr_deserialize,
  _MissionStates__get_serialized_size,
  _MissionStates__max_serialized_size,
  nullptr
};

static rosidl_message_type_support_t _MissionStates__handle = {
  rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
  &_MissionStates__callbacks,
  get_message_typesupport_handle_function,
  &fsae_interfaces__msg__MissionStates__get_type_hash,
  &fsae_interfaces__msg__MissionStates__get_type_description,
  &fsae_interfaces__msg__MissionStates__get_type_description_sources,
};

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace fsae_interfaces

namespace rosidl_typesupport_fastrtps_cpp
{

template<>
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_EXPORT_fsae_interfaces
const rosidl_message_type_support_t *
get_message_type_support_handle<fsae_interfaces::msg::MissionStates>()
{
  return &fsae_interfaces::msg::typesupport_fastrtps_cpp::_MissionStates__handle;
}

}  // namespace rosidl_typesupport_fastrtps_cpp

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, fsae_interfaces, msg, MissionStates)() {
  return &fsae_interfaces::msg::typesupport_fastrtps_cpp::_MissionStates__handle;
}

#ifdef __cplusplus
}
#endif

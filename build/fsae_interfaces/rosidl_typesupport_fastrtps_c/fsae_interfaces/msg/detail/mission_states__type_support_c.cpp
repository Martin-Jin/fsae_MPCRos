// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from fsae_interfaces:msg/MissionStates.idl
// generated code does not contain a copyright notice
#include "fsae_interfaces/msg/detail/mission_states__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <cstddef>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/serialization_helpers.hpp"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "fsae_interfaces/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "fsae_interfaces/msg/detail/mission_states__struct.h"
#include "fsae_interfaces/msg/detail/mission_states__functions.h"
#include "fastcdr/Cdr.h"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

// includes and forward declarations of message dependencies and their conversion functions

#if defined(__cplusplus)
extern "C"
{
#endif


// forward declare type support functions


using _MissionStates__ros_msg_type = fsae_interfaces__msg__MissionStates;


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
bool cdr_serialize_fsae_interfaces__msg__MissionStates(
  const fsae_interfaces__msg__MissionStates * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: mission_selected
  {
    cdr << ros_message->mission_selected;
  }

  // Field name: mission_finished
  {
    cdr << ros_message->mission_finished;
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
bool cdr_deserialize_fsae_interfaces__msg__MissionStates(
  eprosima::fastcdr::Cdr & cdr,
  fsae_interfaces__msg__MissionStates * ros_message)
{
  // Field name: mission_selected
  {
    cdr >> ros_message->mission_selected;
  }

  // Field name: mission_finished
  {
    cdr >> ros_message->mission_finished;
  }

  return true;
}  // NOLINT(readability/fn_size)


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
size_t get_serialized_size_fsae_interfaces__msg__MissionStates(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _MissionStates__ros_msg_type * ros_message = static_cast<const _MissionStates__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: mission_selected
  {
    size_t item_size = sizeof(ros_message->mission_selected);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: mission_finished
  {
    size_t item_size = sizeof(ros_message->mission_finished);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
size_t max_serialized_size_fsae_interfaces__msg__MissionStates(
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

  // Field name: mission_selected
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: mission_finished
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
    using DataType = fsae_interfaces__msg__MissionStates;
    is_plain =
      (
      offsetof(DataType, mission_finished) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
bool cdr_serialize_key_fsae_interfaces__msg__MissionStates(
  const fsae_interfaces__msg__MissionStates * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: mission_selected
  {
    cdr << ros_message->mission_selected;
  }

  // Field name: mission_finished
  {
    cdr << ros_message->mission_finished;
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
size_t get_serialized_size_key_fsae_interfaces__msg__MissionStates(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _MissionStates__ros_msg_type * ros_message = static_cast<const _MissionStates__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;

  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: mission_selected
  {
    size_t item_size = sizeof(ros_message->mission_selected);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: mission_finished
  {
    size_t item_size = sizeof(ros_message->mission_finished);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
size_t max_serialized_size_key_fsae_interfaces__msg__MissionStates(
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
  // Field name: mission_selected
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: mission_finished
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
    using DataType = fsae_interfaces__msg__MissionStates;
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
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const fsae_interfaces__msg__MissionStates * ros_message = static_cast<const fsae_interfaces__msg__MissionStates *>(untyped_ros_message);
  (void)ros_message;
  return cdr_serialize_fsae_interfaces__msg__MissionStates(ros_message, cdr);
}

static bool _MissionStates__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  fsae_interfaces__msg__MissionStates * ros_message = static_cast<fsae_interfaces__msg__MissionStates *>(untyped_ros_message);
  (void)ros_message;
  return cdr_deserialize_fsae_interfaces__msg__MissionStates(cdr, ros_message);
}

static uint32_t _MissionStates__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_fsae_interfaces__msg__MissionStates(
      untyped_ros_message, 0));
}

static size_t _MissionStates__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_fsae_interfaces__msg__MissionStates(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_MissionStates = {
  "fsae_interfaces::msg",
  "MissionStates",
  _MissionStates__cdr_serialize,
  _MissionStates__cdr_deserialize,
  _MissionStates__get_serialized_size,
  _MissionStates__max_serialized_size,
  nullptr
};

static rosidl_message_type_support_t _MissionStates__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_MissionStates,
  get_message_typesupport_handle_function,
  &fsae_interfaces__msg__MissionStates__get_type_hash,
  &fsae_interfaces__msg__MissionStates__get_type_description,
  &fsae_interfaces__msg__MissionStates__get_type_description_sources,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, fsae_interfaces, msg, MissionStates)() {
  return &_MissionStates__type_support;
}

#if defined(__cplusplus)
}
#endif

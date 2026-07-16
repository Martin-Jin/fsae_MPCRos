// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from fsae_interfaces:msg/CANStamped.idl
// generated code does not contain a copyright notice
#include "fsae_interfaces/msg/detail/can_stamped__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <cstddef>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/serialization_helpers.hpp"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "fsae_interfaces/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "fsae_interfaces/msg/detail/can_stamped__struct.h"
#include "fsae_interfaces/msg/detail/can_stamped__functions.h"
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

#include "fsae_interfaces/msg/detail/can__functions.h"  // can
#include "std_msgs/msg/detail/header__functions.h"  // header

// forward declare type support functions

bool cdr_serialize_fsae_interfaces__msg__CAN(
  const fsae_interfaces__msg__CAN * ros_message,
  eprosima::fastcdr::Cdr & cdr);

bool cdr_deserialize_fsae_interfaces__msg__CAN(
  eprosima::fastcdr::Cdr & cdr,
  fsae_interfaces__msg__CAN * ros_message);

size_t get_serialized_size_fsae_interfaces__msg__CAN(
  const void * untyped_ros_message,
  size_t current_alignment);

size_t max_serialized_size_fsae_interfaces__msg__CAN(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

bool cdr_serialize_key_fsae_interfaces__msg__CAN(
  const fsae_interfaces__msg__CAN * ros_message,
  eprosima::fastcdr::Cdr & cdr);

size_t get_serialized_size_key_fsae_interfaces__msg__CAN(
  const void * untyped_ros_message,
  size_t current_alignment);

size_t max_serialized_size_key_fsae_interfaces__msg__CAN(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, fsae_interfaces, msg, CAN)();

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_fsae_interfaces
bool cdr_serialize_std_msgs__msg__Header(
  const std_msgs__msg__Header * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_fsae_interfaces
bool cdr_deserialize_std_msgs__msg__Header(
  eprosima::fastcdr::Cdr & cdr,
  std_msgs__msg__Header * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_fsae_interfaces
size_t get_serialized_size_std_msgs__msg__Header(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_fsae_interfaces
size_t max_serialized_size_std_msgs__msg__Header(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_fsae_interfaces
bool cdr_serialize_key_std_msgs__msg__Header(
  const std_msgs__msg__Header * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_fsae_interfaces
size_t get_serialized_size_key_std_msgs__msg__Header(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_fsae_interfaces
size_t max_serialized_size_key_std_msgs__msg__Header(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_fsae_interfaces
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, std_msgs, msg, Header)();


using _CANStamped__ros_msg_type = fsae_interfaces__msg__CANStamped;


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
bool cdr_serialize_fsae_interfaces__msg__CANStamped(
  const fsae_interfaces__msg__CANStamped * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: header
  {
    cdr_serialize_std_msgs__msg__Header(
      &ros_message->header, cdr);
  }

  // Field name: can
  {
    cdr_serialize_fsae_interfaces__msg__CAN(
      &ros_message->can, cdr);
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
bool cdr_deserialize_fsae_interfaces__msg__CANStamped(
  eprosima::fastcdr::Cdr & cdr,
  fsae_interfaces__msg__CANStamped * ros_message)
{
  // Field name: header
  {
    cdr_deserialize_std_msgs__msg__Header(cdr, &ros_message->header);
  }

  // Field name: can
  {
    cdr_deserialize_fsae_interfaces__msg__CAN(cdr, &ros_message->can);
  }

  return true;
}  // NOLINT(readability/fn_size)


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
size_t get_serialized_size_fsae_interfaces__msg__CANStamped(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _CANStamped__ros_msg_type * ros_message = static_cast<const _CANStamped__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: header
  current_alignment += get_serialized_size_std_msgs__msg__Header(
    &(ros_message->header), current_alignment);

  // Field name: can
  current_alignment += get_serialized_size_fsae_interfaces__msg__CAN(
    &(ros_message->can), current_alignment);

  return current_alignment - initial_alignment;
}


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
size_t max_serialized_size_fsae_interfaces__msg__CANStamped(
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

  // Field name: header
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_std_msgs__msg__Header(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: can
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_fsae_interfaces__msg__CAN(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }


  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = fsae_interfaces__msg__CANStamped;
    is_plain =
      (
      offsetof(DataType, can) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
bool cdr_serialize_key_fsae_interfaces__msg__CANStamped(
  const fsae_interfaces__msg__CANStamped * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: header
  {
    cdr_serialize_key_std_msgs__msg__Header(
      &ros_message->header, cdr);
  }

  // Field name: can
  {
    cdr_serialize_key_fsae_interfaces__msg__CAN(
      &ros_message->can, cdr);
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
size_t get_serialized_size_key_fsae_interfaces__msg__CANStamped(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _CANStamped__ros_msg_type * ros_message = static_cast<const _CANStamped__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;

  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: header
  current_alignment += get_serialized_size_key_std_msgs__msg__Header(
    &(ros_message->header), current_alignment);

  // Field name: can
  current_alignment += get_serialized_size_key_fsae_interfaces__msg__CAN(
    &(ros_message->can), current_alignment);

  return current_alignment - initial_alignment;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
size_t max_serialized_size_key_fsae_interfaces__msg__CANStamped(
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
  // Field name: header
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_std_msgs__msg__Header(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: can
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_fsae_interfaces__msg__CAN(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = fsae_interfaces__msg__CANStamped;
    is_plain =
      (
      offsetof(DataType, can) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}


static bool _CANStamped__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const fsae_interfaces__msg__CANStamped * ros_message = static_cast<const fsae_interfaces__msg__CANStamped *>(untyped_ros_message);
  (void)ros_message;
  return cdr_serialize_fsae_interfaces__msg__CANStamped(ros_message, cdr);
}

static bool _CANStamped__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  fsae_interfaces__msg__CANStamped * ros_message = static_cast<fsae_interfaces__msg__CANStamped *>(untyped_ros_message);
  (void)ros_message;
  return cdr_deserialize_fsae_interfaces__msg__CANStamped(cdr, ros_message);
}

static uint32_t _CANStamped__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_fsae_interfaces__msg__CANStamped(
      untyped_ros_message, 0));
}

static size_t _CANStamped__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_fsae_interfaces__msg__CANStamped(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_CANStamped = {
  "fsae_interfaces::msg",
  "CANStamped",
  _CANStamped__cdr_serialize,
  _CANStamped__cdr_deserialize,
  _CANStamped__get_serialized_size,
  _CANStamped__max_serialized_size,
  nullptr
};

static rosidl_message_type_support_t _CANStamped__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_CANStamped,
  get_message_typesupport_handle_function,
  &fsae_interfaces__msg__CANStamped__get_type_hash,
  &fsae_interfaces__msg__CANStamped__get_type_description,
  &fsae_interfaces__msg__CANStamped__get_type_description_sources,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, fsae_interfaces, msg, CANStamped)() {
  return &_CANStamped__type_support;
}

#if defined(__cplusplus)
}
#endif

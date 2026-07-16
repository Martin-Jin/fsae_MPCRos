// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from fsae_interfaces:msg/HardwareStates.idl
// generated code does not contain a copyright notice
#include "fsae_interfaces/msg/detail/hardware_states__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <cstddef>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/serialization_helpers.hpp"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "fsae_interfaces/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "fsae_interfaces/msg/detail/hardware_states__struct.h"
#include "fsae_interfaces/msg/detail/hardware_states__functions.h"
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


using _HardwareStates__ros_msg_type = fsae_interfaces__msg__HardwareStates;


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
bool cdr_serialize_fsae_interfaces__msg__HardwareStates(
  const fsae_interfaces__msg__HardwareStates * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: ebs_active
  {
    cdr << ros_message->ebs_active;
  }

  // Field name: ts_active
  {
    cdr << ros_message->ts_active;
  }

  // Field name: in_gear
  {
    cdr << ros_message->in_gear;
  }

  // Field name: master_switch_on
  {
    cdr << ros_message->master_switch_on;
  }

  // Field name: asb_ready
  {
    cdr << ros_message->asb_ready;
  }

  // Field name: brakes_engaged
  {
    cdr << ros_message->brakes_engaged;
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
bool cdr_deserialize_fsae_interfaces__msg__HardwareStates(
  eprosima::fastcdr::Cdr & cdr,
  fsae_interfaces__msg__HardwareStates * ros_message)
{
  // Field name: ebs_active
  {
    cdr >> ros_message->ebs_active;
  }

  // Field name: ts_active
  {
    cdr >> ros_message->ts_active;
  }

  // Field name: in_gear
  {
    cdr >> ros_message->in_gear;
  }

  // Field name: master_switch_on
  {
    cdr >> ros_message->master_switch_on;
  }

  // Field name: asb_ready
  {
    cdr >> ros_message->asb_ready;
  }

  // Field name: brakes_engaged
  {
    cdr >> ros_message->brakes_engaged;
  }

  return true;
}  // NOLINT(readability/fn_size)


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
size_t get_serialized_size_fsae_interfaces__msg__HardwareStates(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _HardwareStates__ros_msg_type * ros_message = static_cast<const _HardwareStates__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: ebs_active
  {
    size_t item_size = sizeof(ros_message->ebs_active);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: ts_active
  {
    size_t item_size = sizeof(ros_message->ts_active);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: in_gear
  {
    size_t item_size = sizeof(ros_message->in_gear);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: master_switch_on
  {
    size_t item_size = sizeof(ros_message->master_switch_on);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: asb_ready
  {
    size_t item_size = sizeof(ros_message->asb_ready);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: brakes_engaged
  {
    size_t item_size = sizeof(ros_message->brakes_engaged);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
size_t max_serialized_size_fsae_interfaces__msg__HardwareStates(
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

  // Field name: ebs_active
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: ts_active
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: in_gear
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: master_switch_on
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: asb_ready
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: brakes_engaged
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
    using DataType = fsae_interfaces__msg__HardwareStates;
    is_plain =
      (
      offsetof(DataType, brakes_engaged) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
bool cdr_serialize_key_fsae_interfaces__msg__HardwareStates(
  const fsae_interfaces__msg__HardwareStates * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: ebs_active
  {
    cdr << ros_message->ebs_active;
  }

  // Field name: ts_active
  {
    cdr << ros_message->ts_active;
  }

  // Field name: in_gear
  {
    cdr << ros_message->in_gear;
  }

  // Field name: master_switch_on
  {
    cdr << ros_message->master_switch_on;
  }

  // Field name: asb_ready
  {
    cdr << ros_message->asb_ready;
  }

  // Field name: brakes_engaged
  {
    cdr << ros_message->brakes_engaged;
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
size_t get_serialized_size_key_fsae_interfaces__msg__HardwareStates(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _HardwareStates__ros_msg_type * ros_message = static_cast<const _HardwareStates__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;

  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: ebs_active
  {
    size_t item_size = sizeof(ros_message->ebs_active);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: ts_active
  {
    size_t item_size = sizeof(ros_message->ts_active);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: in_gear
  {
    size_t item_size = sizeof(ros_message->in_gear);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: master_switch_on
  {
    size_t item_size = sizeof(ros_message->master_switch_on);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: asb_ready
  {
    size_t item_size = sizeof(ros_message->asb_ready);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: brakes_engaged
  {
    size_t item_size = sizeof(ros_message->brakes_engaged);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
size_t max_serialized_size_key_fsae_interfaces__msg__HardwareStates(
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
  // Field name: ebs_active
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: ts_active
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: in_gear
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: master_switch_on
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: asb_ready
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: brakes_engaged
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
    using DataType = fsae_interfaces__msg__HardwareStates;
    is_plain =
      (
      offsetof(DataType, brakes_engaged) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}


static bool _HardwareStates__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const fsae_interfaces__msg__HardwareStates * ros_message = static_cast<const fsae_interfaces__msg__HardwareStates *>(untyped_ros_message);
  (void)ros_message;
  return cdr_serialize_fsae_interfaces__msg__HardwareStates(ros_message, cdr);
}

static bool _HardwareStates__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  fsae_interfaces__msg__HardwareStates * ros_message = static_cast<fsae_interfaces__msg__HardwareStates *>(untyped_ros_message);
  (void)ros_message;
  return cdr_deserialize_fsae_interfaces__msg__HardwareStates(cdr, ros_message);
}

static uint32_t _HardwareStates__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_fsae_interfaces__msg__HardwareStates(
      untyped_ros_message, 0));
}

static size_t _HardwareStates__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_fsae_interfaces__msg__HardwareStates(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_HardwareStates = {
  "fsae_interfaces::msg",
  "HardwareStates",
  _HardwareStates__cdr_serialize,
  _HardwareStates__cdr_deserialize,
  _HardwareStates__get_serialized_size,
  _HardwareStates__max_serialized_size,
  nullptr
};

static rosidl_message_type_support_t _HardwareStates__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_HardwareStates,
  get_message_typesupport_handle_function,
  &fsae_interfaces__msg__HardwareStates__get_type_hash,
  &fsae_interfaces__msg__HardwareStates__get_type_description,
  &fsae_interfaces__msg__HardwareStates__get_type_description_sources,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, fsae_interfaces, msg, HardwareStates)() {
  return &_HardwareStates__type_support;
}

#if defined(__cplusplus)
}
#endif

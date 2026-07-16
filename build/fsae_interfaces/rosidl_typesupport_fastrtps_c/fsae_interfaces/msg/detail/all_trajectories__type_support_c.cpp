// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from fsae_interfaces:msg/AllTrajectories.idl
// generated code does not contain a copyright notice
#include "fsae_interfaces/msg/detail/all_trajectories__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <cstddef>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/serialization_helpers.hpp"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "fsae_interfaces/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "fsae_interfaces/msg/detail/all_trajectories__struct.h"
#include "fsae_interfaces/msg/detail/all_trajectories__functions.h"
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

#include "geometry_msgs/msg/detail/pose_array__functions.h"  // trajectories

// forward declare type support functions

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_fsae_interfaces
bool cdr_serialize_geometry_msgs__msg__PoseArray(
  const geometry_msgs__msg__PoseArray * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_fsae_interfaces
bool cdr_deserialize_geometry_msgs__msg__PoseArray(
  eprosima::fastcdr::Cdr & cdr,
  geometry_msgs__msg__PoseArray * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_fsae_interfaces
size_t get_serialized_size_geometry_msgs__msg__PoseArray(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_fsae_interfaces
size_t max_serialized_size_geometry_msgs__msg__PoseArray(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_fsae_interfaces
bool cdr_serialize_key_geometry_msgs__msg__PoseArray(
  const geometry_msgs__msg__PoseArray * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_fsae_interfaces
size_t get_serialized_size_key_geometry_msgs__msg__PoseArray(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_fsae_interfaces
size_t max_serialized_size_key_geometry_msgs__msg__PoseArray(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_fsae_interfaces
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, geometry_msgs, msg, PoseArray)();


using _AllTrajectories__ros_msg_type = fsae_interfaces__msg__AllTrajectories;


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
bool cdr_serialize_fsae_interfaces__msg__AllTrajectories(
  const fsae_interfaces__msg__AllTrajectories * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: id
  {
    cdr << ros_message->id;
  }

  // Field name: trajectories
  {
    size_t size = ros_message->trajectories.size;
    auto array_ptr = ros_message->trajectories.data;
    cdr << static_cast<uint32_t>(size);
    for (size_t i = 0; i < size; ++i) {
      cdr_serialize_geometry_msgs__msg__PoseArray(
        &array_ptr[i], cdr);
    }
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
bool cdr_deserialize_fsae_interfaces__msg__AllTrajectories(
  eprosima::fastcdr::Cdr & cdr,
  fsae_interfaces__msg__AllTrajectories * ros_message)
{
  // Field name: id
  {
    cdr >> ros_message->id;
  }

  // Field name: trajectories
  {
    uint32_t cdrSize;
    cdr >> cdrSize;
    size_t size = static_cast<size_t>(cdrSize);

    // Check there are at least 'size' remaining bytes in the CDR stream before resizing
    auto old_state = cdr.get_state();
    bool correct_size = cdr.jump(size);
    cdr.set_state(old_state);
    if (!correct_size) {
      fprintf(stderr, "sequence size exceeds remaining buffer\n");
      return false;
    }

    if (ros_message->trajectories.data) {
      geometry_msgs__msg__PoseArray__Sequence__fini(&ros_message->trajectories);
    }
    if (!geometry_msgs__msg__PoseArray__Sequence__init(&ros_message->trajectories, size)) {
      fprintf(stderr, "failed to create array for field 'trajectories'");
      return false;
    }
    auto array_ptr = ros_message->trajectories.data;
    for (size_t i = 0; i < size; ++i) {
      cdr_deserialize_geometry_msgs__msg__PoseArray(cdr, &array_ptr[i]);
    }
  }

  return true;
}  // NOLINT(readability/fn_size)


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
size_t get_serialized_size_fsae_interfaces__msg__AllTrajectories(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _AllTrajectories__ros_msg_type * ros_message = static_cast<const _AllTrajectories__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: id
  {
    size_t item_size = sizeof(ros_message->id);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: trajectories
  {
    size_t array_size = ros_message->trajectories.size;
    auto array_ptr = ros_message->trajectories.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += get_serialized_size_geometry_msgs__msg__PoseArray(
        &array_ptr[index], current_alignment);
    }
  }

  return current_alignment - initial_alignment;
}


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
size_t max_serialized_size_fsae_interfaces__msg__AllTrajectories(
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

  // Field name: id
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint16_t);
    current_alignment += array_size * sizeof(uint16_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint16_t));
  }

  // Field name: trajectories
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_geometry_msgs__msg__PoseArray(
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
    using DataType = fsae_interfaces__msg__AllTrajectories;
    is_plain =
      (
      offsetof(DataType, trajectories) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
bool cdr_serialize_key_fsae_interfaces__msg__AllTrajectories(
  const fsae_interfaces__msg__AllTrajectories * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: id
  {
    cdr << ros_message->id;
  }

  // Field name: trajectories
  {
    size_t size = ros_message->trajectories.size;
    auto array_ptr = ros_message->trajectories.data;
    cdr << static_cast<uint32_t>(size);
    for (size_t i = 0; i < size; ++i) {
      cdr_serialize_key_geometry_msgs__msg__PoseArray(
        &array_ptr[i], cdr);
    }
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
size_t get_serialized_size_key_fsae_interfaces__msg__AllTrajectories(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _AllTrajectories__ros_msg_type * ros_message = static_cast<const _AllTrajectories__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;

  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: id
  {
    size_t item_size = sizeof(ros_message->id);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: trajectories
  {
    size_t array_size = ros_message->trajectories.size;
    auto array_ptr = ros_message->trajectories.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += get_serialized_size_key_geometry_msgs__msg__PoseArray(
        &array_ptr[index], current_alignment);
    }
  }

  return current_alignment - initial_alignment;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fsae_interfaces
size_t max_serialized_size_key_fsae_interfaces__msg__AllTrajectories(
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
  // Field name: id
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint16_t);
    current_alignment += array_size * sizeof(uint16_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint16_t));
  }

  // Field name: trajectories
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_geometry_msgs__msg__PoseArray(
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
    using DataType = fsae_interfaces__msg__AllTrajectories;
    is_plain =
      (
      offsetof(DataType, trajectories) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}


static bool _AllTrajectories__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const fsae_interfaces__msg__AllTrajectories * ros_message = static_cast<const fsae_interfaces__msg__AllTrajectories *>(untyped_ros_message);
  (void)ros_message;
  return cdr_serialize_fsae_interfaces__msg__AllTrajectories(ros_message, cdr);
}

static bool _AllTrajectories__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  fsae_interfaces__msg__AllTrajectories * ros_message = static_cast<fsae_interfaces__msg__AllTrajectories *>(untyped_ros_message);
  (void)ros_message;
  return cdr_deserialize_fsae_interfaces__msg__AllTrajectories(cdr, ros_message);
}

static uint32_t _AllTrajectories__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_fsae_interfaces__msg__AllTrajectories(
      untyped_ros_message, 0));
}

static size_t _AllTrajectories__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_fsae_interfaces__msg__AllTrajectories(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_AllTrajectories = {
  "fsae_interfaces::msg",
  "AllTrajectories",
  _AllTrajectories__cdr_serialize,
  _AllTrajectories__cdr_deserialize,
  _AllTrajectories__get_serialized_size,
  _AllTrajectories__max_serialized_size,
  nullptr
};

static rosidl_message_type_support_t _AllTrajectories__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_AllTrajectories,
  get_message_typesupport_handle_function,
  &fsae_interfaces__msg__AllTrajectories__get_type_hash,
  &fsae_interfaces__msg__AllTrajectories__get_type_description,
  &fsae_interfaces__msg__AllTrajectories__get_type_description_sources,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, fsae_interfaces, msg, AllTrajectories)() {
  return &_AllTrajectories__type_support;
}

#if defined(__cplusplus)
}
#endif

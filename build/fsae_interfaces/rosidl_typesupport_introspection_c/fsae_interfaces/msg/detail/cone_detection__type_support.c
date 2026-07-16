// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from fsae_interfaces:msg/ConeDetection.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "fsae_interfaces/msg/detail/cone_detection__rosidl_typesupport_introspection_c.h"
#include "fsae_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "fsae_interfaces/msg/detail/cone_detection__functions.h"
#include "fsae_interfaces/msg/detail/cone_detection__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"
// Member `car_pose`
#include "geometry_msgs/msg/pose.h"
// Member `car_pose`
#include "geometry_msgs/msg/detail/pose__rosidl_typesupport_introspection_c.h"
// Member `yellow`
// Member `blue`
// Member `small_orange`
// Member `big_orange`
#include "geometry_msgs/msg/point.h"
// Member `yellow`
// Member `blue`
// Member `small_orange`
// Member `big_orange`
#include "geometry_msgs/msg/detail/point__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__ConeDetection_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  fsae_interfaces__msg__ConeDetection__init(message_memory);
}

void fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__ConeDetection_fini_function(void * message_memory)
{
  fsae_interfaces__msg__ConeDetection__fini(message_memory);
}

size_t fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__size_function__ConeDetection__yellow(
  const void * untyped_member)
{
  const geometry_msgs__msg__Point__Sequence * member =
    (const geometry_msgs__msg__Point__Sequence *)(untyped_member);
  return member->size;
}

const void * fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__get_const_function__ConeDetection__yellow(
  const void * untyped_member, size_t index)
{
  const geometry_msgs__msg__Point__Sequence * member =
    (const geometry_msgs__msg__Point__Sequence *)(untyped_member);
  return &member->data[index];
}

void * fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__get_function__ConeDetection__yellow(
  void * untyped_member, size_t index)
{
  geometry_msgs__msg__Point__Sequence * member =
    (geometry_msgs__msg__Point__Sequence *)(untyped_member);
  return &member->data[index];
}

void fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__fetch_function__ConeDetection__yellow(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const geometry_msgs__msg__Point * item =
    ((const geometry_msgs__msg__Point *)
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__get_const_function__ConeDetection__yellow(untyped_member, index));
  geometry_msgs__msg__Point * value =
    (geometry_msgs__msg__Point *)(untyped_value);
  *value = *item;
}

void fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__assign_function__ConeDetection__yellow(
  void * untyped_member, size_t index, const void * untyped_value)
{
  geometry_msgs__msg__Point * item =
    ((geometry_msgs__msg__Point *)
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__get_function__ConeDetection__yellow(untyped_member, index));
  const geometry_msgs__msg__Point * value =
    (const geometry_msgs__msg__Point *)(untyped_value);
  *item = *value;
}

bool fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__resize_function__ConeDetection__yellow(
  void * untyped_member, size_t size)
{
  geometry_msgs__msg__Point__Sequence * member =
    (geometry_msgs__msg__Point__Sequence *)(untyped_member);
  geometry_msgs__msg__Point__Sequence__fini(member);
  return geometry_msgs__msg__Point__Sequence__init(member, size);
}

size_t fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__size_function__ConeDetection__blue(
  const void * untyped_member)
{
  const geometry_msgs__msg__Point__Sequence * member =
    (const geometry_msgs__msg__Point__Sequence *)(untyped_member);
  return member->size;
}

const void * fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__get_const_function__ConeDetection__blue(
  const void * untyped_member, size_t index)
{
  const geometry_msgs__msg__Point__Sequence * member =
    (const geometry_msgs__msg__Point__Sequence *)(untyped_member);
  return &member->data[index];
}

void * fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__get_function__ConeDetection__blue(
  void * untyped_member, size_t index)
{
  geometry_msgs__msg__Point__Sequence * member =
    (geometry_msgs__msg__Point__Sequence *)(untyped_member);
  return &member->data[index];
}

void fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__fetch_function__ConeDetection__blue(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const geometry_msgs__msg__Point * item =
    ((const geometry_msgs__msg__Point *)
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__get_const_function__ConeDetection__blue(untyped_member, index));
  geometry_msgs__msg__Point * value =
    (geometry_msgs__msg__Point *)(untyped_value);
  *value = *item;
}

void fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__assign_function__ConeDetection__blue(
  void * untyped_member, size_t index, const void * untyped_value)
{
  geometry_msgs__msg__Point * item =
    ((geometry_msgs__msg__Point *)
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__get_function__ConeDetection__blue(untyped_member, index));
  const geometry_msgs__msg__Point * value =
    (const geometry_msgs__msg__Point *)(untyped_value);
  *item = *value;
}

bool fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__resize_function__ConeDetection__blue(
  void * untyped_member, size_t size)
{
  geometry_msgs__msg__Point__Sequence * member =
    (geometry_msgs__msg__Point__Sequence *)(untyped_member);
  geometry_msgs__msg__Point__Sequence__fini(member);
  return geometry_msgs__msg__Point__Sequence__init(member, size);
}

size_t fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__size_function__ConeDetection__small_orange(
  const void * untyped_member)
{
  const geometry_msgs__msg__Point__Sequence * member =
    (const geometry_msgs__msg__Point__Sequence *)(untyped_member);
  return member->size;
}

const void * fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__get_const_function__ConeDetection__small_orange(
  const void * untyped_member, size_t index)
{
  const geometry_msgs__msg__Point__Sequence * member =
    (const geometry_msgs__msg__Point__Sequence *)(untyped_member);
  return &member->data[index];
}

void * fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__get_function__ConeDetection__small_orange(
  void * untyped_member, size_t index)
{
  geometry_msgs__msg__Point__Sequence * member =
    (geometry_msgs__msg__Point__Sequence *)(untyped_member);
  return &member->data[index];
}

void fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__fetch_function__ConeDetection__small_orange(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const geometry_msgs__msg__Point * item =
    ((const geometry_msgs__msg__Point *)
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__get_const_function__ConeDetection__small_orange(untyped_member, index));
  geometry_msgs__msg__Point * value =
    (geometry_msgs__msg__Point *)(untyped_value);
  *value = *item;
}

void fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__assign_function__ConeDetection__small_orange(
  void * untyped_member, size_t index, const void * untyped_value)
{
  geometry_msgs__msg__Point * item =
    ((geometry_msgs__msg__Point *)
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__get_function__ConeDetection__small_orange(untyped_member, index));
  const geometry_msgs__msg__Point * value =
    (const geometry_msgs__msg__Point *)(untyped_value);
  *item = *value;
}

bool fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__resize_function__ConeDetection__small_orange(
  void * untyped_member, size_t size)
{
  geometry_msgs__msg__Point__Sequence * member =
    (geometry_msgs__msg__Point__Sequence *)(untyped_member);
  geometry_msgs__msg__Point__Sequence__fini(member);
  return geometry_msgs__msg__Point__Sequence__init(member, size);
}

size_t fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__size_function__ConeDetection__big_orange(
  const void * untyped_member)
{
  const geometry_msgs__msg__Point__Sequence * member =
    (const geometry_msgs__msg__Point__Sequence *)(untyped_member);
  return member->size;
}

const void * fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__get_const_function__ConeDetection__big_orange(
  const void * untyped_member, size_t index)
{
  const geometry_msgs__msg__Point__Sequence * member =
    (const geometry_msgs__msg__Point__Sequence *)(untyped_member);
  return &member->data[index];
}

void * fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__get_function__ConeDetection__big_orange(
  void * untyped_member, size_t index)
{
  geometry_msgs__msg__Point__Sequence * member =
    (geometry_msgs__msg__Point__Sequence *)(untyped_member);
  return &member->data[index];
}

void fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__fetch_function__ConeDetection__big_orange(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const geometry_msgs__msg__Point * item =
    ((const geometry_msgs__msg__Point *)
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__get_const_function__ConeDetection__big_orange(untyped_member, index));
  geometry_msgs__msg__Point * value =
    (geometry_msgs__msg__Point *)(untyped_value);
  *value = *item;
}

void fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__assign_function__ConeDetection__big_orange(
  void * untyped_member, size_t index, const void * untyped_value)
{
  geometry_msgs__msg__Point * item =
    ((geometry_msgs__msg__Point *)
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__get_function__ConeDetection__big_orange(untyped_member, index));
  const geometry_msgs__msg__Point * value =
    (const geometry_msgs__msg__Point *)(untyped_value);
  *item = *value;
}

bool fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__resize_function__ConeDetection__big_orange(
  void * untyped_member, size_t size)
{
  geometry_msgs__msg__Point__Sequence * member =
    (geometry_msgs__msg__Point__Sequence *)(untyped_member);
  geometry_msgs__msg__Point__Sequence__fini(member);
  return geometry_msgs__msg__Point__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__ConeDetection_message_member_array[6] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces__msg__ConeDetection, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "car_pose",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces__msg__ConeDetection, car_pose),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "yellow",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces__msg__ConeDetection, yellow),  // bytes offset in struct
    NULL,  // default value
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__size_function__ConeDetection__yellow,  // size() function pointer
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__get_const_function__ConeDetection__yellow,  // get_const(index) function pointer
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__get_function__ConeDetection__yellow,  // get(index) function pointer
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__fetch_function__ConeDetection__yellow,  // fetch(index, &value) function pointer
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__assign_function__ConeDetection__yellow,  // assign(index, value) function pointer
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__resize_function__ConeDetection__yellow  // resize(index) function pointer
  },
  {
    "blue",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces__msg__ConeDetection, blue),  // bytes offset in struct
    NULL,  // default value
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__size_function__ConeDetection__blue,  // size() function pointer
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__get_const_function__ConeDetection__blue,  // get_const(index) function pointer
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__get_function__ConeDetection__blue,  // get(index) function pointer
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__fetch_function__ConeDetection__blue,  // fetch(index, &value) function pointer
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__assign_function__ConeDetection__blue,  // assign(index, value) function pointer
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__resize_function__ConeDetection__blue  // resize(index) function pointer
  },
  {
    "small_orange",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces__msg__ConeDetection, small_orange),  // bytes offset in struct
    NULL,  // default value
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__size_function__ConeDetection__small_orange,  // size() function pointer
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__get_const_function__ConeDetection__small_orange,  // get_const(index) function pointer
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__get_function__ConeDetection__small_orange,  // get(index) function pointer
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__fetch_function__ConeDetection__small_orange,  // fetch(index, &value) function pointer
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__assign_function__ConeDetection__small_orange,  // assign(index, value) function pointer
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__resize_function__ConeDetection__small_orange  // resize(index) function pointer
  },
  {
    "big_orange",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces__msg__ConeDetection, big_orange),  // bytes offset in struct
    NULL,  // default value
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__size_function__ConeDetection__big_orange,  // size() function pointer
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__get_const_function__ConeDetection__big_orange,  // get_const(index) function pointer
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__get_function__ConeDetection__big_orange,  // get(index) function pointer
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__fetch_function__ConeDetection__big_orange,  // fetch(index, &value) function pointer
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__assign_function__ConeDetection__big_orange,  // assign(index, value) function pointer
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__resize_function__ConeDetection__big_orange  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__ConeDetection_message_members = {
  "fsae_interfaces__msg",  // message namespace
  "ConeDetection",  // message name
  6,  // number of fields
  sizeof(fsae_interfaces__msg__ConeDetection),
  false,  // has_any_key_member_
  fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__ConeDetection_message_member_array,  // message members
  fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__ConeDetection_init_function,  // function to initialize message memory (memory has to be allocated)
  fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__ConeDetection_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__ConeDetection_message_type_support_handle = {
  0,
  &fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__ConeDetection_message_members,
  get_message_typesupport_handle_function,
  &fsae_interfaces__msg__ConeDetection__get_type_hash,
  &fsae_interfaces__msg__ConeDetection__get_type_description,
  &fsae_interfaces__msg__ConeDetection__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_fsae_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, fsae_interfaces, msg, ConeDetection)() {
  fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__ConeDetection_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__ConeDetection_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, Pose)();
  fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__ConeDetection_message_member_array[2].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, Point)();
  fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__ConeDetection_message_member_array[3].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, Point)();
  fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__ConeDetection_message_member_array[4].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, Point)();
  fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__ConeDetection_message_member_array[5].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, Point)();
  if (!fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__ConeDetection_message_type_support_handle.typesupport_identifier) {
    fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__ConeDetection_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &fsae_interfaces__msg__ConeDetection__rosidl_typesupport_introspection_c__ConeDetection_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

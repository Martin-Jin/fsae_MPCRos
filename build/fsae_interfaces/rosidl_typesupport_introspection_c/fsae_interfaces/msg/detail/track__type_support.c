// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from fsae_interfaces:msg/Track.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "fsae_interfaces/msg/detail/track__rosidl_typesupport_introspection_c.h"
#include "fsae_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "fsae_interfaces/msg/detail/track__functions.h"
#include "fsae_interfaces/msg/detail/track__struct.h"


// Include directives for member types
// Member `cones`
#include "geometry_msgs/msg/point.h"
// Member `cones`
#include "geometry_msgs/msg/detail/point__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__Track_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  fsae_interfaces__msg__Track__init(message_memory);
}

void fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__Track_fini_function(void * message_memory)
{
  fsae_interfaces__msg__Track__fini(message_memory);
}

size_t fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__size_function__Track__cones(
  const void * untyped_member)
{
  const geometry_msgs__msg__Point__Sequence * member =
    (const geometry_msgs__msg__Point__Sequence *)(untyped_member);
  return member->size;
}

const void * fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__get_const_function__Track__cones(
  const void * untyped_member, size_t index)
{
  const geometry_msgs__msg__Point__Sequence * member =
    (const geometry_msgs__msg__Point__Sequence *)(untyped_member);
  return &member->data[index];
}

void * fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__get_function__Track__cones(
  void * untyped_member, size_t index)
{
  geometry_msgs__msg__Point__Sequence * member =
    (geometry_msgs__msg__Point__Sequence *)(untyped_member);
  return &member->data[index];
}

void fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__fetch_function__Track__cones(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const geometry_msgs__msg__Point * item =
    ((const geometry_msgs__msg__Point *)
    fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__get_const_function__Track__cones(untyped_member, index));
  geometry_msgs__msg__Point * value =
    (geometry_msgs__msg__Point *)(untyped_value);
  *value = *item;
}

void fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__assign_function__Track__cones(
  void * untyped_member, size_t index, const void * untyped_value)
{
  geometry_msgs__msg__Point * item =
    ((geometry_msgs__msg__Point *)
    fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__get_function__Track__cones(untyped_member, index));
  const geometry_msgs__msg__Point * value =
    (const geometry_msgs__msg__Point *)(untyped_value);
  *item = *value;
}

bool fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__resize_function__Track__cones(
  void * untyped_member, size_t size)
{
  geometry_msgs__msg__Point__Sequence * member =
    (geometry_msgs__msg__Point__Sequence *)(untyped_member);
  geometry_msgs__msg__Point__Sequence__fini(member);
  return geometry_msgs__msg__Point__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__Track_message_member_array[1] = {
  {
    "cones",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces__msg__Track, cones),  // bytes offset in struct
    NULL,  // default value
    fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__size_function__Track__cones,  // size() function pointer
    fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__get_const_function__Track__cones,  // get_const(index) function pointer
    fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__get_function__Track__cones,  // get(index) function pointer
    fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__fetch_function__Track__cones,  // fetch(index, &value) function pointer
    fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__assign_function__Track__cones,  // assign(index, value) function pointer
    fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__resize_function__Track__cones  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__Track_message_members = {
  "fsae_interfaces__msg",  // message namespace
  "Track",  // message name
  1,  // number of fields
  sizeof(fsae_interfaces__msg__Track),
  false,  // has_any_key_member_
  fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__Track_message_member_array,  // message members
  fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__Track_init_function,  // function to initialize message memory (memory has to be allocated)
  fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__Track_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__Track_message_type_support_handle = {
  0,
  &fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__Track_message_members,
  get_message_typesupport_handle_function,
  &fsae_interfaces__msg__Track__get_type_hash,
  &fsae_interfaces__msg__Track__get_type_description,
  &fsae_interfaces__msg__Track__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_fsae_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, fsae_interfaces, msg, Track)() {
  fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__Track_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, Point)();
  if (!fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__Track_message_type_support_handle.typesupport_identifier) {
    fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__Track_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &fsae_interfaces__msg__Track__rosidl_typesupport_introspection_c__Track_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

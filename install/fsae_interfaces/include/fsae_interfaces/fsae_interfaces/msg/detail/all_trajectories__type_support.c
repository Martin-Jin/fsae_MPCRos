// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from fsae_interfaces:msg/AllTrajectories.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "fsae_interfaces/msg/detail/all_trajectories__rosidl_typesupport_introspection_c.h"
#include "fsae_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "fsae_interfaces/msg/detail/all_trajectories__functions.h"
#include "fsae_interfaces/msg/detail/all_trajectories__struct.h"


// Include directives for member types
// Member `trajectories`
#include "geometry_msgs/msg/pose_array.h"
// Member `trajectories`
#include "geometry_msgs/msg/detail/pose_array__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__AllTrajectories_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  fsae_interfaces__msg__AllTrajectories__init(message_memory);
}

void fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__AllTrajectories_fini_function(void * message_memory)
{
  fsae_interfaces__msg__AllTrajectories__fini(message_memory);
}

size_t fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__size_function__AllTrajectories__trajectories(
  const void * untyped_member)
{
  const geometry_msgs__msg__PoseArray__Sequence * member =
    (const geometry_msgs__msg__PoseArray__Sequence *)(untyped_member);
  return member->size;
}

const void * fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__get_const_function__AllTrajectories__trajectories(
  const void * untyped_member, size_t index)
{
  const geometry_msgs__msg__PoseArray__Sequence * member =
    (const geometry_msgs__msg__PoseArray__Sequence *)(untyped_member);
  return &member->data[index];
}

void * fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__get_function__AllTrajectories__trajectories(
  void * untyped_member, size_t index)
{
  geometry_msgs__msg__PoseArray__Sequence * member =
    (geometry_msgs__msg__PoseArray__Sequence *)(untyped_member);
  return &member->data[index];
}

void fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__fetch_function__AllTrajectories__trajectories(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const geometry_msgs__msg__PoseArray * item =
    ((const geometry_msgs__msg__PoseArray *)
    fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__get_const_function__AllTrajectories__trajectories(untyped_member, index));
  geometry_msgs__msg__PoseArray * value =
    (geometry_msgs__msg__PoseArray *)(untyped_value);
  *value = *item;
}

void fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__assign_function__AllTrajectories__trajectories(
  void * untyped_member, size_t index, const void * untyped_value)
{
  geometry_msgs__msg__PoseArray * item =
    ((geometry_msgs__msg__PoseArray *)
    fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__get_function__AllTrajectories__trajectories(untyped_member, index));
  const geometry_msgs__msg__PoseArray * value =
    (const geometry_msgs__msg__PoseArray *)(untyped_value);
  *item = *value;
}

bool fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__resize_function__AllTrajectories__trajectories(
  void * untyped_member, size_t size)
{
  geometry_msgs__msg__PoseArray__Sequence * member =
    (geometry_msgs__msg__PoseArray__Sequence *)(untyped_member);
  geometry_msgs__msg__PoseArray__Sequence__fini(member);
  return geometry_msgs__msg__PoseArray__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__AllTrajectories_message_member_array[2] = {
  {
    "id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT16,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces__msg__AllTrajectories, id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "trajectories",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fsae_interfaces__msg__AllTrajectories, trajectories),  // bytes offset in struct
    NULL,  // default value
    fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__size_function__AllTrajectories__trajectories,  // size() function pointer
    fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__get_const_function__AllTrajectories__trajectories,  // get_const(index) function pointer
    fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__get_function__AllTrajectories__trajectories,  // get(index) function pointer
    fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__fetch_function__AllTrajectories__trajectories,  // fetch(index, &value) function pointer
    fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__assign_function__AllTrajectories__trajectories,  // assign(index, value) function pointer
    fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__resize_function__AllTrajectories__trajectories  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__AllTrajectories_message_members = {
  "fsae_interfaces__msg",  // message namespace
  "AllTrajectories",  // message name
  2,  // number of fields
  sizeof(fsae_interfaces__msg__AllTrajectories),
  false,  // has_any_key_member_
  fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__AllTrajectories_message_member_array,  // message members
  fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__AllTrajectories_init_function,  // function to initialize message memory (memory has to be allocated)
  fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__AllTrajectories_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__AllTrajectories_message_type_support_handle = {
  0,
  &fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__AllTrajectories_message_members,
  get_message_typesupport_handle_function,
  &fsae_interfaces__msg__AllTrajectories__get_type_hash,
  &fsae_interfaces__msg__AllTrajectories__get_type_description,
  &fsae_interfaces__msg__AllTrajectories__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_fsae_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, fsae_interfaces, msg, AllTrajectories)() {
  fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__AllTrajectories_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, PoseArray)();
  if (!fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__AllTrajectories_message_type_support_handle.typesupport_identifier) {
    fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__AllTrajectories_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &fsae_interfaces__msg__AllTrajectories__rosidl_typesupport_introspection_c__AllTrajectories_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

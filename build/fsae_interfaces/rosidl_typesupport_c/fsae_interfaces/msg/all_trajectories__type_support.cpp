// generated from rosidl_typesupport_c/resource/idl__type_support.cpp.em
// with input from fsae_interfaces:msg/AllTrajectories.idl
// generated code does not contain a copyright notice

#include "cstddef"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "fsae_interfaces/msg/detail/all_trajectories__struct.h"
#include "fsae_interfaces/msg/detail/all_trajectories__type_support.h"
#include "fsae_interfaces/msg/detail/all_trajectories__functions.h"
#include "rosidl_typesupport_c/identifier.h"
#include "rosidl_typesupport_c/message_type_support_dispatch.h"
#include "rosidl_typesupport_c/type_support_map.h"
#include "rosidl_typesupport_c/visibility_control.h"
#include "rosidl_typesupport_interface/macros.h"

namespace fsae_interfaces
{

namespace msg
{

namespace rosidl_typesupport_c
{

typedef struct _AllTrajectories_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _AllTrajectories_type_support_ids_t;

static const _AllTrajectories_type_support_ids_t _AllTrajectories_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _AllTrajectories_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _AllTrajectories_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _AllTrajectories_type_support_symbol_names_t _AllTrajectories_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, fsae_interfaces, msg, AllTrajectories)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, fsae_interfaces, msg, AllTrajectories)),
  }
};

typedef struct _AllTrajectories_type_support_data_t
{
  void * data[2];
} _AllTrajectories_type_support_data_t;

static _AllTrajectories_type_support_data_t _AllTrajectories_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _AllTrajectories_message_typesupport_map = {
  2,
  "fsae_interfaces",
  &_AllTrajectories_message_typesupport_ids.typesupport_identifier[0],
  &_AllTrajectories_message_typesupport_symbol_names.symbol_name[0],
  &_AllTrajectories_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t AllTrajectories_message_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_AllTrajectories_message_typesupport_map),
  rosidl_typesupport_c__get_message_typesupport_handle_function,
  &fsae_interfaces__msg__AllTrajectories__get_type_hash,
  &fsae_interfaces__msg__AllTrajectories__get_type_description,
  &fsae_interfaces__msg__AllTrajectories__get_type_description_sources,
};

}  // namespace rosidl_typesupport_c

}  // namespace msg

}  // namespace fsae_interfaces

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_c, fsae_interfaces, msg, AllTrajectories)() {
  return &::fsae_interfaces::msg::rosidl_typesupport_c::AllTrajectories_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

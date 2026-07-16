// generated from rosidl_typesupport_cpp/resource/idl__type_support.cpp.em
// with input from fsae_interfaces:msg/HardwareStates.idl
// generated code does not contain a copyright notice

#include "cstddef"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "fsae_interfaces/msg/detail/hardware_states__functions.h"
#include "fsae_interfaces/msg/detail/hardware_states__struct.hpp"
#include "rosidl_typesupport_cpp/identifier.hpp"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_c/type_support_map.h"
#include "rosidl_typesupport_cpp/message_type_support_dispatch.hpp"
#include "rosidl_typesupport_cpp/visibility_control.h"
#include "rosidl_typesupport_interface/macros.h"

namespace fsae_interfaces
{

namespace msg
{

namespace rosidl_typesupport_cpp
{

typedef struct _HardwareStates_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _HardwareStates_type_support_ids_t;

static const _HardwareStates_type_support_ids_t _HardwareStates_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _HardwareStates_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _HardwareStates_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _HardwareStates_type_support_symbol_names_t _HardwareStates_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, fsae_interfaces, msg, HardwareStates)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, fsae_interfaces, msg, HardwareStates)),
  }
};

typedef struct _HardwareStates_type_support_data_t
{
  void * data[2];
} _HardwareStates_type_support_data_t;

static _HardwareStates_type_support_data_t _HardwareStates_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _HardwareStates_message_typesupport_map = {
  2,
  "fsae_interfaces",
  &_HardwareStates_message_typesupport_ids.typesupport_identifier[0],
  &_HardwareStates_message_typesupport_symbol_names.symbol_name[0],
  &_HardwareStates_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t HardwareStates_message_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_HardwareStates_message_typesupport_map),
  ::rosidl_typesupport_cpp::get_message_typesupport_handle_function,
  &fsae_interfaces__msg__HardwareStates__get_type_hash,
  &fsae_interfaces__msg__HardwareStates__get_type_description,
  &fsae_interfaces__msg__HardwareStates__get_type_description_sources,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace msg

}  // namespace fsae_interfaces

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<fsae_interfaces::msg::HardwareStates>()
{
  return &::fsae_interfaces::msg::rosidl_typesupport_cpp::HardwareStates_message_type_support_handle;
}

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_cpp, fsae_interfaces, msg, HardwareStates)() {
  return get_message_type_support_handle<fsae_interfaces::msg::HardwareStates>();
}

#ifdef __cplusplus
}
#endif
}  // namespace rosidl_typesupport_cpp

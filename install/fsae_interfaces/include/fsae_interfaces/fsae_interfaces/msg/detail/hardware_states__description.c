// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from fsae_interfaces:msg/HardwareStates.idl
// generated code does not contain a copyright notice

#include "fsae_interfaces/msg/detail/hardware_states__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_fsae_interfaces
const rosidl_type_hash_t *
fsae_interfaces__msg__HardwareStates__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xbd, 0xce, 0xab, 0x33, 0xcd, 0x86, 0x95, 0x08,
      0x13, 0x5d, 0x87, 0x7b, 0x1e, 0x14, 0x76, 0x14,
      0xe6, 0xe9, 0xc2, 0xf6, 0x79, 0x97, 0x96, 0x17,
      0xbd, 0xc9, 0xff, 0x54, 0x71, 0x1b, 0x38, 0x0c,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char fsae_interfaces__msg__HardwareStates__TYPE_NAME[] = "fsae_interfaces/msg/HardwareStates";

// Define type names, field names, and default values
static char fsae_interfaces__msg__HardwareStates__FIELD_NAME__ebs_active[] = "ebs_active";
static char fsae_interfaces__msg__HardwareStates__FIELD_NAME__ts_active[] = "ts_active";
static char fsae_interfaces__msg__HardwareStates__FIELD_NAME__in_gear[] = "in_gear";
static char fsae_interfaces__msg__HardwareStates__FIELD_NAME__master_switch_on[] = "master_switch_on";
static char fsae_interfaces__msg__HardwareStates__FIELD_NAME__asb_ready[] = "asb_ready";
static char fsae_interfaces__msg__HardwareStates__FIELD_NAME__brakes_engaged[] = "brakes_engaged";

static rosidl_runtime_c__type_description__Field fsae_interfaces__msg__HardwareStates__FIELDS[] = {
  {
    {fsae_interfaces__msg__HardwareStates__FIELD_NAME__ebs_active, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fsae_interfaces__msg__HardwareStates__FIELD_NAME__ts_active, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fsae_interfaces__msg__HardwareStates__FIELD_NAME__in_gear, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fsae_interfaces__msg__HardwareStates__FIELD_NAME__master_switch_on, 16, 16},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fsae_interfaces__msg__HardwareStates__FIELD_NAME__asb_ready, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fsae_interfaces__msg__HardwareStates__FIELD_NAME__brakes_engaged, 14, 14},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
fsae_interfaces__msg__HardwareStates__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {fsae_interfaces__msg__HardwareStates__TYPE_NAME, 34, 34},
      {fsae_interfaces__msg__HardwareStates__FIELDS, 6, 6},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "uint8 ebs_active \n"
  "uint8 ts_active \n"
  "uint8 in_gear \n"
  "uint8 master_switch_on \n"
  "uint8 asb_ready \n"
  "uint8 brakes_engaged ";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
fsae_interfaces__msg__HardwareStates__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {fsae_interfaces__msg__HardwareStates__TYPE_NAME, 34, 34},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 113, 113},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
fsae_interfaces__msg__HardwareStates__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *fsae_interfaces__msg__HardwareStates__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}

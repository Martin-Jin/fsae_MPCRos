// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from fsae_interfaces:msg/CAN.idl
// generated code does not contain a copyright notice

#include "fsae_interfaces/msg/detail/can__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_fsae_interfaces
const rosidl_type_hash_t *
fsae_interfaces__msg__CAN__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x51, 0x5c, 0xb0, 0x4d, 0x77, 0x69, 0xaf, 0xb6,
      0x47, 0xe6, 0x2c, 0xf9, 0xdc, 0x05, 0xe2, 0x84,
      0xda, 0x73, 0x39, 0xa8, 0xc6, 0x64, 0x8a, 0xa7,
      0x08, 0x2f, 0x02, 0x43, 0x67, 0x44, 0x90, 0x10,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char fsae_interfaces__msg__CAN__TYPE_NAME[] = "fsae_interfaces/msg/CAN";

// Define type names, field names, and default values
static char fsae_interfaces__msg__CAN__FIELD_NAME__id[] = "id";
static char fsae_interfaces__msg__CAN__FIELD_NAME__is_rtr[] = "is_rtr";
static char fsae_interfaces__msg__CAN__DEFAULT_VALUE__is_rtr[] = "False";
static char fsae_interfaces__msg__CAN__FIELD_NAME__data[] = "data";
static char fsae_interfaces__msg__CAN__DEFAULT_VALUE__data[] = "(0, 0, 0, 0, 0, 0, 0, 0)";

static rosidl_runtime_c__type_description__Field fsae_interfaces__msg__CAN__FIELDS[] = {
  {
    {fsae_interfaces__msg__CAN__FIELD_NAME__id, 2, 2},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT16,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fsae_interfaces__msg__CAN__FIELD_NAME__is_rtr, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN,
      0,
      0,
      {NULL, 0, 0},
    },
    {fsae_interfaces__msg__CAN__DEFAULT_VALUE__is_rtr, 5, 5},
  },
  {
    {fsae_interfaces__msg__CAN__FIELD_NAME__data, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8_ARRAY,
      8,
      0,
      {NULL, 0, 0},
    },
    {fsae_interfaces__msg__CAN__DEFAULT_VALUE__data, 24, 24},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
fsae_interfaces__msg__CAN__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {fsae_interfaces__msg__CAN__TYPE_NAME, 23, 23},
      {fsae_interfaces__msg__CAN__FIELDS, 3, 3},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "uint16 id \n"
  "\n"
  "bool is_rtr false \n"
  "uint8[8] data [0, 0, 0, 0, 0, 0, 0, 0]";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
fsae_interfaces__msg__CAN__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {fsae_interfaces__msg__CAN__TYPE_NAME, 23, 23},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 70, 70},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
fsae_interfaces__msg__CAN__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *fsae_interfaces__msg__CAN__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}

// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from fsae_interfaces:msg/MissionStates.idl
// generated code does not contain a copyright notice

#include "fsae_interfaces/msg/detail/mission_states__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_fsae_interfaces
const rosidl_type_hash_t *
fsae_interfaces__msg__MissionStates__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x19, 0xde, 0x38, 0x36, 0xbe, 0xf3, 0x2d, 0x81,
      0xa2, 0x4b, 0x67, 0x76, 0xc5, 0x55, 0x18, 0x6d,
      0x2b, 0x2b, 0xfe, 0xbf, 0x71, 0xa9, 0x7f, 0xa6,
      0xd3, 0xc4, 0x63, 0x5a, 0xb0, 0xae, 0x70, 0xcf,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char fsae_interfaces__msg__MissionStates__TYPE_NAME[] = "fsae_interfaces/msg/MissionStates";

// Define type names, field names, and default values
static char fsae_interfaces__msg__MissionStates__FIELD_NAME__mission_selected[] = "mission_selected";
static char fsae_interfaces__msg__MissionStates__FIELD_NAME__mission_finished[] = "mission_finished";

static rosidl_runtime_c__type_description__Field fsae_interfaces__msg__MissionStates__FIELDS[] = {
  {
    {fsae_interfaces__msg__MissionStates__FIELD_NAME__mission_selected, 16, 16},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fsae_interfaces__msg__MissionStates__FIELD_NAME__mission_finished, 16, 16},
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
fsae_interfaces__msg__MissionStates__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {fsae_interfaces__msg__MissionStates__TYPE_NAME, 33, 33},
      {fsae_interfaces__msg__MissionStates__FIELDS, 2, 2},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "uint8 mission_selected \n"
  "uint8 mission_finished ";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
fsae_interfaces__msg__MissionStates__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {fsae_interfaces__msg__MissionStates__TYPE_NAME, 33, 33},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 48, 48},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
fsae_interfaces__msg__MissionStates__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *fsae_interfaces__msg__MissionStates__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}

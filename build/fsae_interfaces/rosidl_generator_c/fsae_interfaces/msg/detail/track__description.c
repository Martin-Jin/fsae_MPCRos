// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from fsae_interfaces:msg/Track.idl
// generated code does not contain a copyright notice

#include "fsae_interfaces/msg/detail/track__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_fsae_interfaces
const rosidl_type_hash_t *
fsae_interfaces__msg__Track__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x91, 0xeb, 0xc4, 0xcc, 0x31, 0x05, 0x23, 0x9b,
      0xcd, 0xc7, 0x65, 0x4a, 0x7e, 0x13, 0xb4, 0x16,
      0xcb, 0x3a, 0x34, 0xf7, 0x4f, 0xb8, 0x44, 0x2b,
      0xb4, 0xb5, 0x8d, 0xf5, 0x43, 0x96, 0xae, 0x32,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "geometry_msgs/msg/detail/point__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t geometry_msgs__msg__Point__EXPECTED_HASH = {1, {
    0x69, 0x63, 0x08, 0x48, 0x42, 0xa9, 0xb0, 0x44,
    0x94, 0xd6, 0xb2, 0x94, 0x1d, 0x11, 0x44, 0x47,
    0x08, 0xd8, 0x92, 0xda, 0x2f, 0x4b, 0x09, 0x84,
    0x3b, 0x9c, 0x43, 0xf4, 0x2a, 0x7f, 0x68, 0x81,
  }};
#endif

static char fsae_interfaces__msg__Track__TYPE_NAME[] = "fsae_interfaces/msg/Track";
static char geometry_msgs__msg__Point__TYPE_NAME[] = "geometry_msgs/msg/Point";

// Define type names, field names, and default values
static char fsae_interfaces__msg__Track__FIELD_NAME__cones[] = "cones";

static rosidl_runtime_c__type_description__Field fsae_interfaces__msg__Track__FIELDS[] = {
  {
    {fsae_interfaces__msg__Track__FIELD_NAME__cones, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE_UNBOUNDED_SEQUENCE,
      0,
      0,
      {geometry_msgs__msg__Point__TYPE_NAME, 23, 23},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription fsae_interfaces__msg__Track__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {geometry_msgs__msg__Point__TYPE_NAME, 23, 23},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
fsae_interfaces__msg__Track__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {fsae_interfaces__msg__Track__TYPE_NAME, 25, 25},
      {fsae_interfaces__msg__Track__FIELDS, 1, 1},
    },
    {fsae_interfaces__msg__Track__REFERENCED_TYPE_DESCRIPTIONS, 1, 1},
  };
  if (!constructed) {
    assert(0 == memcmp(&geometry_msgs__msg__Point__EXPECTED_HASH, geometry_msgs__msg__Point__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = geometry_msgs__msg__Point__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "geometry_msgs/Point[] cones ";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
fsae_interfaces__msg__Track__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {fsae_interfaces__msg__Track__TYPE_NAME, 25, 25},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 29, 29},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
fsae_interfaces__msg__Track__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[2];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 2, 2};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *fsae_interfaces__msg__Track__get_individual_type_description_source(NULL),
    sources[1] = *geometry_msgs__msg__Point__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}

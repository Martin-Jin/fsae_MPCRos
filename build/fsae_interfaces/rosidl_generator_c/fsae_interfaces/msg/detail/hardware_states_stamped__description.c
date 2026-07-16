// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from fsae_interfaces:msg/HardwareStatesStamped.idl
// generated code does not contain a copyright notice

#include "fsae_interfaces/msg/detail/hardware_states_stamped__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_fsae_interfaces
const rosidl_type_hash_t *
fsae_interfaces__msg__HardwareStatesStamped__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xdd, 0xc0, 0x7e, 0x83, 0x28, 0x44, 0x63, 0xde,
      0x35, 0x18, 0xc5, 0x10, 0x26, 0x0d, 0x61, 0xbb,
      0x15, 0x8c, 0xc8, 0x4a, 0x32, 0xdf, 0x2c, 0x31,
      0x19, 0x6b, 0x76, 0x79, 0x6a, 0xf2, 0xfb, 0x5a,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "fsae_interfaces/msg/detail/hardware_states__functions.h"
#include "builtin_interfaces/msg/detail/time__functions.h"
#include "std_msgs/msg/detail/header__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t builtin_interfaces__msg__Time__EXPECTED_HASH = {1, {
    0xb1, 0x06, 0x23, 0x5e, 0x25, 0xa4, 0xc5, 0xed,
    0x35, 0x09, 0x8a, 0xa0, 0xa6, 0x1a, 0x3e, 0xe9,
    0xc9, 0xb1, 0x8d, 0x19, 0x7f, 0x39, 0x8b, 0x0e,
    0x42, 0x06, 0xce, 0xa9, 0xac, 0xf9, 0xc1, 0x97,
  }};
static const rosidl_type_hash_t fsae_interfaces__msg__HardwareStates__EXPECTED_HASH = {1, {
    0xbd, 0xce, 0xab, 0x33, 0xcd, 0x86, 0x95, 0x08,
    0x13, 0x5d, 0x87, 0x7b, 0x1e, 0x14, 0x76, 0x14,
    0xe6, 0xe9, 0xc2, 0xf6, 0x79, 0x97, 0x96, 0x17,
    0xbd, 0xc9, 0xff, 0x54, 0x71, 0x1b, 0x38, 0x0c,
  }};
static const rosidl_type_hash_t std_msgs__msg__Header__EXPECTED_HASH = {1, {
    0xf4, 0x9f, 0xb3, 0xae, 0x2c, 0xf0, 0x70, 0xf7,
    0x93, 0x64, 0x5f, 0xf7, 0x49, 0x68, 0x3a, 0xc6,
    0xb0, 0x62, 0x03, 0xe4, 0x1c, 0x89, 0x1e, 0x17,
    0x70, 0x1b, 0x1c, 0xb5, 0x97, 0xce, 0x6a, 0x01,
  }};
#endif

static char fsae_interfaces__msg__HardwareStatesStamped__TYPE_NAME[] = "fsae_interfaces/msg/HardwareStatesStamped";
static char builtin_interfaces__msg__Time__TYPE_NAME[] = "builtin_interfaces/msg/Time";
static char fsae_interfaces__msg__HardwareStates__TYPE_NAME[] = "fsae_interfaces/msg/HardwareStates";
static char std_msgs__msg__Header__TYPE_NAME[] = "std_msgs/msg/Header";

// Define type names, field names, and default values
static char fsae_interfaces__msg__HardwareStatesStamped__FIELD_NAME__header[] = "header";
static char fsae_interfaces__msg__HardwareStatesStamped__FIELD_NAME__hardware_states[] = "hardware_states";

static rosidl_runtime_c__type_description__Field fsae_interfaces__msg__HardwareStatesStamped__FIELDS[] = {
  {
    {fsae_interfaces__msg__HardwareStatesStamped__FIELD_NAME__header, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {std_msgs__msg__Header__TYPE_NAME, 19, 19},
    },
    {NULL, 0, 0},
  },
  {
    {fsae_interfaces__msg__HardwareStatesStamped__FIELD_NAME__hardware_states, 15, 15},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {fsae_interfaces__msg__HardwareStates__TYPE_NAME, 34, 34},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription fsae_interfaces__msg__HardwareStatesStamped__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {builtin_interfaces__msg__Time__TYPE_NAME, 27, 27},
    {NULL, 0, 0},
  },
  {
    {fsae_interfaces__msg__HardwareStates__TYPE_NAME, 34, 34},
    {NULL, 0, 0},
  },
  {
    {std_msgs__msg__Header__TYPE_NAME, 19, 19},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
fsae_interfaces__msg__HardwareStatesStamped__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {fsae_interfaces__msg__HardwareStatesStamped__TYPE_NAME, 41, 41},
      {fsae_interfaces__msg__HardwareStatesStamped__FIELDS, 2, 2},
    },
    {fsae_interfaces__msg__HardwareStatesStamped__REFERENCED_TYPE_DESCRIPTIONS, 3, 3},
  };
  if (!constructed) {
    assert(0 == memcmp(&builtin_interfaces__msg__Time__EXPECTED_HASH, builtin_interfaces__msg__Time__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = builtin_interfaces__msg__Time__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&fsae_interfaces__msg__HardwareStates__EXPECTED_HASH, fsae_interfaces__msg__HardwareStates__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = fsae_interfaces__msg__HardwareStates__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__Header__EXPECTED_HASH, std_msgs__msg__Header__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[2].fields = std_msgs__msg__Header__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "std_msgs/Header header \n"
  "HardwareStates hardware_states ";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
fsae_interfaces__msg__HardwareStatesStamped__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {fsae_interfaces__msg__HardwareStatesStamped__TYPE_NAME, 41, 41},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 56, 56},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
fsae_interfaces__msg__HardwareStatesStamped__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[4];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 4, 4};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *fsae_interfaces__msg__HardwareStatesStamped__get_individual_type_description_source(NULL),
    sources[1] = *builtin_interfaces__msg__Time__get_individual_type_description_source(NULL);
    sources[2] = *fsae_interfaces__msg__HardwareStates__get_individual_type_description_source(NULL);
    sources[3] = *std_msgs__msg__Header__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}

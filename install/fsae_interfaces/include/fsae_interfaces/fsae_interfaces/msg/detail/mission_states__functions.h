// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from fsae_interfaces:msg/MissionStates.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/mission_states.h"


#ifndef FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES__FUNCTIONS_H_
#define FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/action_type_support_struct.h"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_runtime_c/service_type_support_struct.h"
#include "rosidl_runtime_c/type_description/type_description__struct.h"
#include "rosidl_runtime_c/type_description/type_source__struct.h"
#include "rosidl_runtime_c/type_hash.h"
#include "rosidl_runtime_c/visibility_control.h"
#include "fsae_interfaces/msg/rosidl_generator_c__visibility_control.h"

#include "fsae_interfaces/msg/detail/mission_states__struct.h"

/// Initialize msg/MissionStates message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * fsae_interfaces__msg__MissionStates
 * )) before or use
 * fsae_interfaces__msg__MissionStates__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_fsae_interfaces
bool
fsae_interfaces__msg__MissionStates__init(fsae_interfaces__msg__MissionStates * msg);

/// Finalize msg/MissionStates message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_fsae_interfaces
void
fsae_interfaces__msg__MissionStates__fini(fsae_interfaces__msg__MissionStates * msg);

/// Create msg/MissionStates message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * fsae_interfaces__msg__MissionStates__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_fsae_interfaces
fsae_interfaces__msg__MissionStates *
fsae_interfaces__msg__MissionStates__create(void);

/// Destroy msg/MissionStates message.
/**
 * It calls
 * fsae_interfaces__msg__MissionStates__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_fsae_interfaces
void
fsae_interfaces__msg__MissionStates__destroy(fsae_interfaces__msg__MissionStates * msg);

/// Check for msg/MissionStates message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_fsae_interfaces
bool
fsae_interfaces__msg__MissionStates__are_equal(const fsae_interfaces__msg__MissionStates * lhs, const fsae_interfaces__msg__MissionStates * rhs);

/// Copy a msg/MissionStates message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_fsae_interfaces
bool
fsae_interfaces__msg__MissionStates__copy(
  const fsae_interfaces__msg__MissionStates * input,
  fsae_interfaces__msg__MissionStates * output);

/// Retrieve pointer to the hash of the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_fsae_interfaces
const rosidl_type_hash_t *
fsae_interfaces__msg__MissionStates__get_type_hash(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_fsae_interfaces
const rosidl_runtime_c__type_description__TypeDescription *
fsae_interfaces__msg__MissionStates__get_type_description(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the single raw source text that defined this type.
ROSIDL_GENERATOR_C_PUBLIC_fsae_interfaces
const rosidl_runtime_c__type_description__TypeSource *
fsae_interfaces__msg__MissionStates__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the recursive raw sources that defined the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_fsae_interfaces
const rosidl_runtime_c__type_description__TypeSource__Sequence *
fsae_interfaces__msg__MissionStates__get_type_description_sources(
  const rosidl_message_type_support_t * type_support);

/// Initialize array of msg/MissionStates messages.
/**
 * It allocates the memory for the number of elements and calls
 * fsae_interfaces__msg__MissionStates__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_fsae_interfaces
bool
fsae_interfaces__msg__MissionStates__Sequence__init(fsae_interfaces__msg__MissionStates__Sequence * array, size_t size);

/// Finalize array of msg/MissionStates messages.
/**
 * It calls
 * fsae_interfaces__msg__MissionStates__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_fsae_interfaces
void
fsae_interfaces__msg__MissionStates__Sequence__fini(fsae_interfaces__msg__MissionStates__Sequence * array);

/// Create array of msg/MissionStates messages.
/**
 * It allocates the memory for the array and calls
 * fsae_interfaces__msg__MissionStates__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_fsae_interfaces
fsae_interfaces__msg__MissionStates__Sequence *
fsae_interfaces__msg__MissionStates__Sequence__create(size_t size);

/// Destroy array of msg/MissionStates messages.
/**
 * It calls
 * fsae_interfaces__msg__MissionStates__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_fsae_interfaces
void
fsae_interfaces__msg__MissionStates__Sequence__destroy(fsae_interfaces__msg__MissionStates__Sequence * array);

/// Check for msg/MissionStates message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_fsae_interfaces
bool
fsae_interfaces__msg__MissionStates__Sequence__are_equal(const fsae_interfaces__msg__MissionStates__Sequence * lhs, const fsae_interfaces__msg__MissionStates__Sequence * rhs);

/// Copy an array of msg/MissionStates messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_fsae_interfaces
bool
fsae_interfaces__msg__MissionStates__Sequence__copy(
  const fsae_interfaces__msg__MissionStates__Sequence * input,
  fsae_interfaces__msg__MissionStates__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES__FUNCTIONS_H_

// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from fsae_interfaces:msg/HardwareStatesStamped.idl
// generated code does not contain a copyright notice
#include "fsae_interfaces/msg/detail/hardware_states_stamped__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `hardware_states`
#include "fsae_interfaces/msg/detail/hardware_states__functions.h"

bool
fsae_interfaces__msg__HardwareStatesStamped__init(fsae_interfaces__msg__HardwareStatesStamped * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    fsae_interfaces__msg__HardwareStatesStamped__fini(msg);
    return false;
  }
  // hardware_states
  if (!fsae_interfaces__msg__HardwareStates__init(&msg->hardware_states)) {
    fsae_interfaces__msg__HardwareStatesStamped__fini(msg);
    return false;
  }
  return true;
}

void
fsae_interfaces__msg__HardwareStatesStamped__fini(fsae_interfaces__msg__HardwareStatesStamped * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // hardware_states
  fsae_interfaces__msg__HardwareStates__fini(&msg->hardware_states);
}

bool
fsae_interfaces__msg__HardwareStatesStamped__are_equal(const fsae_interfaces__msg__HardwareStatesStamped * lhs, const fsae_interfaces__msg__HardwareStatesStamped * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__are_equal(
      &(lhs->header), &(rhs->header)))
  {
    return false;
  }
  // hardware_states
  if (!fsae_interfaces__msg__HardwareStates__are_equal(
      &(lhs->hardware_states), &(rhs->hardware_states)))
  {
    return false;
  }
  return true;
}

bool
fsae_interfaces__msg__HardwareStatesStamped__copy(
  const fsae_interfaces__msg__HardwareStatesStamped * input,
  fsae_interfaces__msg__HardwareStatesStamped * output)
{
  if (!input || !output) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__copy(
      &(input->header), &(output->header)))
  {
    return false;
  }
  // hardware_states
  if (!fsae_interfaces__msg__HardwareStates__copy(
      &(input->hardware_states), &(output->hardware_states)))
  {
    return false;
  }
  return true;
}

fsae_interfaces__msg__HardwareStatesStamped *
fsae_interfaces__msg__HardwareStatesStamped__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fsae_interfaces__msg__HardwareStatesStamped * msg = (fsae_interfaces__msg__HardwareStatesStamped *)allocator.allocate(sizeof(fsae_interfaces__msg__HardwareStatesStamped), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(fsae_interfaces__msg__HardwareStatesStamped));
  bool success = fsae_interfaces__msg__HardwareStatesStamped__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
fsae_interfaces__msg__HardwareStatesStamped__destroy(fsae_interfaces__msg__HardwareStatesStamped * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    fsae_interfaces__msg__HardwareStatesStamped__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
fsae_interfaces__msg__HardwareStatesStamped__Sequence__init(fsae_interfaces__msg__HardwareStatesStamped__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fsae_interfaces__msg__HardwareStatesStamped * data = NULL;

  if (size) {
    data = (fsae_interfaces__msg__HardwareStatesStamped *)allocator.zero_allocate(size, sizeof(fsae_interfaces__msg__HardwareStatesStamped), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = fsae_interfaces__msg__HardwareStatesStamped__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        fsae_interfaces__msg__HardwareStatesStamped__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
fsae_interfaces__msg__HardwareStatesStamped__Sequence__fini(fsae_interfaces__msg__HardwareStatesStamped__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      fsae_interfaces__msg__HardwareStatesStamped__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

fsae_interfaces__msg__HardwareStatesStamped__Sequence *
fsae_interfaces__msg__HardwareStatesStamped__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fsae_interfaces__msg__HardwareStatesStamped__Sequence * array = (fsae_interfaces__msg__HardwareStatesStamped__Sequence *)allocator.allocate(sizeof(fsae_interfaces__msg__HardwareStatesStamped__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = fsae_interfaces__msg__HardwareStatesStamped__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
fsae_interfaces__msg__HardwareStatesStamped__Sequence__destroy(fsae_interfaces__msg__HardwareStatesStamped__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    fsae_interfaces__msg__HardwareStatesStamped__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
fsae_interfaces__msg__HardwareStatesStamped__Sequence__are_equal(const fsae_interfaces__msg__HardwareStatesStamped__Sequence * lhs, const fsae_interfaces__msg__HardwareStatesStamped__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!fsae_interfaces__msg__HardwareStatesStamped__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
fsae_interfaces__msg__HardwareStatesStamped__Sequence__copy(
  const fsae_interfaces__msg__HardwareStatesStamped__Sequence * input,
  fsae_interfaces__msg__HardwareStatesStamped__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(fsae_interfaces__msg__HardwareStatesStamped);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    fsae_interfaces__msg__HardwareStatesStamped * data =
      (fsae_interfaces__msg__HardwareStatesStamped *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!fsae_interfaces__msg__HardwareStatesStamped__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          fsae_interfaces__msg__HardwareStatesStamped__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!fsae_interfaces__msg__HardwareStatesStamped__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}

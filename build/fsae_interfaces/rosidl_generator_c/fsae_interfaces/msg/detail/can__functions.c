// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from fsae_interfaces:msg/CAN.idl
// generated code does not contain a copyright notice
#include "fsae_interfaces/msg/detail/can__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
fsae_interfaces__msg__CAN__init(fsae_interfaces__msg__CAN * msg)
{
  if (!msg) {
    return false;
  }
  // id
  // is_rtr
  msg->is_rtr = false;
  // data
  msg->data[0] = 0;
  msg->data[1] = 0;
  msg->data[2] = 0;
  msg->data[3] = 0;
  msg->data[4] = 0;
  msg->data[5] = 0;
  msg->data[6] = 0;
  msg->data[7] = 0;
  return true;
}

void
fsae_interfaces__msg__CAN__fini(fsae_interfaces__msg__CAN * msg)
{
  if (!msg) {
    return;
  }
  // id
  // is_rtr
  // data
}

bool
fsae_interfaces__msg__CAN__are_equal(const fsae_interfaces__msg__CAN * lhs, const fsae_interfaces__msg__CAN * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // id
  if (lhs->id != rhs->id) {
    return false;
  }
  // is_rtr
  if (lhs->is_rtr != rhs->is_rtr) {
    return false;
  }
  // data
  for (size_t i = 0; i < 8; ++i) {
    if (lhs->data[i] != rhs->data[i]) {
      return false;
    }
  }
  return true;
}

bool
fsae_interfaces__msg__CAN__copy(
  const fsae_interfaces__msg__CAN * input,
  fsae_interfaces__msg__CAN * output)
{
  if (!input || !output) {
    return false;
  }
  // id
  output->id = input->id;
  // is_rtr
  output->is_rtr = input->is_rtr;
  // data
  for (size_t i = 0; i < 8; ++i) {
    output->data[i] = input->data[i];
  }
  return true;
}

fsae_interfaces__msg__CAN *
fsae_interfaces__msg__CAN__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fsae_interfaces__msg__CAN * msg = (fsae_interfaces__msg__CAN *)allocator.allocate(sizeof(fsae_interfaces__msg__CAN), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(fsae_interfaces__msg__CAN));
  bool success = fsae_interfaces__msg__CAN__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
fsae_interfaces__msg__CAN__destroy(fsae_interfaces__msg__CAN * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    fsae_interfaces__msg__CAN__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
fsae_interfaces__msg__CAN__Sequence__init(fsae_interfaces__msg__CAN__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fsae_interfaces__msg__CAN * data = NULL;

  if (size) {
    data = (fsae_interfaces__msg__CAN *)allocator.zero_allocate(size, sizeof(fsae_interfaces__msg__CAN), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = fsae_interfaces__msg__CAN__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        fsae_interfaces__msg__CAN__fini(&data[i - 1]);
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
fsae_interfaces__msg__CAN__Sequence__fini(fsae_interfaces__msg__CAN__Sequence * array)
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
      fsae_interfaces__msg__CAN__fini(&array->data[i]);
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

fsae_interfaces__msg__CAN__Sequence *
fsae_interfaces__msg__CAN__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fsae_interfaces__msg__CAN__Sequence * array = (fsae_interfaces__msg__CAN__Sequence *)allocator.allocate(sizeof(fsae_interfaces__msg__CAN__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = fsae_interfaces__msg__CAN__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
fsae_interfaces__msg__CAN__Sequence__destroy(fsae_interfaces__msg__CAN__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    fsae_interfaces__msg__CAN__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
fsae_interfaces__msg__CAN__Sequence__are_equal(const fsae_interfaces__msg__CAN__Sequence * lhs, const fsae_interfaces__msg__CAN__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!fsae_interfaces__msg__CAN__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
fsae_interfaces__msg__CAN__Sequence__copy(
  const fsae_interfaces__msg__CAN__Sequence * input,
  fsae_interfaces__msg__CAN__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(fsae_interfaces__msg__CAN);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    fsae_interfaces__msg__CAN * data =
      (fsae_interfaces__msg__CAN *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!fsae_interfaces__msg__CAN__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          fsae_interfaces__msg__CAN__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!fsae_interfaces__msg__CAN__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}

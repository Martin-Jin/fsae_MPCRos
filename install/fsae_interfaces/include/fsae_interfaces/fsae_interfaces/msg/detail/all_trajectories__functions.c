// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from fsae_interfaces:msg/AllTrajectories.idl
// generated code does not contain a copyright notice
#include "fsae_interfaces/msg/detail/all_trajectories__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `trajectories`
#include "geometry_msgs/msg/detail/pose_array__functions.h"

bool
fsae_interfaces__msg__AllTrajectories__init(fsae_interfaces__msg__AllTrajectories * msg)
{
  if (!msg) {
    return false;
  }
  // id
  // trajectories
  if (!geometry_msgs__msg__PoseArray__Sequence__init(&msg->trajectories, 0)) {
    fsae_interfaces__msg__AllTrajectories__fini(msg);
    return false;
  }
  return true;
}

void
fsae_interfaces__msg__AllTrajectories__fini(fsae_interfaces__msg__AllTrajectories * msg)
{
  if (!msg) {
    return;
  }
  // id
  // trajectories
  geometry_msgs__msg__PoseArray__Sequence__fini(&msg->trajectories);
}

bool
fsae_interfaces__msg__AllTrajectories__are_equal(const fsae_interfaces__msg__AllTrajectories * lhs, const fsae_interfaces__msg__AllTrajectories * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // id
  if (lhs->id != rhs->id) {
    return false;
  }
  // trajectories
  if (!geometry_msgs__msg__PoseArray__Sequence__are_equal(
      &(lhs->trajectories), &(rhs->trajectories)))
  {
    return false;
  }
  return true;
}

bool
fsae_interfaces__msg__AllTrajectories__copy(
  const fsae_interfaces__msg__AllTrajectories * input,
  fsae_interfaces__msg__AllTrajectories * output)
{
  if (!input || !output) {
    return false;
  }
  // id
  output->id = input->id;
  // trajectories
  if (!geometry_msgs__msg__PoseArray__Sequence__copy(
      &(input->trajectories), &(output->trajectories)))
  {
    return false;
  }
  return true;
}

fsae_interfaces__msg__AllTrajectories *
fsae_interfaces__msg__AllTrajectories__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fsae_interfaces__msg__AllTrajectories * msg = (fsae_interfaces__msg__AllTrajectories *)allocator.allocate(sizeof(fsae_interfaces__msg__AllTrajectories), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(fsae_interfaces__msg__AllTrajectories));
  bool success = fsae_interfaces__msg__AllTrajectories__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
fsae_interfaces__msg__AllTrajectories__destroy(fsae_interfaces__msg__AllTrajectories * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    fsae_interfaces__msg__AllTrajectories__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
fsae_interfaces__msg__AllTrajectories__Sequence__init(fsae_interfaces__msg__AllTrajectories__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fsae_interfaces__msg__AllTrajectories * data = NULL;

  if (size) {
    data = (fsae_interfaces__msg__AllTrajectories *)allocator.zero_allocate(size, sizeof(fsae_interfaces__msg__AllTrajectories), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = fsae_interfaces__msg__AllTrajectories__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        fsae_interfaces__msg__AllTrajectories__fini(&data[i - 1]);
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
fsae_interfaces__msg__AllTrajectories__Sequence__fini(fsae_interfaces__msg__AllTrajectories__Sequence * array)
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
      fsae_interfaces__msg__AllTrajectories__fini(&array->data[i]);
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

fsae_interfaces__msg__AllTrajectories__Sequence *
fsae_interfaces__msg__AllTrajectories__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fsae_interfaces__msg__AllTrajectories__Sequence * array = (fsae_interfaces__msg__AllTrajectories__Sequence *)allocator.allocate(sizeof(fsae_interfaces__msg__AllTrajectories__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = fsae_interfaces__msg__AllTrajectories__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
fsae_interfaces__msg__AllTrajectories__Sequence__destroy(fsae_interfaces__msg__AllTrajectories__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    fsae_interfaces__msg__AllTrajectories__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
fsae_interfaces__msg__AllTrajectories__Sequence__are_equal(const fsae_interfaces__msg__AllTrajectories__Sequence * lhs, const fsae_interfaces__msg__AllTrajectories__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!fsae_interfaces__msg__AllTrajectories__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
fsae_interfaces__msg__AllTrajectories__Sequence__copy(
  const fsae_interfaces__msg__AllTrajectories__Sequence * input,
  fsae_interfaces__msg__AllTrajectories__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(fsae_interfaces__msg__AllTrajectories);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    fsae_interfaces__msg__AllTrajectories * data =
      (fsae_interfaces__msg__AllTrajectories *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!fsae_interfaces__msg__AllTrajectories__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          fsae_interfaces__msg__AllTrajectories__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!fsae_interfaces__msg__AllTrajectories__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}

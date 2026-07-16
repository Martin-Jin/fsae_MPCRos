// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from fsae_interfaces:msg/ConeDetection.idl
// generated code does not contain a copyright notice
#include "fsae_interfaces/msg/detail/cone_detection__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `car_pose`
#include "geometry_msgs/msg/detail/pose__functions.h"
// Member `yellow`
// Member `blue`
// Member `small_orange`
// Member `big_orange`
#include "geometry_msgs/msg/detail/point__functions.h"

bool
fsae_interfaces__msg__ConeDetection__init(fsae_interfaces__msg__ConeDetection * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    fsae_interfaces__msg__ConeDetection__fini(msg);
    return false;
  }
  // car_pose
  if (!geometry_msgs__msg__Pose__init(&msg->car_pose)) {
    fsae_interfaces__msg__ConeDetection__fini(msg);
    return false;
  }
  // yellow
  if (!geometry_msgs__msg__Point__Sequence__init(&msg->yellow, 0)) {
    fsae_interfaces__msg__ConeDetection__fini(msg);
    return false;
  }
  // blue
  if (!geometry_msgs__msg__Point__Sequence__init(&msg->blue, 0)) {
    fsae_interfaces__msg__ConeDetection__fini(msg);
    return false;
  }
  // small_orange
  if (!geometry_msgs__msg__Point__Sequence__init(&msg->small_orange, 0)) {
    fsae_interfaces__msg__ConeDetection__fini(msg);
    return false;
  }
  // big_orange
  if (!geometry_msgs__msg__Point__Sequence__init(&msg->big_orange, 0)) {
    fsae_interfaces__msg__ConeDetection__fini(msg);
    return false;
  }
  return true;
}

void
fsae_interfaces__msg__ConeDetection__fini(fsae_interfaces__msg__ConeDetection * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // car_pose
  geometry_msgs__msg__Pose__fini(&msg->car_pose);
  // yellow
  geometry_msgs__msg__Point__Sequence__fini(&msg->yellow);
  // blue
  geometry_msgs__msg__Point__Sequence__fini(&msg->blue);
  // small_orange
  geometry_msgs__msg__Point__Sequence__fini(&msg->small_orange);
  // big_orange
  geometry_msgs__msg__Point__Sequence__fini(&msg->big_orange);
}

bool
fsae_interfaces__msg__ConeDetection__are_equal(const fsae_interfaces__msg__ConeDetection * lhs, const fsae_interfaces__msg__ConeDetection * rhs)
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
  // car_pose
  if (!geometry_msgs__msg__Pose__are_equal(
      &(lhs->car_pose), &(rhs->car_pose)))
  {
    return false;
  }
  // yellow
  if (!geometry_msgs__msg__Point__Sequence__are_equal(
      &(lhs->yellow), &(rhs->yellow)))
  {
    return false;
  }
  // blue
  if (!geometry_msgs__msg__Point__Sequence__are_equal(
      &(lhs->blue), &(rhs->blue)))
  {
    return false;
  }
  // small_orange
  if (!geometry_msgs__msg__Point__Sequence__are_equal(
      &(lhs->small_orange), &(rhs->small_orange)))
  {
    return false;
  }
  // big_orange
  if (!geometry_msgs__msg__Point__Sequence__are_equal(
      &(lhs->big_orange), &(rhs->big_orange)))
  {
    return false;
  }
  return true;
}

bool
fsae_interfaces__msg__ConeDetection__copy(
  const fsae_interfaces__msg__ConeDetection * input,
  fsae_interfaces__msg__ConeDetection * output)
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
  // car_pose
  if (!geometry_msgs__msg__Pose__copy(
      &(input->car_pose), &(output->car_pose)))
  {
    return false;
  }
  // yellow
  if (!geometry_msgs__msg__Point__Sequence__copy(
      &(input->yellow), &(output->yellow)))
  {
    return false;
  }
  // blue
  if (!geometry_msgs__msg__Point__Sequence__copy(
      &(input->blue), &(output->blue)))
  {
    return false;
  }
  // small_orange
  if (!geometry_msgs__msg__Point__Sequence__copy(
      &(input->small_orange), &(output->small_orange)))
  {
    return false;
  }
  // big_orange
  if (!geometry_msgs__msg__Point__Sequence__copy(
      &(input->big_orange), &(output->big_orange)))
  {
    return false;
  }
  return true;
}

fsae_interfaces__msg__ConeDetection *
fsae_interfaces__msg__ConeDetection__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fsae_interfaces__msg__ConeDetection * msg = (fsae_interfaces__msg__ConeDetection *)allocator.allocate(sizeof(fsae_interfaces__msg__ConeDetection), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(fsae_interfaces__msg__ConeDetection));
  bool success = fsae_interfaces__msg__ConeDetection__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
fsae_interfaces__msg__ConeDetection__destroy(fsae_interfaces__msg__ConeDetection * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    fsae_interfaces__msg__ConeDetection__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
fsae_interfaces__msg__ConeDetection__Sequence__init(fsae_interfaces__msg__ConeDetection__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fsae_interfaces__msg__ConeDetection * data = NULL;

  if (size) {
    data = (fsae_interfaces__msg__ConeDetection *)allocator.zero_allocate(size, sizeof(fsae_interfaces__msg__ConeDetection), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = fsae_interfaces__msg__ConeDetection__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        fsae_interfaces__msg__ConeDetection__fini(&data[i - 1]);
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
fsae_interfaces__msg__ConeDetection__Sequence__fini(fsae_interfaces__msg__ConeDetection__Sequence * array)
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
      fsae_interfaces__msg__ConeDetection__fini(&array->data[i]);
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

fsae_interfaces__msg__ConeDetection__Sequence *
fsae_interfaces__msg__ConeDetection__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fsae_interfaces__msg__ConeDetection__Sequence * array = (fsae_interfaces__msg__ConeDetection__Sequence *)allocator.allocate(sizeof(fsae_interfaces__msg__ConeDetection__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = fsae_interfaces__msg__ConeDetection__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
fsae_interfaces__msg__ConeDetection__Sequence__destroy(fsae_interfaces__msg__ConeDetection__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    fsae_interfaces__msg__ConeDetection__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
fsae_interfaces__msg__ConeDetection__Sequence__are_equal(const fsae_interfaces__msg__ConeDetection__Sequence * lhs, const fsae_interfaces__msg__ConeDetection__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!fsae_interfaces__msg__ConeDetection__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
fsae_interfaces__msg__ConeDetection__Sequence__copy(
  const fsae_interfaces__msg__ConeDetection__Sequence * input,
  fsae_interfaces__msg__ConeDetection__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(fsae_interfaces__msg__ConeDetection);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    fsae_interfaces__msg__ConeDetection * data =
      (fsae_interfaces__msg__ConeDetection *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!fsae_interfaces__msg__ConeDetection__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          fsae_interfaces__msg__ConeDetection__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!fsae_interfaces__msg__ConeDetection__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}

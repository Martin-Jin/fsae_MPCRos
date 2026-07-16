// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from fsae_interfaces:msg/HardwareStates.idl
// generated code does not contain a copyright notice
#include "fsae_interfaces/msg/detail/hardware_states__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
fsae_interfaces__msg__HardwareStates__init(fsae_interfaces__msg__HardwareStates * msg)
{
  if (!msg) {
    return false;
  }
  // ebs_active
  // ts_active
  // in_gear
  // master_switch_on
  // asb_ready
  // brakes_engaged
  return true;
}

void
fsae_interfaces__msg__HardwareStates__fini(fsae_interfaces__msg__HardwareStates * msg)
{
  if (!msg) {
    return;
  }
  // ebs_active
  // ts_active
  // in_gear
  // master_switch_on
  // asb_ready
  // brakes_engaged
}

bool
fsae_interfaces__msg__HardwareStates__are_equal(const fsae_interfaces__msg__HardwareStates * lhs, const fsae_interfaces__msg__HardwareStates * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // ebs_active
  if (lhs->ebs_active != rhs->ebs_active) {
    return false;
  }
  // ts_active
  if (lhs->ts_active != rhs->ts_active) {
    return false;
  }
  // in_gear
  if (lhs->in_gear != rhs->in_gear) {
    return false;
  }
  // master_switch_on
  if (lhs->master_switch_on != rhs->master_switch_on) {
    return false;
  }
  // asb_ready
  if (lhs->asb_ready != rhs->asb_ready) {
    return false;
  }
  // brakes_engaged
  if (lhs->brakes_engaged != rhs->brakes_engaged) {
    return false;
  }
  return true;
}

bool
fsae_interfaces__msg__HardwareStates__copy(
  const fsae_interfaces__msg__HardwareStates * input,
  fsae_interfaces__msg__HardwareStates * output)
{
  if (!input || !output) {
    return false;
  }
  // ebs_active
  output->ebs_active = input->ebs_active;
  // ts_active
  output->ts_active = input->ts_active;
  // in_gear
  output->in_gear = input->in_gear;
  // master_switch_on
  output->master_switch_on = input->master_switch_on;
  // asb_ready
  output->asb_ready = input->asb_ready;
  // brakes_engaged
  output->brakes_engaged = input->brakes_engaged;
  return true;
}

fsae_interfaces__msg__HardwareStates *
fsae_interfaces__msg__HardwareStates__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fsae_interfaces__msg__HardwareStates * msg = (fsae_interfaces__msg__HardwareStates *)allocator.allocate(sizeof(fsae_interfaces__msg__HardwareStates), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(fsae_interfaces__msg__HardwareStates));
  bool success = fsae_interfaces__msg__HardwareStates__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
fsae_interfaces__msg__HardwareStates__destroy(fsae_interfaces__msg__HardwareStates * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    fsae_interfaces__msg__HardwareStates__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
fsae_interfaces__msg__HardwareStates__Sequence__init(fsae_interfaces__msg__HardwareStates__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fsae_interfaces__msg__HardwareStates * data = NULL;

  if (size) {
    data = (fsae_interfaces__msg__HardwareStates *)allocator.zero_allocate(size, sizeof(fsae_interfaces__msg__HardwareStates), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = fsae_interfaces__msg__HardwareStates__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        fsae_interfaces__msg__HardwareStates__fini(&data[i - 1]);
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
fsae_interfaces__msg__HardwareStates__Sequence__fini(fsae_interfaces__msg__HardwareStates__Sequence * array)
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
      fsae_interfaces__msg__HardwareStates__fini(&array->data[i]);
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

fsae_interfaces__msg__HardwareStates__Sequence *
fsae_interfaces__msg__HardwareStates__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fsae_interfaces__msg__HardwareStates__Sequence * array = (fsae_interfaces__msg__HardwareStates__Sequence *)allocator.allocate(sizeof(fsae_interfaces__msg__HardwareStates__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = fsae_interfaces__msg__HardwareStates__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
fsae_interfaces__msg__HardwareStates__Sequence__destroy(fsae_interfaces__msg__HardwareStates__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    fsae_interfaces__msg__HardwareStates__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
fsae_interfaces__msg__HardwareStates__Sequence__are_equal(const fsae_interfaces__msg__HardwareStates__Sequence * lhs, const fsae_interfaces__msg__HardwareStates__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!fsae_interfaces__msg__HardwareStates__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
fsae_interfaces__msg__HardwareStates__Sequence__copy(
  const fsae_interfaces__msg__HardwareStates__Sequence * input,
  fsae_interfaces__msg__HardwareStates__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(fsae_interfaces__msg__HardwareStates);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    fsae_interfaces__msg__HardwareStates * data =
      (fsae_interfaces__msg__HardwareStates *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!fsae_interfaces__msg__HardwareStates__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          fsae_interfaces__msg__HardwareStates__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!fsae_interfaces__msg__HardwareStates__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}

// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from fsae_interfaces:msg/HardwareStates.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/hardware_states.hpp"


#ifndef FSAE_INTERFACES__MSG__DETAIL__HARDWARE_STATES__STRUCT_HPP_
#define FSAE_INTERFACES__MSG__DETAIL__HARDWARE_STATES__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__fsae_interfaces__msg__HardwareStates __attribute__((deprecated))
#else
# define DEPRECATED__fsae_interfaces__msg__HardwareStates __declspec(deprecated)
#endif

namespace fsae_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct HardwareStates_
{
  using Type = HardwareStates_<ContainerAllocator>;

  explicit HardwareStates_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->ebs_active = 0;
      this->ts_active = 0;
      this->in_gear = 0;
      this->master_switch_on = 0;
      this->asb_ready = 0;
      this->brakes_engaged = 0;
    }
  }

  explicit HardwareStates_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->ebs_active = 0;
      this->ts_active = 0;
      this->in_gear = 0;
      this->master_switch_on = 0;
      this->asb_ready = 0;
      this->brakes_engaged = 0;
    }
  }

  // field types and members
  using _ebs_active_type =
    uint8_t;
  _ebs_active_type ebs_active;
  using _ts_active_type =
    uint8_t;
  _ts_active_type ts_active;
  using _in_gear_type =
    uint8_t;
  _in_gear_type in_gear;
  using _master_switch_on_type =
    uint8_t;
  _master_switch_on_type master_switch_on;
  using _asb_ready_type =
    uint8_t;
  _asb_ready_type asb_ready;
  using _brakes_engaged_type =
    uint8_t;
  _brakes_engaged_type brakes_engaged;

  // setters for named parameter idiom
  Type & set__ebs_active(
    const uint8_t & _arg)
  {
    this->ebs_active = _arg;
    return *this;
  }
  Type & set__ts_active(
    const uint8_t & _arg)
  {
    this->ts_active = _arg;
    return *this;
  }
  Type & set__in_gear(
    const uint8_t & _arg)
  {
    this->in_gear = _arg;
    return *this;
  }
  Type & set__master_switch_on(
    const uint8_t & _arg)
  {
    this->master_switch_on = _arg;
    return *this;
  }
  Type & set__asb_ready(
    const uint8_t & _arg)
  {
    this->asb_ready = _arg;
    return *this;
  }
  Type & set__brakes_engaged(
    const uint8_t & _arg)
  {
    this->brakes_engaged = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    fsae_interfaces::msg::HardwareStates_<ContainerAllocator> *;
  using ConstRawPtr =
    const fsae_interfaces::msg::HardwareStates_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<fsae_interfaces::msg::HardwareStates_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<fsae_interfaces::msg::HardwareStates_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      fsae_interfaces::msg::HardwareStates_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<fsae_interfaces::msg::HardwareStates_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      fsae_interfaces::msg::HardwareStates_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<fsae_interfaces::msg::HardwareStates_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<fsae_interfaces::msg::HardwareStates_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<fsae_interfaces::msg::HardwareStates_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__fsae_interfaces__msg__HardwareStates
    std::shared_ptr<fsae_interfaces::msg::HardwareStates_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__fsae_interfaces__msg__HardwareStates
    std::shared_ptr<fsae_interfaces::msg::HardwareStates_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const HardwareStates_ & other) const
  {
    if (this->ebs_active != other.ebs_active) {
      return false;
    }
    if (this->ts_active != other.ts_active) {
      return false;
    }
    if (this->in_gear != other.in_gear) {
      return false;
    }
    if (this->master_switch_on != other.master_switch_on) {
      return false;
    }
    if (this->asb_ready != other.asb_ready) {
      return false;
    }
    if (this->brakes_engaged != other.brakes_engaged) {
      return false;
    }
    return true;
  }
  bool operator!=(const HardwareStates_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct HardwareStates_

// alias to use template instance with default allocator
using HardwareStates =
  fsae_interfaces::msg::HardwareStates_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace fsae_interfaces

#endif  // FSAE_INTERFACES__MSG__DETAIL__HARDWARE_STATES__STRUCT_HPP_

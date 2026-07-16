// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from fsae_interfaces:msg/MissionStates.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/mission_states.hpp"


#ifndef FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES__STRUCT_HPP_
#define FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__fsae_interfaces__msg__MissionStates __attribute__((deprecated))
#else
# define DEPRECATED__fsae_interfaces__msg__MissionStates __declspec(deprecated)
#endif

namespace fsae_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct MissionStates_
{
  using Type = MissionStates_<ContainerAllocator>;

  explicit MissionStates_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->mission_selected = 0;
      this->mission_finished = 0;
    }
  }

  explicit MissionStates_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->mission_selected = 0;
      this->mission_finished = 0;
    }
  }

  // field types and members
  using _mission_selected_type =
    uint8_t;
  _mission_selected_type mission_selected;
  using _mission_finished_type =
    uint8_t;
  _mission_finished_type mission_finished;

  // setters for named parameter idiom
  Type & set__mission_selected(
    const uint8_t & _arg)
  {
    this->mission_selected = _arg;
    return *this;
  }
  Type & set__mission_finished(
    const uint8_t & _arg)
  {
    this->mission_finished = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    fsae_interfaces::msg::MissionStates_<ContainerAllocator> *;
  using ConstRawPtr =
    const fsae_interfaces::msg::MissionStates_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<fsae_interfaces::msg::MissionStates_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<fsae_interfaces::msg::MissionStates_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      fsae_interfaces::msg::MissionStates_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<fsae_interfaces::msg::MissionStates_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      fsae_interfaces::msg::MissionStates_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<fsae_interfaces::msg::MissionStates_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<fsae_interfaces::msg::MissionStates_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<fsae_interfaces::msg::MissionStates_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__fsae_interfaces__msg__MissionStates
    std::shared_ptr<fsae_interfaces::msg::MissionStates_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__fsae_interfaces__msg__MissionStates
    std::shared_ptr<fsae_interfaces::msg::MissionStates_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const MissionStates_ & other) const
  {
    if (this->mission_selected != other.mission_selected) {
      return false;
    }
    if (this->mission_finished != other.mission_finished) {
      return false;
    }
    return true;
  }
  bool operator!=(const MissionStates_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct MissionStates_

// alias to use template instance with default allocator
using MissionStates =
  fsae_interfaces::msg::MissionStates_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace fsae_interfaces

#endif  // FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES__STRUCT_HPP_

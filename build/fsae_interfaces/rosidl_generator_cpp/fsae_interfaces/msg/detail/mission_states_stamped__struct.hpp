// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from fsae_interfaces:msg/MissionStatesStamped.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/mission_states_stamped.hpp"


#ifndef FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES_STAMPED__STRUCT_HPP_
#define FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES_STAMPED__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.hpp"
// Member 'mission_states'
#include "fsae_interfaces/msg/detail/mission_states__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__fsae_interfaces__msg__MissionStatesStamped __attribute__((deprecated))
#else
# define DEPRECATED__fsae_interfaces__msg__MissionStatesStamped __declspec(deprecated)
#endif

namespace fsae_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct MissionStatesStamped_
{
  using Type = MissionStatesStamped_<ContainerAllocator>;

  explicit MissionStatesStamped_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init),
    mission_states(_init)
  {
    (void)_init;
  }

  explicit MissionStatesStamped_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init),
    mission_states(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _mission_states_type =
    fsae_interfaces::msg::MissionStates_<ContainerAllocator>;
  _mission_states_type mission_states;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__mission_states(
    const fsae_interfaces::msg::MissionStates_<ContainerAllocator> & _arg)
  {
    this->mission_states = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    fsae_interfaces::msg::MissionStatesStamped_<ContainerAllocator> *;
  using ConstRawPtr =
    const fsae_interfaces::msg::MissionStatesStamped_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<fsae_interfaces::msg::MissionStatesStamped_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<fsae_interfaces::msg::MissionStatesStamped_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      fsae_interfaces::msg::MissionStatesStamped_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<fsae_interfaces::msg::MissionStatesStamped_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      fsae_interfaces::msg::MissionStatesStamped_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<fsae_interfaces::msg::MissionStatesStamped_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<fsae_interfaces::msg::MissionStatesStamped_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<fsae_interfaces::msg::MissionStatesStamped_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__fsae_interfaces__msg__MissionStatesStamped
    std::shared_ptr<fsae_interfaces::msg::MissionStatesStamped_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__fsae_interfaces__msg__MissionStatesStamped
    std::shared_ptr<fsae_interfaces::msg::MissionStatesStamped_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const MissionStatesStamped_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->mission_states != other.mission_states) {
      return false;
    }
    return true;
  }
  bool operator!=(const MissionStatesStamped_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct MissionStatesStamped_

// alias to use template instance with default allocator
using MissionStatesStamped =
  fsae_interfaces::msg::MissionStatesStamped_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace fsae_interfaces

#endif  // FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES_STAMPED__STRUCT_HPP_

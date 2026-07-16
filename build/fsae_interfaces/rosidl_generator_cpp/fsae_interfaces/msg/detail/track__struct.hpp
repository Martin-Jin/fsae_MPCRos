// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from fsae_interfaces:msg/Track.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/track.hpp"


#ifndef FSAE_INTERFACES__MSG__DETAIL__TRACK__STRUCT_HPP_
#define FSAE_INTERFACES__MSG__DETAIL__TRACK__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'cones'
#include "geometry_msgs/msg/detail/point__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__fsae_interfaces__msg__Track __attribute__((deprecated))
#else
# define DEPRECATED__fsae_interfaces__msg__Track __declspec(deprecated)
#endif

namespace fsae_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Track_
{
  using Type = Track_<ContainerAllocator>;

  explicit Track_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_init;
  }

  explicit Track_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_init;
    (void)_alloc;
  }

  // field types and members
  using _cones_type =
    std::vector<geometry_msgs::msg::Point_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geometry_msgs::msg::Point_<ContainerAllocator>>>;
  _cones_type cones;

  // setters for named parameter idiom
  Type & set__cones(
    const std::vector<geometry_msgs::msg::Point_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geometry_msgs::msg::Point_<ContainerAllocator>>> & _arg)
  {
    this->cones = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    fsae_interfaces::msg::Track_<ContainerAllocator> *;
  using ConstRawPtr =
    const fsae_interfaces::msg::Track_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<fsae_interfaces::msg::Track_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<fsae_interfaces::msg::Track_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      fsae_interfaces::msg::Track_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<fsae_interfaces::msg::Track_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      fsae_interfaces::msg::Track_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<fsae_interfaces::msg::Track_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<fsae_interfaces::msg::Track_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<fsae_interfaces::msg::Track_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__fsae_interfaces__msg__Track
    std::shared_ptr<fsae_interfaces::msg::Track_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__fsae_interfaces__msg__Track
    std::shared_ptr<fsae_interfaces::msg::Track_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Track_ & other) const
  {
    if (this->cones != other.cones) {
      return false;
    }
    return true;
  }
  bool operator!=(const Track_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Track_

// alias to use template instance with default allocator
using Track =
  fsae_interfaces::msg::Track_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace fsae_interfaces

#endif  // FSAE_INTERFACES__MSG__DETAIL__TRACK__STRUCT_HPP_

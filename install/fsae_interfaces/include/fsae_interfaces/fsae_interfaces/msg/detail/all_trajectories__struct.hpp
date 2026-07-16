// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from fsae_interfaces:msg/AllTrajectories.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/all_trajectories.hpp"


#ifndef FSAE_INTERFACES__MSG__DETAIL__ALL_TRAJECTORIES__STRUCT_HPP_
#define FSAE_INTERFACES__MSG__DETAIL__ALL_TRAJECTORIES__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'trajectories'
#include "geometry_msgs/msg/detail/pose_array__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__fsae_interfaces__msg__AllTrajectories __attribute__((deprecated))
#else
# define DEPRECATED__fsae_interfaces__msg__AllTrajectories __declspec(deprecated)
#endif

namespace fsae_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct AllTrajectories_
{
  using Type = AllTrajectories_<ContainerAllocator>;

  explicit AllTrajectories_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->id = 0;
    }
  }

  explicit AllTrajectories_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->id = 0;
    }
  }

  // field types and members
  using _id_type =
    uint16_t;
  _id_type id;
  using _trajectories_type =
    std::vector<geometry_msgs::msg::PoseArray_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geometry_msgs::msg::PoseArray_<ContainerAllocator>>>;
  _trajectories_type trajectories;

  // setters for named parameter idiom
  Type & set__id(
    const uint16_t & _arg)
  {
    this->id = _arg;
    return *this;
  }
  Type & set__trajectories(
    const std::vector<geometry_msgs::msg::PoseArray_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geometry_msgs::msg::PoseArray_<ContainerAllocator>>> & _arg)
  {
    this->trajectories = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    fsae_interfaces::msg::AllTrajectories_<ContainerAllocator> *;
  using ConstRawPtr =
    const fsae_interfaces::msg::AllTrajectories_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<fsae_interfaces::msg::AllTrajectories_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<fsae_interfaces::msg::AllTrajectories_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      fsae_interfaces::msg::AllTrajectories_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<fsae_interfaces::msg::AllTrajectories_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      fsae_interfaces::msg::AllTrajectories_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<fsae_interfaces::msg::AllTrajectories_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<fsae_interfaces::msg::AllTrajectories_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<fsae_interfaces::msg::AllTrajectories_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__fsae_interfaces__msg__AllTrajectories
    std::shared_ptr<fsae_interfaces::msg::AllTrajectories_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__fsae_interfaces__msg__AllTrajectories
    std::shared_ptr<fsae_interfaces::msg::AllTrajectories_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const AllTrajectories_ & other) const
  {
    if (this->id != other.id) {
      return false;
    }
    if (this->trajectories != other.trajectories) {
      return false;
    }
    return true;
  }
  bool operator!=(const AllTrajectories_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct AllTrajectories_

// alias to use template instance with default allocator
using AllTrajectories =
  fsae_interfaces::msg::AllTrajectories_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace fsae_interfaces

#endif  // FSAE_INTERFACES__MSG__DETAIL__ALL_TRAJECTORIES__STRUCT_HPP_

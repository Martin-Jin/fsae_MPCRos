// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from fsae_interfaces:msg/ConeDetection.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/cone_detection.hpp"


#ifndef FSAE_INTERFACES__MSG__DETAIL__CONE_DETECTION__STRUCT_HPP_
#define FSAE_INTERFACES__MSG__DETAIL__CONE_DETECTION__STRUCT_HPP_

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
// Member 'car_pose'
#include "geometry_msgs/msg/detail/pose__struct.hpp"
// Member 'yellow'
// Member 'blue'
// Member 'small_orange'
// Member 'big_orange'
#include "geometry_msgs/msg/detail/point__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__fsae_interfaces__msg__ConeDetection __attribute__((deprecated))
#else
# define DEPRECATED__fsae_interfaces__msg__ConeDetection __declspec(deprecated)
#endif

namespace fsae_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct ConeDetection_
{
  using Type = ConeDetection_<ContainerAllocator>;

  explicit ConeDetection_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init),
    car_pose(_init)
  {
    (void)_init;
  }

  explicit ConeDetection_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init),
    car_pose(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _car_pose_type =
    geometry_msgs::msg::Pose_<ContainerAllocator>;
  _car_pose_type car_pose;
  using _yellow_type =
    std::vector<geometry_msgs::msg::Point_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geometry_msgs::msg::Point_<ContainerAllocator>>>;
  _yellow_type yellow;
  using _blue_type =
    std::vector<geometry_msgs::msg::Point_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geometry_msgs::msg::Point_<ContainerAllocator>>>;
  _blue_type blue;
  using _small_orange_type =
    std::vector<geometry_msgs::msg::Point_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geometry_msgs::msg::Point_<ContainerAllocator>>>;
  _small_orange_type small_orange;
  using _big_orange_type =
    std::vector<geometry_msgs::msg::Point_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geometry_msgs::msg::Point_<ContainerAllocator>>>;
  _big_orange_type big_orange;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__car_pose(
    const geometry_msgs::msg::Pose_<ContainerAllocator> & _arg)
  {
    this->car_pose = _arg;
    return *this;
  }
  Type & set__yellow(
    const std::vector<geometry_msgs::msg::Point_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geometry_msgs::msg::Point_<ContainerAllocator>>> & _arg)
  {
    this->yellow = _arg;
    return *this;
  }
  Type & set__blue(
    const std::vector<geometry_msgs::msg::Point_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geometry_msgs::msg::Point_<ContainerAllocator>>> & _arg)
  {
    this->blue = _arg;
    return *this;
  }
  Type & set__small_orange(
    const std::vector<geometry_msgs::msg::Point_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geometry_msgs::msg::Point_<ContainerAllocator>>> & _arg)
  {
    this->small_orange = _arg;
    return *this;
  }
  Type & set__big_orange(
    const std::vector<geometry_msgs::msg::Point_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geometry_msgs::msg::Point_<ContainerAllocator>>> & _arg)
  {
    this->big_orange = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    fsae_interfaces::msg::ConeDetection_<ContainerAllocator> *;
  using ConstRawPtr =
    const fsae_interfaces::msg::ConeDetection_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<fsae_interfaces::msg::ConeDetection_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<fsae_interfaces::msg::ConeDetection_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      fsae_interfaces::msg::ConeDetection_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<fsae_interfaces::msg::ConeDetection_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      fsae_interfaces::msg::ConeDetection_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<fsae_interfaces::msg::ConeDetection_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<fsae_interfaces::msg::ConeDetection_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<fsae_interfaces::msg::ConeDetection_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__fsae_interfaces__msg__ConeDetection
    std::shared_ptr<fsae_interfaces::msg::ConeDetection_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__fsae_interfaces__msg__ConeDetection
    std::shared_ptr<fsae_interfaces::msg::ConeDetection_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ConeDetection_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->car_pose != other.car_pose) {
      return false;
    }
    if (this->yellow != other.yellow) {
      return false;
    }
    if (this->blue != other.blue) {
      return false;
    }
    if (this->small_orange != other.small_orange) {
      return false;
    }
    if (this->big_orange != other.big_orange) {
      return false;
    }
    return true;
  }
  bool operator!=(const ConeDetection_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ConeDetection_

// alias to use template instance with default allocator
using ConeDetection =
  fsae_interfaces::msg::ConeDetection_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace fsae_interfaces

#endif  // FSAE_INTERFACES__MSG__DETAIL__CONE_DETECTION__STRUCT_HPP_

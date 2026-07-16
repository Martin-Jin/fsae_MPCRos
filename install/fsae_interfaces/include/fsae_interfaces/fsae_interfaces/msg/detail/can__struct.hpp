// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from fsae_interfaces:msg/CAN.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/can.hpp"


#ifndef FSAE_INTERFACES__MSG__DETAIL__CAN__STRUCT_HPP_
#define FSAE_INTERFACES__MSG__DETAIL__CAN__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__fsae_interfaces__msg__CAN __attribute__((deprecated))
#else
# define DEPRECATED__fsae_interfaces__msg__CAN __declspec(deprecated)
#endif

namespace fsae_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct CAN_
{
  using Type = CAN_<ContainerAllocator>;

  explicit CAN_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::DEFAULTS_ONLY == _init)
    {
      this->is_rtr = false;
      std::fill<typename std::array<uint8_t, 8>::iterator, uint8_t>(this->data.begin(), this->data.end(), 0);
    } else if (rosidl_runtime_cpp::MessageInitialization::ZERO == _init) {
      this->id = 0;
      this->is_rtr = false;
      std::fill<typename std::array<uint8_t, 8>::iterator, uint8_t>(this->data.begin(), this->data.end(), 0);
    }
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->id = 0;
    }
  }

  explicit CAN_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : data(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::DEFAULTS_ONLY == _init)
    {
      this->is_rtr = false;
      std::fill<typename std::array<uint8_t, 8>::iterator, uint8_t>(this->data.begin(), this->data.end(), 0);
    } else if (rosidl_runtime_cpp::MessageInitialization::ZERO == _init) {
      this->id = 0;
      this->is_rtr = false;
      std::fill<typename std::array<uint8_t, 8>::iterator, uint8_t>(this->data.begin(), this->data.end(), 0);
    }
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
  using _is_rtr_type =
    bool;
  _is_rtr_type is_rtr;
  using _data_type =
    std::array<uint8_t, 8>;
  _data_type data;

  // setters for named parameter idiom
  Type & set__id(
    const uint16_t & _arg)
  {
    this->id = _arg;
    return *this;
  }
  Type & set__is_rtr(
    const bool & _arg)
  {
    this->is_rtr = _arg;
    return *this;
  }
  Type & set__data(
    const std::array<uint8_t, 8> & _arg)
  {
    this->data = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    fsae_interfaces::msg::CAN_<ContainerAllocator> *;
  using ConstRawPtr =
    const fsae_interfaces::msg::CAN_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<fsae_interfaces::msg::CAN_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<fsae_interfaces::msg::CAN_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      fsae_interfaces::msg::CAN_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<fsae_interfaces::msg::CAN_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      fsae_interfaces::msg::CAN_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<fsae_interfaces::msg::CAN_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<fsae_interfaces::msg::CAN_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<fsae_interfaces::msg::CAN_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__fsae_interfaces__msg__CAN
    std::shared_ptr<fsae_interfaces::msg::CAN_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__fsae_interfaces__msg__CAN
    std::shared_ptr<fsae_interfaces::msg::CAN_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const CAN_ & other) const
  {
    if (this->id != other.id) {
      return false;
    }
    if (this->is_rtr != other.is_rtr) {
      return false;
    }
    if (this->data != other.data) {
      return false;
    }
    return true;
  }
  bool operator!=(const CAN_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct CAN_

// alias to use template instance with default allocator
using CAN =
  fsae_interfaces::msg::CAN_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace fsae_interfaces

#endif  // FSAE_INTERFACES__MSG__DETAIL__CAN__STRUCT_HPP_

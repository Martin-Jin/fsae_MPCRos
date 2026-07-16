// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from fsae_interfaces:msg/CANStamped.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/can_stamped.hpp"


#ifndef FSAE_INTERFACES__MSG__DETAIL__CAN_STAMPED__BUILDER_HPP_
#define FSAE_INTERFACES__MSG__DETAIL__CAN_STAMPED__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "fsae_interfaces/msg/detail/can_stamped__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace fsae_interfaces
{

namespace msg
{

namespace builder
{

class Init_CANStamped_can
{
public:
  explicit Init_CANStamped_can(::fsae_interfaces::msg::CANStamped & msg)
  : msg_(msg)
  {}
  ::fsae_interfaces::msg::CANStamped can(::fsae_interfaces::msg::CANStamped::_can_type arg)
  {
    msg_.can = std::move(arg);
    return std::move(msg_);
  }

private:
  ::fsae_interfaces::msg::CANStamped msg_;
};

class Init_CANStamped_header
{
public:
  Init_CANStamped_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_CANStamped_can header(::fsae_interfaces::msg::CANStamped::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_CANStamped_can(msg_);
  }

private:
  ::fsae_interfaces::msg::CANStamped msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::fsae_interfaces::msg::CANStamped>()
{
  return fsae_interfaces::msg::builder::Init_CANStamped_header();
}

}  // namespace fsae_interfaces

#endif  // FSAE_INTERFACES__MSG__DETAIL__CAN_STAMPED__BUILDER_HPP_

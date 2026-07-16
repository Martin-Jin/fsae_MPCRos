// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from fsae_interfaces:msg/CAN.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/can.hpp"


#ifndef FSAE_INTERFACES__MSG__DETAIL__CAN__BUILDER_HPP_
#define FSAE_INTERFACES__MSG__DETAIL__CAN__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "fsae_interfaces/msg/detail/can__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace fsae_interfaces
{

namespace msg
{

namespace builder
{

class Init_CAN_data
{
public:
  explicit Init_CAN_data(::fsae_interfaces::msg::CAN & msg)
  : msg_(msg)
  {}
  ::fsae_interfaces::msg::CAN data(::fsae_interfaces::msg::CAN::_data_type arg)
  {
    msg_.data = std::move(arg);
    return std::move(msg_);
  }

private:
  ::fsae_interfaces::msg::CAN msg_;
};

class Init_CAN_is_rtr
{
public:
  explicit Init_CAN_is_rtr(::fsae_interfaces::msg::CAN & msg)
  : msg_(msg)
  {}
  Init_CAN_data is_rtr(::fsae_interfaces::msg::CAN::_is_rtr_type arg)
  {
    msg_.is_rtr = std::move(arg);
    return Init_CAN_data(msg_);
  }

private:
  ::fsae_interfaces::msg::CAN msg_;
};

class Init_CAN_id
{
public:
  Init_CAN_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_CAN_is_rtr id(::fsae_interfaces::msg::CAN::_id_type arg)
  {
    msg_.id = std::move(arg);
    return Init_CAN_is_rtr(msg_);
  }

private:
  ::fsae_interfaces::msg::CAN msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::fsae_interfaces::msg::CAN>()
{
  return fsae_interfaces::msg::builder::Init_CAN_id();
}

}  // namespace fsae_interfaces

#endif  // FSAE_INTERFACES__MSG__DETAIL__CAN__BUILDER_HPP_

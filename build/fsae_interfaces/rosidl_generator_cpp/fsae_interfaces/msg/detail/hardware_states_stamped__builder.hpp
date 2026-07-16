// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from fsae_interfaces:msg/HardwareStatesStamped.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/hardware_states_stamped.hpp"


#ifndef FSAE_INTERFACES__MSG__DETAIL__HARDWARE_STATES_STAMPED__BUILDER_HPP_
#define FSAE_INTERFACES__MSG__DETAIL__HARDWARE_STATES_STAMPED__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "fsae_interfaces/msg/detail/hardware_states_stamped__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace fsae_interfaces
{

namespace msg
{

namespace builder
{

class Init_HardwareStatesStamped_hardware_states
{
public:
  explicit Init_HardwareStatesStamped_hardware_states(::fsae_interfaces::msg::HardwareStatesStamped & msg)
  : msg_(msg)
  {}
  ::fsae_interfaces::msg::HardwareStatesStamped hardware_states(::fsae_interfaces::msg::HardwareStatesStamped::_hardware_states_type arg)
  {
    msg_.hardware_states = std::move(arg);
    return std::move(msg_);
  }

private:
  ::fsae_interfaces::msg::HardwareStatesStamped msg_;
};

class Init_HardwareStatesStamped_header
{
public:
  Init_HardwareStatesStamped_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_HardwareStatesStamped_hardware_states header(::fsae_interfaces::msg::HardwareStatesStamped::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_HardwareStatesStamped_hardware_states(msg_);
  }

private:
  ::fsae_interfaces::msg::HardwareStatesStamped msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::fsae_interfaces::msg::HardwareStatesStamped>()
{
  return fsae_interfaces::msg::builder::Init_HardwareStatesStamped_header();
}

}  // namespace fsae_interfaces

#endif  // FSAE_INTERFACES__MSG__DETAIL__HARDWARE_STATES_STAMPED__BUILDER_HPP_

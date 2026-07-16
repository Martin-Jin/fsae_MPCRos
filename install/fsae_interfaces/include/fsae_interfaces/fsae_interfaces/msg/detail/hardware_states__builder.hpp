// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from fsae_interfaces:msg/HardwareStates.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/hardware_states.hpp"


#ifndef FSAE_INTERFACES__MSG__DETAIL__HARDWARE_STATES__BUILDER_HPP_
#define FSAE_INTERFACES__MSG__DETAIL__HARDWARE_STATES__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "fsae_interfaces/msg/detail/hardware_states__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace fsae_interfaces
{

namespace msg
{

namespace builder
{

class Init_HardwareStates_brakes_engaged
{
public:
  explicit Init_HardwareStates_brakes_engaged(::fsae_interfaces::msg::HardwareStates & msg)
  : msg_(msg)
  {}
  ::fsae_interfaces::msg::HardwareStates brakes_engaged(::fsae_interfaces::msg::HardwareStates::_brakes_engaged_type arg)
  {
    msg_.brakes_engaged = std::move(arg);
    return std::move(msg_);
  }

private:
  ::fsae_interfaces::msg::HardwareStates msg_;
};

class Init_HardwareStates_asb_ready
{
public:
  explicit Init_HardwareStates_asb_ready(::fsae_interfaces::msg::HardwareStates & msg)
  : msg_(msg)
  {}
  Init_HardwareStates_brakes_engaged asb_ready(::fsae_interfaces::msg::HardwareStates::_asb_ready_type arg)
  {
    msg_.asb_ready = std::move(arg);
    return Init_HardwareStates_brakes_engaged(msg_);
  }

private:
  ::fsae_interfaces::msg::HardwareStates msg_;
};

class Init_HardwareStates_master_switch_on
{
public:
  explicit Init_HardwareStates_master_switch_on(::fsae_interfaces::msg::HardwareStates & msg)
  : msg_(msg)
  {}
  Init_HardwareStates_asb_ready master_switch_on(::fsae_interfaces::msg::HardwareStates::_master_switch_on_type arg)
  {
    msg_.master_switch_on = std::move(arg);
    return Init_HardwareStates_asb_ready(msg_);
  }

private:
  ::fsae_interfaces::msg::HardwareStates msg_;
};

class Init_HardwareStates_in_gear
{
public:
  explicit Init_HardwareStates_in_gear(::fsae_interfaces::msg::HardwareStates & msg)
  : msg_(msg)
  {}
  Init_HardwareStates_master_switch_on in_gear(::fsae_interfaces::msg::HardwareStates::_in_gear_type arg)
  {
    msg_.in_gear = std::move(arg);
    return Init_HardwareStates_master_switch_on(msg_);
  }

private:
  ::fsae_interfaces::msg::HardwareStates msg_;
};

class Init_HardwareStates_ts_active
{
public:
  explicit Init_HardwareStates_ts_active(::fsae_interfaces::msg::HardwareStates & msg)
  : msg_(msg)
  {}
  Init_HardwareStates_in_gear ts_active(::fsae_interfaces::msg::HardwareStates::_ts_active_type arg)
  {
    msg_.ts_active = std::move(arg);
    return Init_HardwareStates_in_gear(msg_);
  }

private:
  ::fsae_interfaces::msg::HardwareStates msg_;
};

class Init_HardwareStates_ebs_active
{
public:
  Init_HardwareStates_ebs_active()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_HardwareStates_ts_active ebs_active(::fsae_interfaces::msg::HardwareStates::_ebs_active_type arg)
  {
    msg_.ebs_active = std::move(arg);
    return Init_HardwareStates_ts_active(msg_);
  }

private:
  ::fsae_interfaces::msg::HardwareStates msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::fsae_interfaces::msg::HardwareStates>()
{
  return fsae_interfaces::msg::builder::Init_HardwareStates_ebs_active();
}

}  // namespace fsae_interfaces

#endif  // FSAE_INTERFACES__MSG__DETAIL__HARDWARE_STATES__BUILDER_HPP_

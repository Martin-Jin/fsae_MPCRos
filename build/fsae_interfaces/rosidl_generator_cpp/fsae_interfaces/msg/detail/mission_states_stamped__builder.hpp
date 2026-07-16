// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from fsae_interfaces:msg/MissionStatesStamped.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/mission_states_stamped.hpp"


#ifndef FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES_STAMPED__BUILDER_HPP_
#define FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES_STAMPED__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "fsae_interfaces/msg/detail/mission_states_stamped__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace fsae_interfaces
{

namespace msg
{

namespace builder
{

class Init_MissionStatesStamped_mission_states
{
public:
  explicit Init_MissionStatesStamped_mission_states(::fsae_interfaces::msg::MissionStatesStamped & msg)
  : msg_(msg)
  {}
  ::fsae_interfaces::msg::MissionStatesStamped mission_states(::fsae_interfaces::msg::MissionStatesStamped::_mission_states_type arg)
  {
    msg_.mission_states = std::move(arg);
    return std::move(msg_);
  }

private:
  ::fsae_interfaces::msg::MissionStatesStamped msg_;
};

class Init_MissionStatesStamped_header
{
public:
  Init_MissionStatesStamped_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_MissionStatesStamped_mission_states header(::fsae_interfaces::msg::MissionStatesStamped::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_MissionStatesStamped_mission_states(msg_);
  }

private:
  ::fsae_interfaces::msg::MissionStatesStamped msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::fsae_interfaces::msg::MissionStatesStamped>()
{
  return fsae_interfaces::msg::builder::Init_MissionStatesStamped_header();
}

}  // namespace fsae_interfaces

#endif  // FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES_STAMPED__BUILDER_HPP_

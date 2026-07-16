// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from fsae_interfaces:msg/MissionStates.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/mission_states.hpp"


#ifndef FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES__BUILDER_HPP_
#define FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "fsae_interfaces/msg/detail/mission_states__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace fsae_interfaces
{

namespace msg
{

namespace builder
{

class Init_MissionStates_mission_finished
{
public:
  explicit Init_MissionStates_mission_finished(::fsae_interfaces::msg::MissionStates & msg)
  : msg_(msg)
  {}
  ::fsae_interfaces::msg::MissionStates mission_finished(::fsae_interfaces::msg::MissionStates::_mission_finished_type arg)
  {
    msg_.mission_finished = std::move(arg);
    return std::move(msg_);
  }

private:
  ::fsae_interfaces::msg::MissionStates msg_;
};

class Init_MissionStates_mission_selected
{
public:
  Init_MissionStates_mission_selected()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_MissionStates_mission_finished mission_selected(::fsae_interfaces::msg::MissionStates::_mission_selected_type arg)
  {
    msg_.mission_selected = std::move(arg);
    return Init_MissionStates_mission_finished(msg_);
  }

private:
  ::fsae_interfaces::msg::MissionStates msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::fsae_interfaces::msg::MissionStates>()
{
  return fsae_interfaces::msg::builder::Init_MissionStates_mission_selected();
}

}  // namespace fsae_interfaces

#endif  // FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES__BUILDER_HPP_

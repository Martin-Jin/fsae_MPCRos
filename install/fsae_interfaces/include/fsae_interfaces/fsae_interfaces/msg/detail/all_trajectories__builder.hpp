// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from fsae_interfaces:msg/AllTrajectories.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/all_trajectories.hpp"


#ifndef FSAE_INTERFACES__MSG__DETAIL__ALL_TRAJECTORIES__BUILDER_HPP_
#define FSAE_INTERFACES__MSG__DETAIL__ALL_TRAJECTORIES__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "fsae_interfaces/msg/detail/all_trajectories__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace fsae_interfaces
{

namespace msg
{

namespace builder
{

class Init_AllTrajectories_trajectories
{
public:
  explicit Init_AllTrajectories_trajectories(::fsae_interfaces::msg::AllTrajectories & msg)
  : msg_(msg)
  {}
  ::fsae_interfaces::msg::AllTrajectories trajectories(::fsae_interfaces::msg::AllTrajectories::_trajectories_type arg)
  {
    msg_.trajectories = std::move(arg);
    return std::move(msg_);
  }

private:
  ::fsae_interfaces::msg::AllTrajectories msg_;
};

class Init_AllTrajectories_id
{
public:
  Init_AllTrajectories_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_AllTrajectories_trajectories id(::fsae_interfaces::msg::AllTrajectories::_id_type arg)
  {
    msg_.id = std::move(arg);
    return Init_AllTrajectories_trajectories(msg_);
  }

private:
  ::fsae_interfaces::msg::AllTrajectories msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::fsae_interfaces::msg::AllTrajectories>()
{
  return fsae_interfaces::msg::builder::Init_AllTrajectories_id();
}

}  // namespace fsae_interfaces

#endif  // FSAE_INTERFACES__MSG__DETAIL__ALL_TRAJECTORIES__BUILDER_HPP_

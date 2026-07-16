// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from fsae_interfaces:msg/Track.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/track.hpp"


#ifndef FSAE_INTERFACES__MSG__DETAIL__TRACK__BUILDER_HPP_
#define FSAE_INTERFACES__MSG__DETAIL__TRACK__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "fsae_interfaces/msg/detail/track__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace fsae_interfaces
{

namespace msg
{

namespace builder
{

class Init_Track_cones
{
public:
  Init_Track_cones()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::fsae_interfaces::msg::Track cones(::fsae_interfaces::msg::Track::_cones_type arg)
  {
    msg_.cones = std::move(arg);
    return std::move(msg_);
  }

private:
  ::fsae_interfaces::msg::Track msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::fsae_interfaces::msg::Track>()
{
  return fsae_interfaces::msg::builder::Init_Track_cones();
}

}  // namespace fsae_interfaces

#endif  // FSAE_INTERFACES__MSG__DETAIL__TRACK__BUILDER_HPP_

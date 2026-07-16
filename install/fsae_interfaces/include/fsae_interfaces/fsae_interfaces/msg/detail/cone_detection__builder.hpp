// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from fsae_interfaces:msg/ConeDetection.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/cone_detection.hpp"


#ifndef FSAE_INTERFACES__MSG__DETAIL__CONE_DETECTION__BUILDER_HPP_
#define FSAE_INTERFACES__MSG__DETAIL__CONE_DETECTION__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "fsae_interfaces/msg/detail/cone_detection__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace fsae_interfaces
{

namespace msg
{

namespace builder
{

class Init_ConeDetection_big_orange
{
public:
  explicit Init_ConeDetection_big_orange(::fsae_interfaces::msg::ConeDetection & msg)
  : msg_(msg)
  {}
  ::fsae_interfaces::msg::ConeDetection big_orange(::fsae_interfaces::msg::ConeDetection::_big_orange_type arg)
  {
    msg_.big_orange = std::move(arg);
    return std::move(msg_);
  }

private:
  ::fsae_interfaces::msg::ConeDetection msg_;
};

class Init_ConeDetection_small_orange
{
public:
  explicit Init_ConeDetection_small_orange(::fsae_interfaces::msg::ConeDetection & msg)
  : msg_(msg)
  {}
  Init_ConeDetection_big_orange small_orange(::fsae_interfaces::msg::ConeDetection::_small_orange_type arg)
  {
    msg_.small_orange = std::move(arg);
    return Init_ConeDetection_big_orange(msg_);
  }

private:
  ::fsae_interfaces::msg::ConeDetection msg_;
};

class Init_ConeDetection_blue
{
public:
  explicit Init_ConeDetection_blue(::fsae_interfaces::msg::ConeDetection & msg)
  : msg_(msg)
  {}
  Init_ConeDetection_small_orange blue(::fsae_interfaces::msg::ConeDetection::_blue_type arg)
  {
    msg_.blue = std::move(arg);
    return Init_ConeDetection_small_orange(msg_);
  }

private:
  ::fsae_interfaces::msg::ConeDetection msg_;
};

class Init_ConeDetection_yellow
{
public:
  explicit Init_ConeDetection_yellow(::fsae_interfaces::msg::ConeDetection & msg)
  : msg_(msg)
  {}
  Init_ConeDetection_blue yellow(::fsae_interfaces::msg::ConeDetection::_yellow_type arg)
  {
    msg_.yellow = std::move(arg);
    return Init_ConeDetection_blue(msg_);
  }

private:
  ::fsae_interfaces::msg::ConeDetection msg_;
};

class Init_ConeDetection_car_pose
{
public:
  explicit Init_ConeDetection_car_pose(::fsae_interfaces::msg::ConeDetection & msg)
  : msg_(msg)
  {}
  Init_ConeDetection_yellow car_pose(::fsae_interfaces::msg::ConeDetection::_car_pose_type arg)
  {
    msg_.car_pose = std::move(arg);
    return Init_ConeDetection_yellow(msg_);
  }

private:
  ::fsae_interfaces::msg::ConeDetection msg_;
};

class Init_ConeDetection_header
{
public:
  Init_ConeDetection_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ConeDetection_car_pose header(::fsae_interfaces::msg::ConeDetection::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_ConeDetection_car_pose(msg_);
  }

private:
  ::fsae_interfaces::msg::ConeDetection msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::fsae_interfaces::msg::ConeDetection>()
{
  return fsae_interfaces::msg::builder::Init_ConeDetection_header();
}

}  // namespace fsae_interfaces

#endif  // FSAE_INTERFACES__MSG__DETAIL__CONE_DETECTION__BUILDER_HPP_

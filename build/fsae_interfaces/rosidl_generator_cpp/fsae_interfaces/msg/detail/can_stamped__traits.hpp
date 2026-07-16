// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from fsae_interfaces:msg/CANStamped.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/can_stamped.hpp"


#ifndef FSAE_INTERFACES__MSG__DETAIL__CAN_STAMPED__TRAITS_HPP_
#define FSAE_INTERFACES__MSG__DETAIL__CAN_STAMPED__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "fsae_interfaces/msg/detail/can_stamped__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"
// Member 'can'
#include "fsae_interfaces/msg/detail/can__traits.hpp"

namespace fsae_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const CANStamped & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: can
  {
    out << "can: ";
    to_flow_style_yaml(msg.can, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const CANStamped & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "header:\n";
    to_block_style_yaml(msg.header, out, indentation + 2);
  }

  // member: can
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "can:\n";
    to_block_style_yaml(msg.can, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const CANStamped & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace fsae_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use fsae_interfaces::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const fsae_interfaces::msg::CANStamped & msg,
  std::ostream & out, size_t indentation = 0)
{
  fsae_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use fsae_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const fsae_interfaces::msg::CANStamped & msg)
{
  return fsae_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<fsae_interfaces::msg::CANStamped>()
{
  return "fsae_interfaces::msg::CANStamped";
}

template<>
inline const char * name<fsae_interfaces::msg::CANStamped>()
{
  return "fsae_interfaces/msg/CANStamped";
}

template<>
struct has_fixed_size<fsae_interfaces::msg::CANStamped>
  : std::integral_constant<bool, has_fixed_size<fsae_interfaces::msg::CAN>::value && has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<fsae_interfaces::msg::CANStamped>
  : std::integral_constant<bool, has_bounded_size<fsae_interfaces::msg::CAN>::value && has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<fsae_interfaces::msg::CANStamped>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // FSAE_INTERFACES__MSG__DETAIL__CAN_STAMPED__TRAITS_HPP_

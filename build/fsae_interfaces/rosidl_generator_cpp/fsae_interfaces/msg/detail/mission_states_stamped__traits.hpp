// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from fsae_interfaces:msg/MissionStatesStamped.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/mission_states_stamped.hpp"


#ifndef FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES_STAMPED__TRAITS_HPP_
#define FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES_STAMPED__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "fsae_interfaces/msg/detail/mission_states_stamped__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"
// Member 'mission_states'
#include "fsae_interfaces/msg/detail/mission_states__traits.hpp"

namespace fsae_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const MissionStatesStamped & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: mission_states
  {
    out << "mission_states: ";
    to_flow_style_yaml(msg.mission_states, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const MissionStatesStamped & msg,
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

  // member: mission_states
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "mission_states:\n";
    to_block_style_yaml(msg.mission_states, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const MissionStatesStamped & msg, bool use_flow_style = false)
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
  const fsae_interfaces::msg::MissionStatesStamped & msg,
  std::ostream & out, size_t indentation = 0)
{
  fsae_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use fsae_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const fsae_interfaces::msg::MissionStatesStamped & msg)
{
  return fsae_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<fsae_interfaces::msg::MissionStatesStamped>()
{
  return "fsae_interfaces::msg::MissionStatesStamped";
}

template<>
inline const char * name<fsae_interfaces::msg::MissionStatesStamped>()
{
  return "fsae_interfaces/msg/MissionStatesStamped";
}

template<>
struct has_fixed_size<fsae_interfaces::msg::MissionStatesStamped>
  : std::integral_constant<bool, has_fixed_size<fsae_interfaces::msg::MissionStates>::value && has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<fsae_interfaces::msg::MissionStatesStamped>
  : std::integral_constant<bool, has_bounded_size<fsae_interfaces::msg::MissionStates>::value && has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<fsae_interfaces::msg::MissionStatesStamped>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES_STAMPED__TRAITS_HPP_

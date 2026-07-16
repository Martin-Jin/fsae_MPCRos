// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from fsae_interfaces:msg/MissionStates.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/mission_states.hpp"


#ifndef FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES__TRAITS_HPP_
#define FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "fsae_interfaces/msg/detail/mission_states__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace fsae_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const MissionStates & msg,
  std::ostream & out)
{
  out << "{";
  // member: mission_selected
  {
    out << "mission_selected: ";
    rosidl_generator_traits::value_to_yaml(msg.mission_selected, out);
    out << ", ";
  }

  // member: mission_finished
  {
    out << "mission_finished: ";
    rosidl_generator_traits::value_to_yaml(msg.mission_finished, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const MissionStates & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: mission_selected
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "mission_selected: ";
    rosidl_generator_traits::value_to_yaml(msg.mission_selected, out);
    out << "\n";
  }

  // member: mission_finished
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "mission_finished: ";
    rosidl_generator_traits::value_to_yaml(msg.mission_finished, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const MissionStates & msg, bool use_flow_style = false)
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
  const fsae_interfaces::msg::MissionStates & msg,
  std::ostream & out, size_t indentation = 0)
{
  fsae_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use fsae_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const fsae_interfaces::msg::MissionStates & msg)
{
  return fsae_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<fsae_interfaces::msg::MissionStates>()
{
  return "fsae_interfaces::msg::MissionStates";
}

template<>
inline const char * name<fsae_interfaces::msg::MissionStates>()
{
  return "fsae_interfaces/msg/MissionStates";
}

template<>
struct has_fixed_size<fsae_interfaces::msg::MissionStates>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<fsae_interfaces::msg::MissionStates>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<fsae_interfaces::msg::MissionStates>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // FSAE_INTERFACES__MSG__DETAIL__MISSION_STATES__TRAITS_HPP_

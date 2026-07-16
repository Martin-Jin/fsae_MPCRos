// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from fsae_interfaces:msg/HardwareStates.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/hardware_states.hpp"


#ifndef FSAE_INTERFACES__MSG__DETAIL__HARDWARE_STATES__TRAITS_HPP_
#define FSAE_INTERFACES__MSG__DETAIL__HARDWARE_STATES__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "fsae_interfaces/msg/detail/hardware_states__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace fsae_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const HardwareStates & msg,
  std::ostream & out)
{
  out << "{";
  // member: ebs_active
  {
    out << "ebs_active: ";
    rosidl_generator_traits::value_to_yaml(msg.ebs_active, out);
    out << ", ";
  }

  // member: ts_active
  {
    out << "ts_active: ";
    rosidl_generator_traits::value_to_yaml(msg.ts_active, out);
    out << ", ";
  }

  // member: in_gear
  {
    out << "in_gear: ";
    rosidl_generator_traits::value_to_yaml(msg.in_gear, out);
    out << ", ";
  }

  // member: master_switch_on
  {
    out << "master_switch_on: ";
    rosidl_generator_traits::value_to_yaml(msg.master_switch_on, out);
    out << ", ";
  }

  // member: asb_ready
  {
    out << "asb_ready: ";
    rosidl_generator_traits::value_to_yaml(msg.asb_ready, out);
    out << ", ";
  }

  // member: brakes_engaged
  {
    out << "brakes_engaged: ";
    rosidl_generator_traits::value_to_yaml(msg.brakes_engaged, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const HardwareStates & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: ebs_active
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "ebs_active: ";
    rosidl_generator_traits::value_to_yaml(msg.ebs_active, out);
    out << "\n";
  }

  // member: ts_active
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "ts_active: ";
    rosidl_generator_traits::value_to_yaml(msg.ts_active, out);
    out << "\n";
  }

  // member: in_gear
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "in_gear: ";
    rosidl_generator_traits::value_to_yaml(msg.in_gear, out);
    out << "\n";
  }

  // member: master_switch_on
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "master_switch_on: ";
    rosidl_generator_traits::value_to_yaml(msg.master_switch_on, out);
    out << "\n";
  }

  // member: asb_ready
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "asb_ready: ";
    rosidl_generator_traits::value_to_yaml(msg.asb_ready, out);
    out << "\n";
  }

  // member: brakes_engaged
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "brakes_engaged: ";
    rosidl_generator_traits::value_to_yaml(msg.brakes_engaged, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const HardwareStates & msg, bool use_flow_style = false)
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
  const fsae_interfaces::msg::HardwareStates & msg,
  std::ostream & out, size_t indentation = 0)
{
  fsae_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use fsae_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const fsae_interfaces::msg::HardwareStates & msg)
{
  return fsae_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<fsae_interfaces::msg::HardwareStates>()
{
  return "fsae_interfaces::msg::HardwareStates";
}

template<>
inline const char * name<fsae_interfaces::msg::HardwareStates>()
{
  return "fsae_interfaces/msg/HardwareStates";
}

template<>
struct has_fixed_size<fsae_interfaces::msg::HardwareStates>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<fsae_interfaces::msg::HardwareStates>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<fsae_interfaces::msg::HardwareStates>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // FSAE_INTERFACES__MSG__DETAIL__HARDWARE_STATES__TRAITS_HPP_

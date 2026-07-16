// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from fsae_interfaces:msg/CAN.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/can.hpp"


#ifndef FSAE_INTERFACES__MSG__DETAIL__CAN__TRAITS_HPP_
#define FSAE_INTERFACES__MSG__DETAIL__CAN__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "fsae_interfaces/msg/detail/can__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace fsae_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const CAN & msg,
  std::ostream & out)
{
  out << "{";
  // member: id
  {
    out << "id: ";
    rosidl_generator_traits::value_to_yaml(msg.id, out);
    out << ", ";
  }

  // member: is_rtr
  {
    out << "is_rtr: ";
    rosidl_generator_traits::value_to_yaml(msg.is_rtr, out);
    out << ", ";
  }

  // member: data
  {
    if (msg.data.size() == 0) {
      out << "data: []";
    } else {
      out << "data: [";
      size_t pending_items = msg.data.size();
      for (auto item : msg.data) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const CAN & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "id: ";
    rosidl_generator_traits::value_to_yaml(msg.id, out);
    out << "\n";
  }

  // member: is_rtr
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "is_rtr: ";
    rosidl_generator_traits::value_to_yaml(msg.is_rtr, out);
    out << "\n";
  }

  // member: data
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.data.size() == 0) {
      out << "data: []\n";
    } else {
      out << "data:\n";
      for (auto item : msg.data) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const CAN & msg, bool use_flow_style = false)
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
  const fsae_interfaces::msg::CAN & msg,
  std::ostream & out, size_t indentation = 0)
{
  fsae_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use fsae_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const fsae_interfaces::msg::CAN & msg)
{
  return fsae_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<fsae_interfaces::msg::CAN>()
{
  return "fsae_interfaces::msg::CAN";
}

template<>
inline const char * name<fsae_interfaces::msg::CAN>()
{
  return "fsae_interfaces/msg/CAN";
}

template<>
struct has_fixed_size<fsae_interfaces::msg::CAN>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<fsae_interfaces::msg::CAN>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<fsae_interfaces::msg::CAN>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // FSAE_INTERFACES__MSG__DETAIL__CAN__TRAITS_HPP_

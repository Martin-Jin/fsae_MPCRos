// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from fsae_interfaces:msg/Track.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/track.hpp"


#ifndef FSAE_INTERFACES__MSG__DETAIL__TRACK__TRAITS_HPP_
#define FSAE_INTERFACES__MSG__DETAIL__TRACK__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "fsae_interfaces/msg/detail/track__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'cones'
#include "geometry_msgs/msg/detail/point__traits.hpp"

namespace fsae_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const Track & msg,
  std::ostream & out)
{
  out << "{";
  // member: cones
  {
    if (msg.cones.size() == 0) {
      out << "cones: []";
    } else {
      out << "cones: [";
      size_t pending_items = msg.cones.size();
      for (auto item : msg.cones) {
        to_flow_style_yaml(item, out);
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
  const Track & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: cones
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.cones.size() == 0) {
      out << "cones: []\n";
    } else {
      out << "cones:\n";
      for (auto item : msg.cones) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Track & msg, bool use_flow_style = false)
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
  const fsae_interfaces::msg::Track & msg,
  std::ostream & out, size_t indentation = 0)
{
  fsae_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use fsae_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const fsae_interfaces::msg::Track & msg)
{
  return fsae_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<fsae_interfaces::msg::Track>()
{
  return "fsae_interfaces::msg::Track";
}

template<>
inline const char * name<fsae_interfaces::msg::Track>()
{
  return "fsae_interfaces/msg/Track";
}

template<>
struct has_fixed_size<fsae_interfaces::msg::Track>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<fsae_interfaces::msg::Track>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<fsae_interfaces::msg::Track>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // FSAE_INTERFACES__MSG__DETAIL__TRACK__TRAITS_HPP_

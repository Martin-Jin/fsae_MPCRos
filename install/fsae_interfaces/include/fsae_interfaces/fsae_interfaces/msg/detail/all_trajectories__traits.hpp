// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from fsae_interfaces:msg/AllTrajectories.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/all_trajectories.hpp"


#ifndef FSAE_INTERFACES__MSG__DETAIL__ALL_TRAJECTORIES__TRAITS_HPP_
#define FSAE_INTERFACES__MSG__DETAIL__ALL_TRAJECTORIES__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "fsae_interfaces/msg/detail/all_trajectories__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'trajectories'
#include "geometry_msgs/msg/detail/pose_array__traits.hpp"

namespace fsae_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const AllTrajectories & msg,
  std::ostream & out)
{
  out << "{";
  // member: id
  {
    out << "id: ";
    rosidl_generator_traits::value_to_yaml(msg.id, out);
    out << ", ";
  }

  // member: trajectories
  {
    if (msg.trajectories.size() == 0) {
      out << "trajectories: []";
    } else {
      out << "trajectories: [";
      size_t pending_items = msg.trajectories.size();
      for (auto item : msg.trajectories) {
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
  const AllTrajectories & msg,
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

  // member: trajectories
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.trajectories.size() == 0) {
      out << "trajectories: []\n";
    } else {
      out << "trajectories:\n";
      for (auto item : msg.trajectories) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const AllTrajectories & msg, bool use_flow_style = false)
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
  const fsae_interfaces::msg::AllTrajectories & msg,
  std::ostream & out, size_t indentation = 0)
{
  fsae_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use fsae_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const fsae_interfaces::msg::AllTrajectories & msg)
{
  return fsae_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<fsae_interfaces::msg::AllTrajectories>()
{
  return "fsae_interfaces::msg::AllTrajectories";
}

template<>
inline const char * name<fsae_interfaces::msg::AllTrajectories>()
{
  return "fsae_interfaces/msg/AllTrajectories";
}

template<>
struct has_fixed_size<fsae_interfaces::msg::AllTrajectories>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<fsae_interfaces::msg::AllTrajectories>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<fsae_interfaces::msg::AllTrajectories>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // FSAE_INTERFACES__MSG__DETAIL__ALL_TRAJECTORIES__TRAITS_HPP_

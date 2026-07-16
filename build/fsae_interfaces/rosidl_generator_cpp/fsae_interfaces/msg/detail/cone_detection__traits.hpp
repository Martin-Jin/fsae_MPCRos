// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from fsae_interfaces:msg/ConeDetection.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fsae_interfaces/msg/cone_detection.hpp"


#ifndef FSAE_INTERFACES__MSG__DETAIL__CONE_DETECTION__TRAITS_HPP_
#define FSAE_INTERFACES__MSG__DETAIL__CONE_DETECTION__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "fsae_interfaces/msg/detail/cone_detection__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"
// Member 'car_pose'
#include "geometry_msgs/msg/detail/pose__traits.hpp"
// Member 'yellow'
// Member 'blue'
// Member 'small_orange'
// Member 'big_orange'
#include "geometry_msgs/msg/detail/point__traits.hpp"

namespace fsae_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const ConeDetection & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: car_pose
  {
    out << "car_pose: ";
    to_flow_style_yaml(msg.car_pose, out);
    out << ", ";
  }

  // member: yellow
  {
    if (msg.yellow.size() == 0) {
      out << "yellow: []";
    } else {
      out << "yellow: [";
      size_t pending_items = msg.yellow.size();
      for (auto item : msg.yellow) {
        to_flow_style_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: blue
  {
    if (msg.blue.size() == 0) {
      out << "blue: []";
    } else {
      out << "blue: [";
      size_t pending_items = msg.blue.size();
      for (auto item : msg.blue) {
        to_flow_style_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: small_orange
  {
    if (msg.small_orange.size() == 0) {
      out << "small_orange: []";
    } else {
      out << "small_orange: [";
      size_t pending_items = msg.small_orange.size();
      for (auto item : msg.small_orange) {
        to_flow_style_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: big_orange
  {
    if (msg.big_orange.size() == 0) {
      out << "big_orange: []";
    } else {
      out << "big_orange: [";
      size_t pending_items = msg.big_orange.size();
      for (auto item : msg.big_orange) {
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
  const ConeDetection & msg,
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

  // member: car_pose
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "car_pose:\n";
    to_block_style_yaml(msg.car_pose, out, indentation + 2);
  }

  // member: yellow
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.yellow.size() == 0) {
      out << "yellow: []\n";
    } else {
      out << "yellow:\n";
      for (auto item : msg.yellow) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }

  // member: blue
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.blue.size() == 0) {
      out << "blue: []\n";
    } else {
      out << "blue:\n";
      for (auto item : msg.blue) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }

  // member: small_orange
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.small_orange.size() == 0) {
      out << "small_orange: []\n";
    } else {
      out << "small_orange:\n";
      for (auto item : msg.small_orange) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }

  // member: big_orange
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.big_orange.size() == 0) {
      out << "big_orange: []\n";
    } else {
      out << "big_orange:\n";
      for (auto item : msg.big_orange) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ConeDetection & msg, bool use_flow_style = false)
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
  const fsae_interfaces::msg::ConeDetection & msg,
  std::ostream & out, size_t indentation = 0)
{
  fsae_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use fsae_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const fsae_interfaces::msg::ConeDetection & msg)
{
  return fsae_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<fsae_interfaces::msg::ConeDetection>()
{
  return "fsae_interfaces::msg::ConeDetection";
}

template<>
inline const char * name<fsae_interfaces::msg::ConeDetection>()
{
  return "fsae_interfaces/msg/ConeDetection";
}

template<>
struct has_fixed_size<fsae_interfaces::msg::ConeDetection>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<fsae_interfaces::msg::ConeDetection>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<fsae_interfaces::msg::ConeDetection>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // FSAE_INTERFACES__MSG__DETAIL__CONE_DETECTION__TRAITS_HPP_

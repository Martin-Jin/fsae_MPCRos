#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "fsae_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__fsae_interfaces__msg__AllTrajectories() -> *const std::ffi::c_void;
}

#[link(name = "fsae_interfaces__rosidl_generator_c")]
extern "C" {
    fn fsae_interfaces__msg__AllTrajectories__init(msg: *mut AllTrajectories) -> bool;
    fn fsae_interfaces__msg__AllTrajectories__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<AllTrajectories>, size: usize) -> bool;
    fn fsae_interfaces__msg__AllTrajectories__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<AllTrajectories>);
    fn fsae_interfaces__msg__AllTrajectories__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<AllTrajectories>, out_seq: *mut rosidl_runtime_rs::Sequence<AllTrajectories>) -> bool;
}

// Corresponds to fsae_interfaces__msg__AllTrajectories
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct AllTrajectories {

    // This member is not documented.
    #[allow(missing_docs)]
    pub id: u16,


    // This member is not documented.
    #[allow(missing_docs)]
    pub trajectories: rosidl_runtime_rs::Sequence<geometry_msgs::msg::rmw::PoseArray>,

}



impl Default for AllTrajectories {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !fsae_interfaces__msg__AllTrajectories__init(&mut msg as *mut _) {
        panic!("Call to fsae_interfaces__msg__AllTrajectories__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for AllTrajectories {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__AllTrajectories__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__AllTrajectories__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__AllTrajectories__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for AllTrajectories {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for AllTrajectories where Self: Sized {
  const TYPE_NAME: &'static str = "fsae_interfaces/msg/AllTrajectories";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__fsae_interfaces__msg__AllTrajectories() }
  }
}


#[link(name = "fsae_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__fsae_interfaces__msg__CAN() -> *const std::ffi::c_void;
}

#[link(name = "fsae_interfaces__rosidl_generator_c")]
extern "C" {
    fn fsae_interfaces__msg__CAN__init(msg: *mut CAN) -> bool;
    fn fsae_interfaces__msg__CAN__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<CAN>, size: usize) -> bool;
    fn fsae_interfaces__msg__CAN__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<CAN>);
    fn fsae_interfaces__msg__CAN__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<CAN>, out_seq: *mut rosidl_runtime_rs::Sequence<CAN>) -> bool;
}

// Corresponds to fsae_interfaces__msg__CAN
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct CAN {

    // This member is not documented.
    #[allow(missing_docs)]
    pub id: u16,


    // This member is not documented.
    #[allow(missing_docs)]
    pub is_rtr: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub data: [u8; 8],

}



impl Default for CAN {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !fsae_interfaces__msg__CAN__init(&mut msg as *mut _) {
        panic!("Call to fsae_interfaces__msg__CAN__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for CAN {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__CAN__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__CAN__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__CAN__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for CAN {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for CAN where Self: Sized {
  const TYPE_NAME: &'static str = "fsae_interfaces/msg/CAN";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__fsae_interfaces__msg__CAN() }
  }
}


#[link(name = "fsae_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__fsae_interfaces__msg__CANStamped() -> *const std::ffi::c_void;
}

#[link(name = "fsae_interfaces__rosidl_generator_c")]
extern "C" {
    fn fsae_interfaces__msg__CANStamped__init(msg: *mut CANStamped) -> bool;
    fn fsae_interfaces__msg__CANStamped__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<CANStamped>, size: usize) -> bool;
    fn fsae_interfaces__msg__CANStamped__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<CANStamped>);
    fn fsae_interfaces__msg__CANStamped__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<CANStamped>, out_seq: *mut rosidl_runtime_rs::Sequence<CANStamped>) -> bool;
}

// Corresponds to fsae_interfaces__msg__CANStamped
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct CANStamped {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub can: super::super::msg::rmw::CAN,

}



impl Default for CANStamped {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !fsae_interfaces__msg__CANStamped__init(&mut msg as *mut _) {
        panic!("Call to fsae_interfaces__msg__CANStamped__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for CANStamped {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__CANStamped__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__CANStamped__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__CANStamped__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for CANStamped {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for CANStamped where Self: Sized {
  const TYPE_NAME: &'static str = "fsae_interfaces/msg/CANStamped";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__fsae_interfaces__msg__CANStamped() }
  }
}


#[link(name = "fsae_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__fsae_interfaces__msg__ConeDetection() -> *const std::ffi::c_void;
}

#[link(name = "fsae_interfaces__rosidl_generator_c")]
extern "C" {
    fn fsae_interfaces__msg__ConeDetection__init(msg: *mut ConeDetection) -> bool;
    fn fsae_interfaces__msg__ConeDetection__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ConeDetection>, size: usize) -> bool;
    fn fsae_interfaces__msg__ConeDetection__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ConeDetection>);
    fn fsae_interfaces__msg__ConeDetection__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ConeDetection>, out_seq: *mut rosidl_runtime_rs::Sequence<ConeDetection>) -> bool;
}

// Corresponds to fsae_interfaces__msg__ConeDetection
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ConeDetection {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub car_pose: geometry_msgs::msg::rmw::Pose,


    // This member is not documented.
    #[allow(missing_docs)]
    pub yellow: rosidl_runtime_rs::Sequence<geometry_msgs::msg::rmw::Point>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub blue: rosidl_runtime_rs::Sequence<geometry_msgs::msg::rmw::Point>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub small_orange: rosidl_runtime_rs::Sequence<geometry_msgs::msg::rmw::Point>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub big_orange: rosidl_runtime_rs::Sequence<geometry_msgs::msg::rmw::Point>,

}



impl Default for ConeDetection {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !fsae_interfaces__msg__ConeDetection__init(&mut msg as *mut _) {
        panic!("Call to fsae_interfaces__msg__ConeDetection__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ConeDetection {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__ConeDetection__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__ConeDetection__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__ConeDetection__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ConeDetection {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ConeDetection where Self: Sized {
  const TYPE_NAME: &'static str = "fsae_interfaces/msg/ConeDetection";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__fsae_interfaces__msg__ConeDetection() }
  }
}


#[link(name = "fsae_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__fsae_interfaces__msg__HardwareStates() -> *const std::ffi::c_void;
}

#[link(name = "fsae_interfaces__rosidl_generator_c")]
extern "C" {
    fn fsae_interfaces__msg__HardwareStates__init(msg: *mut HardwareStates) -> bool;
    fn fsae_interfaces__msg__HardwareStates__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<HardwareStates>, size: usize) -> bool;
    fn fsae_interfaces__msg__HardwareStates__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<HardwareStates>);
    fn fsae_interfaces__msg__HardwareStates__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<HardwareStates>, out_seq: *mut rosidl_runtime_rs::Sequence<HardwareStates>) -> bool;
}

// Corresponds to fsae_interfaces__msg__HardwareStates
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct HardwareStates {

    // This member is not documented.
    #[allow(missing_docs)]
    pub ebs_active: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub ts_active: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub in_gear: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub master_switch_on: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub asb_ready: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub brakes_engaged: u8,

}



impl Default for HardwareStates {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !fsae_interfaces__msg__HardwareStates__init(&mut msg as *mut _) {
        panic!("Call to fsae_interfaces__msg__HardwareStates__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for HardwareStates {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__HardwareStates__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__HardwareStates__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__HardwareStates__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for HardwareStates {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for HardwareStates where Self: Sized {
  const TYPE_NAME: &'static str = "fsae_interfaces/msg/HardwareStates";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__fsae_interfaces__msg__HardwareStates() }
  }
}


#[link(name = "fsae_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__fsae_interfaces__msg__HardwareStatesStamped() -> *const std::ffi::c_void;
}

#[link(name = "fsae_interfaces__rosidl_generator_c")]
extern "C" {
    fn fsae_interfaces__msg__HardwareStatesStamped__init(msg: *mut HardwareStatesStamped) -> bool;
    fn fsae_interfaces__msg__HardwareStatesStamped__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<HardwareStatesStamped>, size: usize) -> bool;
    fn fsae_interfaces__msg__HardwareStatesStamped__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<HardwareStatesStamped>);
    fn fsae_interfaces__msg__HardwareStatesStamped__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<HardwareStatesStamped>, out_seq: *mut rosidl_runtime_rs::Sequence<HardwareStatesStamped>) -> bool;
}

// Corresponds to fsae_interfaces__msg__HardwareStatesStamped
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct HardwareStatesStamped {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub hardware_states: super::super::msg::rmw::HardwareStates,

}



impl Default for HardwareStatesStamped {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !fsae_interfaces__msg__HardwareStatesStamped__init(&mut msg as *mut _) {
        panic!("Call to fsae_interfaces__msg__HardwareStatesStamped__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for HardwareStatesStamped {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__HardwareStatesStamped__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__HardwareStatesStamped__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__HardwareStatesStamped__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for HardwareStatesStamped {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for HardwareStatesStamped where Self: Sized {
  const TYPE_NAME: &'static str = "fsae_interfaces/msg/HardwareStatesStamped";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__fsae_interfaces__msg__HardwareStatesStamped() }
  }
}


#[link(name = "fsae_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__fsae_interfaces__msg__MissionStates() -> *const std::ffi::c_void;
}

#[link(name = "fsae_interfaces__rosidl_generator_c")]
extern "C" {
    fn fsae_interfaces__msg__MissionStates__init(msg: *mut MissionStates) -> bool;
    fn fsae_interfaces__msg__MissionStates__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MissionStates>, size: usize) -> bool;
    fn fsae_interfaces__msg__MissionStates__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MissionStates>);
    fn fsae_interfaces__msg__MissionStates__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MissionStates>, out_seq: *mut rosidl_runtime_rs::Sequence<MissionStates>) -> bool;
}

// Corresponds to fsae_interfaces__msg__MissionStates
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MissionStates {

    // This member is not documented.
    #[allow(missing_docs)]
    pub mission_selected: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub mission_finished: u8,

}



impl Default for MissionStates {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !fsae_interfaces__msg__MissionStates__init(&mut msg as *mut _) {
        panic!("Call to fsae_interfaces__msg__MissionStates__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MissionStates {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__MissionStates__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__MissionStates__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__MissionStates__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MissionStates {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MissionStates where Self: Sized {
  const TYPE_NAME: &'static str = "fsae_interfaces/msg/MissionStates";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__fsae_interfaces__msg__MissionStates() }
  }
}


#[link(name = "fsae_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__fsae_interfaces__msg__MissionStatesStamped() -> *const std::ffi::c_void;
}

#[link(name = "fsae_interfaces__rosidl_generator_c")]
extern "C" {
    fn fsae_interfaces__msg__MissionStatesStamped__init(msg: *mut MissionStatesStamped) -> bool;
    fn fsae_interfaces__msg__MissionStatesStamped__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MissionStatesStamped>, size: usize) -> bool;
    fn fsae_interfaces__msg__MissionStatesStamped__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MissionStatesStamped>);
    fn fsae_interfaces__msg__MissionStatesStamped__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MissionStatesStamped>, out_seq: *mut rosidl_runtime_rs::Sequence<MissionStatesStamped>) -> bool;
}

// Corresponds to fsae_interfaces__msg__MissionStatesStamped
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MissionStatesStamped {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub mission_states: super::super::msg::rmw::MissionStates,

}



impl Default for MissionStatesStamped {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !fsae_interfaces__msg__MissionStatesStamped__init(&mut msg as *mut _) {
        panic!("Call to fsae_interfaces__msg__MissionStatesStamped__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MissionStatesStamped {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__MissionStatesStamped__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__MissionStatesStamped__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__MissionStatesStamped__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MissionStatesStamped {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MissionStatesStamped where Self: Sized {
  const TYPE_NAME: &'static str = "fsae_interfaces/msg/MissionStatesStamped";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__fsae_interfaces__msg__MissionStatesStamped() }
  }
}


#[link(name = "fsae_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__fsae_interfaces__msg__Track() -> *const std::ffi::c_void;
}

#[link(name = "fsae_interfaces__rosidl_generator_c")]
extern "C" {
    fn fsae_interfaces__msg__Track__init(msg: *mut Track) -> bool;
    fn fsae_interfaces__msg__Track__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Track>, size: usize) -> bool;
    fn fsae_interfaces__msg__Track__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Track>);
    fn fsae_interfaces__msg__Track__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Track>, out_seq: *mut rosidl_runtime_rs::Sequence<Track>) -> bool;
}

// Corresponds to fsae_interfaces__msg__Track
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Track {

    // This member is not documented.
    #[allow(missing_docs)]
    pub cones: rosidl_runtime_rs::Sequence<geometry_msgs::msg::rmw::Point>,

}



impl Default for Track {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !fsae_interfaces__msg__Track__init(&mut msg as *mut _) {
        panic!("Call to fsae_interfaces__msg__Track__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Track {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__Track__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__Track__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fsae_interfaces__msg__Track__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Track {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Track where Self: Sized {
  const TYPE_NAME: &'static str = "fsae_interfaces/msg/Track";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__fsae_interfaces__msg__Track() }
  }
}



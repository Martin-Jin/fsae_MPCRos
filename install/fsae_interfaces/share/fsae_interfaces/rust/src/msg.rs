#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to fsae_interfaces__msg__AllTrajectories

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct AllTrajectories {

    // This member is not documented.
    #[allow(missing_docs)]
    pub id: u16,


    // This member is not documented.
    #[allow(missing_docs)]
    pub trajectories: Vec<geometry_msgs::msg::PoseArray>,

}



impl Default for AllTrajectories {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::AllTrajectories::default())
  }
}

impl rosidl_runtime_rs::Message for AllTrajectories {
  type RmwMsg = super::msg::rmw::AllTrajectories;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        id: msg.id,
        trajectories: msg.trajectories
          .into_iter()
          .map(|elem| geometry_msgs::msg::PoseArray::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      id: msg.id,
        trajectories: msg.trajectories
          .iter()
          .map(|elem| geometry_msgs::msg::PoseArray::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      id: msg.id,
      trajectories: msg.trajectories
          .into_iter()
          .map(geometry_msgs::msg::PoseArray::from_rmw_message)
          .collect(),
    }
  }
}


// Corresponds to fsae_interfaces__msg__CAN

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::CAN::default())
  }
}

impl rosidl_runtime_rs::Message for CAN {
  type RmwMsg = super::msg::rmw::CAN;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        id: msg.id,
        is_rtr: msg.is_rtr,
        data: msg.data,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      id: msg.id,
      is_rtr: msg.is_rtr,
        data: msg.data,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      id: msg.id,
      is_rtr: msg.is_rtr,
      data: msg.data,
    }
  }
}


// Corresponds to fsae_interfaces__msg__CANStamped

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct CANStamped {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub can: super::msg::CAN,

}



impl Default for CANStamped {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::CANStamped::default())
  }
}

impl rosidl_runtime_rs::Message for CANStamped {
  type RmwMsg = super::msg::rmw::CANStamped;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        can: super::msg::CAN::into_rmw_message(std::borrow::Cow::Owned(msg.can)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        can: super::msg::CAN::into_rmw_message(std::borrow::Cow::Borrowed(&msg.can)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      can: super::msg::CAN::from_rmw_message(msg.can),
    }
  }
}


// Corresponds to fsae_interfaces__msg__ConeDetection

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ConeDetection {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub car_pose: geometry_msgs::msg::Pose,


    // This member is not documented.
    #[allow(missing_docs)]
    pub yellow: Vec<geometry_msgs::msg::Point>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub blue: Vec<geometry_msgs::msg::Point>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub small_orange: Vec<geometry_msgs::msg::Point>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub big_orange: Vec<geometry_msgs::msg::Point>,

}



impl Default for ConeDetection {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::ConeDetection::default())
  }
}

impl rosidl_runtime_rs::Message for ConeDetection {
  type RmwMsg = super::msg::rmw::ConeDetection;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        car_pose: geometry_msgs::msg::Pose::into_rmw_message(std::borrow::Cow::Owned(msg.car_pose)).into_owned(),
        yellow: msg.yellow
          .into_iter()
          .map(|elem| geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
        blue: msg.blue
          .into_iter()
          .map(|elem| geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
        small_orange: msg.small_orange
          .into_iter()
          .map(|elem| geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
        big_orange: msg.big_orange
          .into_iter()
          .map(|elem| geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        car_pose: geometry_msgs::msg::Pose::into_rmw_message(std::borrow::Cow::Borrowed(&msg.car_pose)).into_owned(),
        yellow: msg.yellow
          .iter()
          .map(|elem| geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
        blue: msg.blue
          .iter()
          .map(|elem| geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
        small_orange: msg.small_orange
          .iter()
          .map(|elem| geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
        big_orange: msg.big_orange
          .iter()
          .map(|elem| geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      car_pose: geometry_msgs::msg::Pose::from_rmw_message(msg.car_pose),
      yellow: msg.yellow
          .into_iter()
          .map(geometry_msgs::msg::Point::from_rmw_message)
          .collect(),
      blue: msg.blue
          .into_iter()
          .map(geometry_msgs::msg::Point::from_rmw_message)
          .collect(),
      small_orange: msg.small_orange
          .into_iter()
          .map(geometry_msgs::msg::Point::from_rmw_message)
          .collect(),
      big_orange: msg.big_orange
          .into_iter()
          .map(geometry_msgs::msg::Point::from_rmw_message)
          .collect(),
    }
  }
}


// Corresponds to fsae_interfaces__msg__HardwareStates

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::HardwareStates::default())
  }
}

impl rosidl_runtime_rs::Message for HardwareStates {
  type RmwMsg = super::msg::rmw::HardwareStates;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        ebs_active: msg.ebs_active,
        ts_active: msg.ts_active,
        in_gear: msg.in_gear,
        master_switch_on: msg.master_switch_on,
        asb_ready: msg.asb_ready,
        brakes_engaged: msg.brakes_engaged,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      ebs_active: msg.ebs_active,
      ts_active: msg.ts_active,
      in_gear: msg.in_gear,
      master_switch_on: msg.master_switch_on,
      asb_ready: msg.asb_ready,
      brakes_engaged: msg.brakes_engaged,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      ebs_active: msg.ebs_active,
      ts_active: msg.ts_active,
      in_gear: msg.in_gear,
      master_switch_on: msg.master_switch_on,
      asb_ready: msg.asb_ready,
      brakes_engaged: msg.brakes_engaged,
    }
  }
}


// Corresponds to fsae_interfaces__msg__HardwareStatesStamped

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct HardwareStatesStamped {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub hardware_states: super::msg::HardwareStates,

}



impl Default for HardwareStatesStamped {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::HardwareStatesStamped::default())
  }
}

impl rosidl_runtime_rs::Message for HardwareStatesStamped {
  type RmwMsg = super::msg::rmw::HardwareStatesStamped;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        hardware_states: super::msg::HardwareStates::into_rmw_message(std::borrow::Cow::Owned(msg.hardware_states)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        hardware_states: super::msg::HardwareStates::into_rmw_message(std::borrow::Cow::Borrowed(&msg.hardware_states)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      hardware_states: super::msg::HardwareStates::from_rmw_message(msg.hardware_states),
    }
  }
}


// Corresponds to fsae_interfaces__msg__MissionStates

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::MissionStates::default())
  }
}

impl rosidl_runtime_rs::Message for MissionStates {
  type RmwMsg = super::msg::rmw::MissionStates;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        mission_selected: msg.mission_selected,
        mission_finished: msg.mission_finished,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      mission_selected: msg.mission_selected,
      mission_finished: msg.mission_finished,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      mission_selected: msg.mission_selected,
      mission_finished: msg.mission_finished,
    }
  }
}


// Corresponds to fsae_interfaces__msg__MissionStatesStamped

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MissionStatesStamped {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub mission_states: super::msg::MissionStates,

}



impl Default for MissionStatesStamped {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::MissionStatesStamped::default())
  }
}

impl rosidl_runtime_rs::Message for MissionStatesStamped {
  type RmwMsg = super::msg::rmw::MissionStatesStamped;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        mission_states: super::msg::MissionStates::into_rmw_message(std::borrow::Cow::Owned(msg.mission_states)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        mission_states: super::msg::MissionStates::into_rmw_message(std::borrow::Cow::Borrowed(&msg.mission_states)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      mission_states: super::msg::MissionStates::from_rmw_message(msg.mission_states),
    }
  }
}


// Corresponds to fsae_interfaces__msg__Track

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Track {

    // This member is not documented.
    #[allow(missing_docs)]
    pub cones: Vec<geometry_msgs::msg::Point>,

}



impl Default for Track {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Track::default())
  }
}

impl rosidl_runtime_rs::Message for Track {
  type RmwMsg = super::msg::rmw::Track;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        cones: msg.cones
          .into_iter()
          .map(|elem| geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        cones: msg.cones
          .iter()
          .map(|elem| geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      cones: msg.cones
          .into_iter()
          .map(geometry_msgs::msg::Point::from_rmw_message)
          .collect(),
    }
  }
}



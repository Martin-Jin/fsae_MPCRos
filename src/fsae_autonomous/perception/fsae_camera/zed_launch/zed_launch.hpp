/*
OVERVIEW:
  This header defines the `ZedLaunchNode` class, the ROS 2-facing entry point of the
  cone-detection pipeline. Since the zed_ros2_wrapper migration the node no longer owns
  the camera: it is a pure subscriber that consumes the wrapper's image / depth /
  camera_info / pose topics and republishes cone detections for the rest of the stack.

KEY RESPONSIBILITIES:
  1. ROS 2 Interface Definition: Declares the four wrapper subscriptions and the three
     publishers (cone detections, car position, annotated debug image).
  2. Shared State: Caches the latest depth frame, camera intrinsics, and car pose in
     mutex-guarded members so the image callback can snapshot them consistently.
  3. YOLO Ownership: Owns the TensorRT Yolo detector object, initialised once from the
     engine_path parameter in the constructor.

DEPENDENCIES:
  - ROS 2 C++ API (`rclcpp::Node`, `rclcpp::Publisher`, `rclcpp::Subscription`)
  - ROS messages (`fsae_interfaces`, `geometry_msgs`, `sensor_msgs`)
  - yolo.hpp (TensorRT detector)
*/

#include <chrono>
#include <memory>
#include <mutex>
#include <string>
#include <iostream>

#include <rclcpp/rclcpp.hpp>

#include "std_msgs/msg/string.hpp"
#include "geometry_msgs/msg/pose.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "fsae_interfaces/msg/cone_detection.hpp"
#include "sensor_msgs/msg/image.hpp"
#include "sensor_msgs/msg/camera_info.hpp"

#include <opencv2/opencv.hpp>

#include "../cone_detection/yolo.hpp"

using namespace std::chrono_literals;

class ZedLaunchNode : public rclcpp::Node // Creates your custom class and tells it to inherit all the standard abilities of a ROS 2 Node.
{
public:
  ZedLaunchNode()
  : Node("cone_detection_node") // The internal node name MUST stay "cone_detection_node": ROS loads YAML params by this name, so it must match the top-level key in fsae_params.yaml and the name= in the launch file.
  {
    /*
    Declare all parameters with their defaults, then read them back. Values come from
    fsae_params.yaml (loaded via the launch file); the defaults below are the fallbacks
    if a key is missing.
    */
    this->declare_parameter<std::string>("engine_path", model_name);
    model_name = this->get_parameter("engine_path").as_string();

    this->declare_parameter<double>("conf_threshold", 0.55); // YOLO confidence gate. Replaces the old distance-tiered ZED tracker confidence (impossible without the SDK tracker).
    conf_threshold_ = this->get_parameter("conf_threshold").as_double();

    this->declare_parameter<double>("max_cone_distance", 25.0); // Metres. Deprojected cones farther than this are discarded (matches the old DIST_FAR_M cutoff).
    max_cone_distance_ = this->get_parameter("max_cone_distance").as_double();

    this->declare_parameter<bool>("visualise", visualisation);
    visualisation = this->get_parameter("visualise").as_bool();

    /*
    Ground-plane fit (RANSAC) — reconstructs the SDK's dropped is_grounded floor anchoring.
    See fit_ground_plane() in cone_detection.cpp. Cones are positioned by intersecting their
    base ray with the fitted plane; a weak fit falls back to per-cone median depth.
    */
    this->declare_parameter<bool>("ground_fit_enable", ground_fit_enable_);
    ground_fit_enable_ = this->get_parameter("ground_fit_enable").as_bool();
    this->declare_parameter<int>("ground_ransac_iters", ground_ransac_iters_); // RANSAC trials per frame.
    ground_ransac_iters_ = this->get_parameter("ground_ransac_iters").as_int();
    this->declare_parameter<double>("ground_inlier_thresh", ground_inlier_thresh_); // Metres from plane to count as inlier.
    ground_inlier_thresh_ = this->get_parameter("ground_inlier_thresh").as_double();
    this->declare_parameter<int>("ground_min_inliers", ground_min_inliers_); // Below this the fit is 'weak' → fall back.
    ground_min_inliers_ = this->get_parameter("ground_min_inliers").as_int();
    this->declare_parameter<int>("ground_subsample_step", ground_subsample_step_); // Pixel stride when building the cloud.
    ground_subsample_step_ = this->get_parameter("ground_subsample_step").as_int();
    this->declare_parameter<double>("ground_max_tilt_deg", ground_max_tilt_deg_); // Gravity prior: reject planes tilted more than this.
    ground_max_tilt_deg_ = this->get_parameter("ground_max_tilt_deg").as_double();
    this->declare_parameter<int>("ground_contact_offset_px", ground_contact_offset_px_); // Down-nudge for the base contact pixel (see member decl + cone_detection.cpp).
    ground_contact_offset_px_ = this->get_parameter("ground_contact_offset_px").as_int();

    // --- DEBUG params (all prefixed debug_; console diagnostics, off/quiet for normal runs) ---
    // debug_depth_grid: when true, every frame prints an ASCII grid of the raw depth-image values
    // over each detected cone's bounding box (metres, downsampled to fit the console). Off by
    // default — this floods the terminal at frame rate. Enable via fsae_params.yaml for tuning.
    this->declare_parameter<bool>("debug_depth_grid", debug_depth_grid_);
    debug_depth_grid_ = this->get_parameter("debug_depth_grid").as_bool();
    // debug_ground_plane_log: gates the routine throttled "ground plane: height=.. tilt=.." INFO
    // line. Default true (unchanged behaviour). The weak-fit WARN is NOT gated — a failed fit is a
    // real fault worth seeing even with routine logging silenced.
    this->declare_parameter<bool>("debug_ground_plane_log", debug_ground_plane_log_);
    debug_ground_plane_log_ = this->get_parameter("debug_ground_plane_log").as_bool();

    // Wrapper topic names. Parameterised because the wrapper's namespace depends on its own
    // launch configuration — confirm with `ros2 topic list | grep zed` on the Jetson.
    this->declare_parameter<std::string>("image_topic", "/zed/zed_node/left/image_rect_color");
    this->declare_parameter<std::string>("depth_topic", "/zed/zed_node/depth/depth_registered");
    this->declare_parameter<std::string>("camera_info_topic", "/zed/zed_node/left/camera_info");
    this->declare_parameter<std::string>("pose_topic", "/zed/zed_node/pose");

    /*
    this->create_publisher<MessageType>("topic_name", queue_size);
    Queue size of 10 means it will keep the last 10 messages.
    The topic contract is UNCHANGED from the SDK version — downstream (SLAM, planning,
    control, viz) depends on these exact names and types.
    (/fsae/slam/car_velocity was removed: it had zero subscribers in the repo.)
    */
    cone_detection_publisher = this->create_publisher<fsae_interfaces::msg::ConeDetection>("/fsae/perception/cone_detection", 10);
    car_position_publisher = this->create_publisher<geometry_msgs::msg::Pose>("/fsae/slam/car_position", 10);
    image_publisher = this->create_publisher<sensor_msgs::msg::Image>("/fsae/perception/image", 10);

    /*
    Load the TensorRT engine ONCE here, before any callbacks can fire. detector_.init()
    reads the .engine file and uploads the network to the GPU; returns 0 on success.
    On failure we log and mark engine_ok_ = false — the image callback then no-ops
    instead of crashing, so the node stays alive and inspectable.
    */
    if (detector_.init(model_name)) {
      RCLCPP_ERROR(this->get_logger(), "Detector init failed! engine_path='%s'", model_name.c_str());
      engine_ok_ = false;
    } else {
      engine_ok_ = true;
    }

    /*
    QoS is a silent-failure trap: the wrapper publishes image/depth/camera_info
    BEST-EFFORT (SensorDataQoS). A default (reliable) subscription would match nothing
    and receive zero messages with no error — it looks exactly like a dead camera.
    */
    image_subscription_ = this->create_subscription<sensor_msgs::msg::Image>(
        this->get_parameter("image_topic").as_string(), rclcpp::SensorDataQoS(),
        std::bind(&ZedLaunchNode::image_callback, this, std::placeholders::_1));
    depth_subscription_ = this->create_subscription<sensor_msgs::msg::Image>(
        this->get_parameter("depth_topic").as_string(), rclcpp::SensorDataQoS(),
        std::bind(&ZedLaunchNode::depth_callback, this, std::placeholders::_1));
    camera_info_subscription_ = this->create_subscription<sensor_msgs::msg::CameraInfo>(
        this->get_parameter("camera_info_topic").as_string(), rclcpp::SensorDataQoS(),
        std::bind(&ZedLaunchNode::camera_info_callback, this, std::placeholders::_1));
    // Pose is a state topic, not a sensor stream — the wrapper publishes it reliable, so a
    // default-QoS subscription matches. (If pose never arrives on the car, try SensorDataQoS.)
    pose_subscription_ = this->create_subscription<geometry_msgs::msg::PoseStamped>(
        this->get_parameter("pose_topic").as_string(), 10,
        std::bind(&ZedLaunchNode::pose_callback, this, std::placeholders::_1));
  }

private:
    // Runtime flags/config values consumed by the callbacks.
    bool visualisation = true;
    std::string model_name = "cone_detection_model.engine"; // Custom object detection model.
    double conf_threshold_ = 0.55;   // YOLO confidence gate (param conf_threshold).
    double max_cone_distance_ = 25.0; // Metres (param max_cone_distance).
    bool engine_ok_ = false;         // Set once in the constructor from detector_.init().

    // Ground-plane fit knobs (all overridable via fsae_params.yaml). See fit_ground_plane().
    bool ground_fit_enable_ = true;       // Master switch; false = always use per-cone depth.
    int ground_ransac_iters_ = 120;       // RANSAC trials per frame.
    double ground_inlier_thresh_ = 0.05;  // Metres; point-to-plane distance to count as inlier.
    int ground_min_inliers_ = 600;        // Minimum support for a trusted fit; below this ⇒ fallback.
    int ground_subsample_step_ = 8;       // Pixel stride when building the cloud (larger = cheaper).
    double ground_max_tilt_deg_ = 20.0;   // Gravity prior: reject planes tilted more than this from horizontal.

    // DEBUG params (all prefixed debug_ in the yaml; console diagnostics only).
    bool debug_depth_grid_ = false;        // dump a per-cone ASCII depth grid to console each frame (param debug_depth_grid).
    bool debug_ground_plane_log_ = true;   // print the throttled "ground plane: height/tilt/inliers" INFO (param debug_ground_plane_log).

    // Nudges the ground-contact pixel DOWN by N depth-image pixels before the ground-plane ray
    // intersection (see cone_detection.cpp, "GROUND-PLANE RAY INTERSECTION"). Corrects a
    // measured over-read caused by YOLO's box bottom sitting slightly ABOVE the true cone/ground
    // contact. RESOLUTION-DEPENDENT (full-res depth-image px): 1 suits HD720; scale up (~2-3) for
    // HD1080. Positive = sample lower = shorter, more accurate range. 0 = original behaviour.
    int ground_contact_offset_px_ = 1;    // param ground_contact_offset_px (see fsae_params.yaml).

    // The TensorRT YOLO detector. Owned by the node; initialised once in the constructor.
    Yolo detector_;

    /*
    Latest-value caches, written by the depth/camera_info/pose callbacks and snapshotted
    by the image callback. Guarded by mutex_ — depth and image arrive on the same executor
    but keeping the lock discipline explicit makes the node safe under a multithreaded
    executor too. (Depth and image are published near-synchronously by the wrapper, so a
    latest-value cache is sufficient; no message_filters sync needed.)
    */
    std::mutex mutex_;
    cv::Mat depth_;                       // Latest depth frame, 32FC1, metres. NaN/Inf = no return.
    double fx_ = 0.0, fy_ = 0.0, cx_ = 0.0, cy_ = 0.0; // Pinhole intrinsics from CameraInfo.k.
    bool have_info_ = false;              // True once the first CameraInfo has been cached.
    geometry_msgs::msg::Pose pose_;       // Latest car pose; yaw stored in orientation.w (downstream contract).

    /*
    Up in the constructor, we configured the topic names and queue sizes for your publishers.
    These lines are where those publishers are actually stored in the computer's memory.
    By keeping them private, it ensures that only this specific node is allowed to broadcast
    messages on those topics.
    */
    rclcpp::Publisher<fsae_interfaces::msg::ConeDetection>::SharedPtr cone_detection_publisher;
    rclcpp::Publisher<geometry_msgs::msg::Pose>::SharedPtr car_position_publisher;
    rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr image_publisher;

    // Subscriptions to the zed_ros2_wrapper's topics.
    rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr image_subscription_;
    rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr depth_subscription_;
    rclcpp::Subscription<sensor_msgs::msg::CameraInfo>::SharedPtr camera_info_subscription_;
    rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr pose_subscription_;

    // Callback declarations — implementations live in cone_detection/cone_detection.cpp.
    void image_callback(const sensor_msgs::msg::Image::SharedPtr msg);
    void depth_callback(const sensor_msgs::msg::Image::SharedPtr msg);
    void camera_info_callback(const sensor_msgs::msg::CameraInfo::SharedPtr msg);
    void pose_callback(const geometry_msgs::msg::PoseStamped::SharedPtr msg);
};

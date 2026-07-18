/*
OVERVIEW:
This file implements the callbacks of ZedLaunchNode (declared in zed_launch/zed_launch.hpp).
Since the zed_ros2_wrapper migration the node no longer touches the ZED SDK: the official
wrapper node owns the camera and publishes ROS topics; we subscribe to them. All the real
work happens in image_callback().

KEY RESPONSIBILITIES:
    1. YOLO Inference: Decodes the wrapper's BGRA image and passes it to the TensorRT YOLO
       network to detect bounding boxes around cones.
    2. Depth Lookup + Deprojection: For each box, reads a median depth from the cached
       depth image at the box centre and deprojects it through the pinhole intrinsics to a
       3D point in the ROS body frame (X forward, Y left).
    3. Visualization: Draws the bounding boxes, confidence scores, and class labels onto
       the camera frame and publishes it as a ROS image topic for debugging.
    4. Data Extraction & ROS Publishing: Categorizes cones by color (blue, yellow, orange),
       attaches the car's cached pose, and publishes everything as a single
       fsae_interfaces::msg::ConeDetection message.

DEPENDENCIES:
    - OpenCV (cv::Mat): For image decoding, drawing bounding boxes, and rendering text.
    - cv_bridge: Converts sensor_msgs/Image <-> cv::Mat.
    - TensorRT (NvInfer.h, yolo.hpp): For running the YOLO object detection model on the GPU.
    - ROS 2 & Messages: rclcpp, sensor_msgs/Image + CameraInfo, geometry_msgs/Pose(Stamped),
      and our custom fsae_interfaces/ConeDetection.
*/

#include <iostream>
#include <chrono>
#include <cmath>
#include <mutex> // For thread safety when accessing shared data.
#include <vector>
#include <algorithm>
#include <limits>
#include <random>
#include <sstream>  // ostringstream (debug_depth_grid dump)
#include <iomanip>  // setprecision (debug_depth_grid dump)
#include <cstdio>   // snprintf (debug_depth_grid dump)
#include <opencv2/opencv.hpp>
#include <cv_bridge/cv_bridge.h>
#include "cuda_utils.h"
#include "logging.h"
#include "utils.h"

#include "yolo.hpp"
#include "../zed_launch/zed_launch.hpp"

#include <NvInfer.h> // Brings in NVIDIA TensorRT, which is the high-performance engine that runs our YOLO model on the GPU.

using namespace nvinfer1;

#define NMS_THRESH 0.4 // NMS stands for Non-Maximum Suppression. If the AI draws two overlapping boxes on the same cone,
                      // this threshold tells the code to combine/delete the weaker box if they overlap by more than 40%.
                      // (Applied inside Yolo::run(); kept here as documentation of the pipeline's NMS setting.)

#include <rclcpp/rclcpp.hpp>

#include "std_msgs/msg/string.hpp"
#include "geometry_msgs/msg/point.hpp"
#include "geometry_msgs/msg/pose.hpp"
#include "fsae_interfaces/msg/cone_detection.hpp"
#include "sensor_msgs/msg/image.hpp"

/*
This function is solely responsible for visual debugging. If we are viewing the ROS image
topic, this is the code that draws the colored boxes and text over the cones.

It takes the raw camera frame and the YOLO detections for this frame. For every detection it
draws a rectangle around the cone and writes the class label (e.g., 0 for blue, 4 for yellow)
and the AI's confidence score above it. Boxes are colored by class label so a given cone
color always draws in the same overlay color. (The old version colored by the ZED tracker's
persistent object ID — that ID no longer exists since the SDK tracker was dropped.)
*/
static void draw_objects(cv::Mat const& image,
                         cv::Mat &res, // This will be the output image with drawings on it.
                         std::vector<BBoxInfo> const& objs, // The YOLO detections for this frame (pixel-space boxes + label + confidence).
                         std::vector<float> const& dists, // Parallel to objs: ground-plane distance (metres) from the deprojection step. NaN = no valid depth at that box centre.
                         std::vector<std::vector<int>> const& colors) // This is a predefined list of colors that we use to draw the boxes.
{
    /*
    .clone() forces a deep copy so drawing on the result never mutates the caller's
    original frame.
    */
    res = image.clone();
    for (size_t i = 0; i < objs.size(); ++i) { // Loop over every detection YOLO returned for this frame.
        BBoxInfo const& obj = objs[i];
        // Pick the box color from the class label so each cone color is drawn consistently.
        size_t const idx_color{static_cast<size_t>(obj.label) % colors.size()};
        cv::Scalar const color{cv::Scalar(colors[idx_color][0U], colors[idx_color][1U], colors[idx_color][2U])};

        // YOLO gives two corners (top-left, bottom-right); OpenCV wants x, y, width, height.
        cv::Rect const rect{static_cast<int>(std::round(obj.box.x1)),
                            static_cast<int>(std::round(obj.box.y1)),
                            static_cast<int>(std::round(obj.box.x2 - obj.box.x1)),
                            static_cast<int>(std::round(obj.box.y2 - obj.box.y1))};
        cv::rectangle(res, rect, color, 2);

        /*
        Creates and formats the text string that floats above the bounding box: the class
        label YOLO detected (e.g., 0 for blue, 4 for yellow), the confidence percentage,
        and the measured ground-plane distance in metres ("?" if the depth lookup found
        no valid stereo samples at the box centre).
        */
        char text[256U];
        if (i < dists.size() && std::isfinite(dists[i]))
            sprintf(text, "Class %d - %.1f%% - %.1fm", obj.label, obj.prob * 100.0f, dists[i]);
        else
            sprintf(text, "Class %d - %.1f%% - ?m", obj.label, obj.prob * 100.0f);

        int baseLine{0};
        cv::Size const label_size{cv::getTextSize(text, cv::FONT_HERSHEY_SIMPLEX, 0.4, 1, &baseLine)};

        // Anchor the text to the box's top-left corner, clamped so it never leaves the frame.
        int const x{rect.x};
        int const y{std::min(rect.y + 1, res.rows)};

        cv::rectangle(res, cv::Rect(x, y, label_size.width, label_size.height + baseLine), {0, 0, 255}, -1);
        cv::putText(res, text, cv::Point(x, y + label_size.height), cv::FONT_HERSHEY_SIMPLEX, 0.4, {255, 255, 255}, 1);
    }
}

/*
Cache the camera intrinsics from the wrapper's CameraInfo message. CameraInfo.k is the
row-major 3x3 pinhole matrix:
    [ fx  0  cx ]
    [  0 fy  cy ]
    [  0  0   1 ]
These four values are everything deprojection needs. They never change while the camera
is running, so caching the first message would be enough — but re-caching every message
is harmless and keeps the code trivial.
*/
void ZedLaunchNode::camera_info_callback(const sensor_msgs::msg::CameraInfo::SharedPtr msg)
{
    std::lock_guard<std::mutex> lock(mutex_);
    fx_ = msg->k[0];
    fy_ = msg->k[4];
    cx_ = msg->k[2];
    cy_ = msg->k[5];
    have_info_ = true;
}

/*
Cache the latest depth frame. The wrapper publishes depth as 32FC1 — one float per pixel,
in METRES (unlike the old SDK path which worked in millimetres). Invalid pixels
(no stereo return, occlusion) are NaN or +/-Inf; the median lookup in image_callback
filters those out.
*/
void ZedLaunchNode::depth_callback(const sensor_msgs::msg::Image::SharedPtr msg)
{
    cv::Mat depth;
    try {
        depth = cv_bridge::toCvCopy(msg, "32FC1")->image;
    } catch (cv_bridge::Exception const& e) {
        RCLCPP_WARN(this->get_logger(), "depth cv_bridge exception: %s", e.what());
        return;
    }
    std::lock_guard<std::mutex> lock(mutex_);
    depth_ = depth;
}

/*
Cache the car's pose from the wrapper's visual odometry. Preserves the OLD contract exactly:
  - position.x / position.y copied through in metres.
  - yaw is extracted from the full quaternion with the standard Euler derivation and stored
    in orientation.w. Downstream (cone_mapper, planners, Stanley) reads orientation.w as the
    heading angle, NOT as a quaternion component — this single-float repurposing is the
    established repo-wide convention.
*/
void ZedLaunchNode::pose_callback(const geometry_msgs::msg::PoseStamped::SharedPtr msg)
{
    // Extract all four components of the orientation quaternion from the wrapper's pose.
    double ox = msg->pose.orientation.x;
    double oy = msg->pose.orientation.y;
    double oz = msg->pose.orientation.z;
    double ow = msg->pose.orientation.w;

    double yaw = atan2(2.0 * (ow * oz + ox * oy), 1.0 - 2.0 * (oy * oy + oz * oz)); // Standard quaternion-to-Euler formula for yaw (heading around vertical Z). The car drives on flat ground, so yaw is the only rotation downstream needs.

    std::lock_guard<std::mutex> lock(mutex_);
    pose_.position.x = msg->pose.position.x;
    pose_.position.y = msg->pose.position.y;
    pose_.orientation.w = yaw; // Repurposed single-float yaw container (see contract note above).
}

/*
GROUND-PLANE FIT (RANSAC) — reconstructs the floor anchoring the pre-wrapper build got for
free from the ZED SDK (obj.is_grounded = true @ main). The wrapper hands us only a raw depth
image, so we rebuild the ground ourselves: subsample the lower part of the depth map into a
3D cloud (camera OPTICAL frame: X right, Y down, Z forward), RANSAC-fit a plane, and keep only
near-horizontal candidates — a gravity prior that rejects walls, cone faces and other cars.
image_callback then intersects each cone's base ray with this plane, so a cone's position
comes from thousands of ground samples instead of one noisy depth patch.
*/
struct GroundPlane {
    cv::Vec3f n{0.f, -1.f, 0.f}; // Unit normal, oriented to point "up" (optical up = -Y).
    float d = 0.f;               // Plane: n·P + d = 0. Camera-to-ground height ≈ |d|.
    int inliers = 0;             // Support count; a weak fit is treated as invalid downstream.
    bool valid = false;
};

// Deproject a depth pixel to a 3D point in the camera optical frame. Returns false for the
// ZED's no-return marker (non-finite or non-positive depth).
static inline bool deproject_px(cv::Mat const& depth, int u, int v,
                                double fx, double fy, double cx, double cy, cv::Vec3f& out)
{
    float z = depth.at<float>(v, u);
    if (!std::isfinite(z) || z <= 0.0f) return false;
    out[0] = static_cast<float>((u - cx) * z / fx);
    out[1] = static_cast<float>((v - cy) * z / fy);
    out[2] = z;
    return true;
}

static GroundPlane fit_ground_plane(cv::Mat const& depth, double fx, double fy, double cx, double cy,
                                    int iters, float inlier_thresh, int min_inliers,
                                    int step, double max_tilt_deg)
{
    GroundPlane best;
    if (depth.empty() || fx <= 0.0 || step < 1) return best;

    // Candidate cloud from the LOWER ~55% of the image only — that's where the track surface
    // projects; the upper rows are sky/backdrop/other cars and would poison the fit.
    std::vector<cv::Vec3f> pts;
    int const v_start = depth.rows * 45 / 100;
    pts.reserve(static_cast<size_t>((depth.rows - v_start) / step) * (depth.cols / step + 1));
    for (int v = v_start; v < depth.rows; v += step) {
        for (int u = 0; u < depth.cols; u += step) {
            cv::Vec3f p;
            if (deproject_px(depth, u, v, fx, fy, cx, cy, p)) pts.push_back(p);
        }
    }
    if (static_cast<int>(pts.size()) < min_inliers) return best; // Too sparse to trust.

    cv::Vec3f const up(0.f, -1.f, 0.f);
    float const cos_max_tilt = static_cast<float>(std::cos(max_tilt_deg * CV_PI / 180.0));

    // Fixed-seed RNG: keeps RANSAC reproducible frame-to-frame (no nondeterministic jitter in
    // the plane estimate) while still sampling the cloud broadly.
    std::mt19937 rng(12345u);
    std::uniform_int_distribution<size_t> pick(0, pts.size() - 1);

    for (int it = 0; it < iters; ++it) {
        cv::Vec3f const& a = pts[pick(rng)];
        cv::Vec3f const& b = pts[pick(rng)];
        cv::Vec3f const& c = pts[pick(rng)];
        cv::Vec3f nrm = (b - a).cross(c - a);
        float len = static_cast<float>(cv::norm(nrm));
        if (len < 1e-6f) continue;         // Degenerate (near-collinear) sample.
        nrm /= len;
        if (nrm.dot(up) < 0.f) nrm = -nrm; // Orient "up" so the gravity prior is one-sided.
        if (nrm.dot(up) < cos_max_tilt) continue; // Too tilted to be the ground — reject.
        float pd = -nrm.dot(a);

        int count = 0;
        for (cv::Vec3f const& p : pts)
            if (std::fabs(nrm.dot(p) + pd) < inlier_thresh) ++count;
        if (count > best.inliers) { best.inliers = count; best.n = nrm; best.d = pd; }
    }

    if (best.inliers < min_inliers) return best; // best.valid stays false → caller falls back.

    // Least-squares refit on the inlier set (PCA: the plane normal is the eigenvector of the
    // smallest eigenvalue of the centred covariance). Sharpens the coarse 3-point estimate.
    cv::Vec3f centroid(0, 0, 0);
    std::vector<cv::Vec3f> inl;
    inl.reserve(best.inliers);
    for (cv::Vec3f const& p : pts)
        if (std::fabs(best.n.dot(p) + best.d) < inlier_thresh) { inl.push_back(p); centroid += p; }
    centroid *= (1.0f / static_cast<float>(inl.size()));
    double c00=0,c01=0,c02=0,c11=0,c12=0,c22=0;
    for (cv::Vec3f const& p : inl) {
        cv::Vec3f q = p - centroid;
        c00+=q[0]*q[0]; c01+=q[0]*q[1]; c02+=q[0]*q[2];
        c11+=q[1]*q[1]; c12+=q[1]*q[2]; c22+=q[2]*q[2];
    }
    cv::Mat cov = (cv::Mat_<float>(3,3) << c00,c01,c02, c01,c11,c12, c02,c12,c22);
    cv::Mat eval, evec;
    cv::eigen(cov, eval, evec); // Rows of evec are eigenvectors, in DESCENDING eigenvalue order.
    cv::Vec3f nrm(evec.at<float>(2,0), evec.at<float>(2,1), evec.at<float>(2,2)); // smallest → normal
    if (nrm.dot(up) < 0.f) nrm = -nrm;
    best.n = nrm;
    best.d = -nrm.dot(centroid);
    best.valid = true;
    return best;
}

/*
DEBUG ONLY (param debug_depth_grid) — prints the raw depth-image values over a cone's bounding
box as an ASCII grid, so you can eyeball the per-pixel depth across a cone. The box is clamped
to the image and DOWNSAMPLED to fit the console (a near cone can be hundreds of px wide); the
printed stride is shown. Cells: depth in metres, or ' .' for the ZED's no-return marker
(NaN/Inf/<=0). The summary line's min/median/max/valid% are computed over EVERY pixel in the
box (full resolution), not just the printed grid. Emitted as one multi-line log per cone.

After the box grid, BELOW_ROWS extra rows sampled just below the box are printed (same column
stride, same vertical stride, marked with a "--- below box ---" separator) so you can see how
the depth transitions into the ground under the cone's base — useful for sanity-checking the
ground-plane fit. These rows are NOT included in the summary stats above.
*/
static void dump_depth_grid(rclcpp::Logger const& log, cv::Mat const& depth,
                            BBox const& box, int label, float dist)
{
    int x1 = std::max(0, static_cast<int>(std::floor(box.x1)));
    int y1 = std::max(0, static_cast<int>(std::floor(box.y1)));
    int x2 = std::min(depth.cols - 1, static_cast<int>(std::ceil(box.x2)));
    int y2 = std::min(depth.rows - 1, static_cast<int>(std::ceil(box.y2)));
    if (x2 < x1 || y2 < y1) return;

    // Full-resolution stats over the whole box.
    int total = 0, valid = 0;
    float dmin = std::numeric_limits<float>::max(), dmax = 0.f;
    std::vector<float> all;
    all.reserve(static_cast<size_t>((x2 - x1 + 1)) * (y2 - y1 + 1));
    for (int v = y1; v <= y2; ++v)
        for (int u = x1; u <= x2; ++u) {
            ++total;
            float d = depth.at<float>(v, u);
            if (std::isfinite(d) && d > 0.f) { ++valid; dmin = std::min(dmin, d); dmax = std::max(dmax, d); all.push_back(d); }
        }
    float dmed = std::numeric_limits<float>::quiet_NaN();
    if (!all.empty()) { std::nth_element(all.begin(), all.begin() + all.size() / 2, all.end()); dmed = all[all.size() / 2]; }

    // Downsample to at most GRID_W x GRID_H cells so a near cone doesn't flood the console.
    constexpr int GRID_W = 20, GRID_H = 16;
    // Extra rows sampled just below the box (same strides) to show the ground transition
    // under the cone base. Purely visual — not counted in the summary stats above.
    constexpr int BELOW_ROWS = 5;
    int bw = x2 - x1 + 1, bh = y2 - y1 + 1;
    int sx = std::max(1, (bw + GRID_W - 1) / GRID_W);
    int sy = std::max(1, (bh + GRID_H - 1) / GRID_H);

    std::ostringstream oss;
    oss << "\n[depth grid] label=" << label << " box=(" << x1 << "," << y1 << ")-(" << x2 << "," << y2 << ")"
        << " " << bw << "x" << bh << "px stride=" << sx << "x" << sy
        << " dist=" << std::fixed << std::setprecision(2) << dist << "m"
        << " valid=" << valid << "/" << total << " (" << (total ? valid * 100 / total : 0) << "%)"
        << " min=" << (valid ? dmin : 0.f) << " med=" << dmed << " max=" << dmax << "m";
    auto append_row = [&](int v) {
        for (int u = x1; u <= x2; u += sx) {
            float d = depth.at<float>(v, u);
            char cell[8];
            if (std::isfinite(d) && d > 0.f) std::snprintf(cell, sizeof(cell), "%5.1f", d);
            else std::snprintf(cell, sizeof(cell), "    .");
            oss << cell;
        }
    };
    for (int v = y1; v <= y2; v += sy) {
        oss << '\n';
        append_row(v);
    }
    // A few rows just below the box, aligned to the same columns, so the ground transition
    // under the cone base is visible. Clamp to the image; stop early if we run off the bottom.
    if (y2 + sy <= depth.rows - 1) {
        oss << "\n--- below box ---";
        for (int k = 1; k <= BELOW_ROWS; ++k) {
            int v = y2 + k * sy;
            if (v > depth.rows - 1) break;
            oss << '\n';
            append_row(v);
        }
    }
    RCLCPP_INFO(log, "%s", oss.str().c_str());
}

/*
The main path — runs once per camera frame, replacing the old zed.grab() polling loop:

    Step 1 - Guard:      Skip the frame if the engine failed to load, intrinsics haven't
                         arrived yet, or no depth frame is cached.
    Step 2 - Decode:     Convert the ROS Image (bgra8) into a cv::Mat.
    Step 3 - Infer:      Run YOLO to get 2D bounding boxes (already rescaled to original
                         image pixels, already confidence-thresholded and NMS-filtered).
    Step 4 - Snapshot:   Copy the cached depth / intrinsics / pose under the lock so the
                         per-cone loop below runs lock-free on a consistent set.
    Step 4.5- Ground fit: RANSAC-fit the ground plane from the depth image (once per frame).
    Step 5 - Deproject:  For each box: intersect the cone's base ray with the ground plane
                         (fallback: median depth at the box centre) -> optical-to-ROS-body
                         frame conversion -> distance filter -> color bucket.
    Step 6 - Visualize:  Optionally draw the boxes and publish the annotated image.
    Step 7 - Publish:    car_position always; ConeDetection only when >=1 blue AND >=1
                         yellow cone is present (preserved pre-existing gate, see
                         docs/MIGRATION_BUGS.md).
*/
void ZedLaunchNode::image_callback(const sensor_msgs::msg::Image::SharedPtr msg)
{
    // Step 1 — guards. Each condition means the pipeline cannot produce valid output yet.
    if (!engine_ok_) return; // Engine failed to load at startup; error was already logged.
    {
        std::lock_guard<std::mutex> lock(mutex_);
        if (!have_info_ || depth_.empty()) return; // Deprojection is impossible without intrinsics + depth.
    }

    // Step 2 — decode the wrapper's bgra8 frame into an OpenCV Mat. This matches the old
    // SDK path exactly: the ZED delivered BGRA there too, and Yolo::run() starts with
    // a BGRA->BGR conversion.
    cv::Mat frame;
    try {
        frame = cv_bridge::toCvCopy(msg, "bgra8")->image;
    } catch (cv_bridge::Exception const& e) {
        RCLCPP_WARN(this->get_logger(), "image cv_bridge exception: %s", e.what());
        return;
    }

    // Step 3 — YOLO inference. Returns pixel-space boxes on the original image, already
    // filtered by conf_threshold_ and NMS.
    auto detections = detector_.run(frame, frame.rows, frame.cols, conf_threshold_);

    // Step 4 — snapshot shared state so the loop below doesn't hold the lock during math.
    cv::Mat depth;
    double fx, fy, cx, cy;
    geometry_msgs::msg::Pose car_pose;
    {
        std::lock_guard<std::mutex> lock(mutex_);
        depth = depth_; // cv::Mat is refcounted — this is a cheap header copy. depth_callback replaces (not mutates) depth_, so this snapshot stays stable.
        fx = fx_; fy = fy_; cx = cx_; cy = cy_;
        car_pose = pose_;
    }

    // Step 4.5 — fit the ground plane once per frame (replaces the SDK's dropped is_grounded
    // floor anchoring). Cones are positioned by intersecting their base ray with this plane in
    // Step 5. Skipped — and the loop falls back to per-cone depth — when disabled, when there
    // are no detections to place, or when the fit is too weak to trust.
    GroundPlane ground;
    if (ground_fit_enable_ && !detections.empty()) {
        ground = fit_ground_plane(depth, fx, fy, cx, cy,
                                  ground_ransac_iters_, static_cast<float>(ground_inlier_thresh_),
                                  ground_min_inliers_, ground_subsample_step_, ground_max_tilt_deg_);
        if (ground.valid) {
            if (debug_ground_plane_log_) {
                float tilt_deg = static_cast<float>(
                    std::acos(std::min(1.0f, ground.n.dot(cv::Vec3f(0.f, -1.f, 0.f)))) * 180.0 / CV_PI);
                RCLCPP_INFO_THROTTLE(this->get_logger(), *this->get_clock(), 2000,
                    "ground plane: height=%.2fm tilt=%.1fdeg inliers=%d", std::fabs(ground.d),
                    tilt_deg, ground.inliers);
            }
        } else {
            RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 2000,
                "ground plane fit weak/failed — using per-cone depth fallback");
        }
    }

    fsae_interfaces::msg::ConeDetection detectionsMsg; // The output message, populated cone by cone below.
    detectionsMsg.header.stamp = msg->header.stamp; // Camera capture time, not publish time — this is what lidar_fusion time-matches against the buffered point clouds.
    detectionsMsg.header.frame_id = "camera_link"; // Cone points below are in the camera BODY frame (see fusion_node.py frame note), not the wrapper's optical frame_id on msg->header.
    detectionsMsg.car_pose = car_pose; // cone_mapper reads car_pose from INSIDE this message (not from /fsae/slam/car_position), so it must be filled every time.

    // Step 5 — depth lookup + deprojection for every detection. per_det_dist records each
    // detection's measured distance (NaN where depth was invalid) so the visualisation
    // overlay can print it next to the class/confidence text.
    std::vector<float> per_det_dist(detections.size(), std::numeric_limits<float>::quiet_NaN());
    for (size_t det_i = 0; det_i < detections.size(); ++det_i) {
        auto const& det = detections[det_i];

        // Coordinates in the CAMERA OPTICAL frame (X right, Y down, Z forward), filled by
        // whichever method below succeeds first.
        float Xc = 0.f, Yc = 0.f, Zc = 0.f;
        bool positioned = false;

        /*
        Preferred — GROUND-PLANE RAY INTERSECTION. Shoot the ray through the cone's BASE pixel
        (bottom-centre of the box, where it meets the track) and intersect it with this frame's
        fitted ground plane. Position then derives from thousands of ground samples, not one
        depth patch, and lands the cone ON the ground (p.z ≈ 0).
        */
        if (ground.valid) {
            int u_base = static_cast<int>(std::round((det.box.x1 + det.box.x2) / 2.0f));
            /*
            box bottom edge = assumed ground-contact pixel, nudged DOWN by ground_contact_offset_px_.

            WHY THE NUDGE (investigation 2026-07): the reported range is this base ray intersected
            with the ground plane, so it's hypersensitive to WHERE the base pixel is. We found the
            distance over-reads (+~0.6 m at 9.5 m, +~1 m at 11 m, growing ∝ range²) because YOLO's
            box BOTTOM sits a few pixels ABOVE the true cone/ground contact: YOLO runs on a 704×704
            letterboxed/downscaled frame, so the cone's low-contrast base edge is blurred and
            quantised (~2.7 full-res px per network px at 1080) and lands high. A pixel that's too
            high makes the ray leave at a shallower down-angle → it meets the plane farther away →
            over-read. Nudging the sample DOWN onto the real contact removes it. The depth map and
            plane fit are both fine — this is purely box-edge placement. (Confirmed against the raw
            depth via debug_depth_grid: clean ground ~2-3 rows below box.y2 reads the true range.)

            Offset is in full-res depth-image px, so it's RESOLUTION-DEPENDENT: 1 px is enough at
            HD720 (current); ~2-3 px at HD1080. Clamped so a cone near the image bottom can't push
            v_base off-image.
            */
            int v_base = static_cast<int>(std::round(det.box.y2)) + ground_contact_offset_px_;
            v_base = std::min(std::max(v_base, 0), depth.rows - 1);
            float rx = static_cast<float>((u_base - cx) / fx);
            float ry = static_cast<float>((v_base - cy) / fy);
            float denom = ground.n[0] * rx + ground.n[1] * ry + ground.n[2]; // n · (rx, ry, 1)
            if (std::fabs(denom) > 1e-6f) {                                   // else ray ∥ plane → fall back
                float t = -ground.d / denom; // ray = t·(rx,ry,1); solve n·(t·dir) + d = 0
                if (t > 0.0f) { Xc = t * rx; Yc = t * ry; Zc = t; positioned = true; }
            }
        }

        /*
        Fallback — robust median depth at the box CENTRE (the original method), used when the
        ground fit was weak or the base ray ran near-parallel to the plane. A single-pixel read
        would be hostage to stereo noise and NaN holes (the ZED marks no-return/occluded pixels
        NaN/Inf); the median of a small window is robust to both. <3 valid samples ⇒ skip cone.
        */
        if (!positioned) {
            int u = static_cast<int>(std::round((det.box.x1 + det.box.x2) / 2.0f));
            int v = static_cast<int>(std::round((det.box.y1 + det.box.y2) / 2.0f));
            std::vector<float> samples;
            samples.reserve(25);
            for (int dv = -2; dv <= 2; ++dv) {
                for (int du = -2; du <= 2; ++du) {
                    int uu = u + du;
                    int vv = v + dv;
                    if (uu < 0 || vv < 0 || uu >= depth.cols || vv >= depth.rows) continue;
                    float dpx = depth.at<float>(vv, uu);
                    if (std::isfinite(dpx) && dpx > 0.0f) samples.push_back(dpx);
                }
            }
            if (samples.size() < 3) continue; // Not enough valid depth around the box centre — skip.
            std::nth_element(samples.begin(), samples.begin() + samples.size() / 2, samples.end());
            Zc = samples[samples.size() / 2];
            Xc = static_cast<float>((u - cx) * Zc / fx);
            Yc = static_cast<float>((v - cy) * Zc / fy);
        }

        /*
        Optical frame -> ROS body frame (REP-103: X forward, Y left, Z up). Downstream
        expects cone.x = forward, cone.y = left — the old SDK build achieved the same via
        COORDINATE_SYSTEM::RIGHT_HANDED_Z_UP_X_FWD.
        MUST VERIFY ON JETSON: with a real cone, point.x must grow as the cone moves
        further ahead and point.y must be positive to the LEFT. A wrong sign here silently
        mirrors the track (see zed_wrapper_plan.md §7 / §14).
        */
        geometry_msgs::msg::Point p;
        p.x = Zc;   // forward
        p.y = -Xc;  // left (negate rightward optical X)
        p.z = -Yc;  // up — ground elevation at the cone (varies with range/pitch); unused downstream

        // Distance filter: replaces the old ZED-tracker distance-tiered confidence bands.
        float dist = std::sqrt(p.x * p.x + p.y * p.y);
        per_det_dist[det_i] = dist; // Record for the overlay even if filtered out below — seeing "27.3m" on a rejected box is more useful than "?".
        if (debug_depth_grid_) dump_depth_grid(this->get_logger(), depth, det.box, det.label, dist); // DEBUG: per-cone depth grid (param debug_depth_grid).
        if (dist > max_cone_distance_) continue; // Beyond this range stereo depth is too noisy to be useful. Skip.

        switch (det.label) { // Branch on the YOLO class label to determine which color bucket this cone belongs to.
            case 0: // Label 0 = Blue cone (left boundary of the track).
                detectionsMsg.blue.push_back(p);
                break;
            case 4: // Label 4 = Yellow cone (right boundary of the track).
                detectionsMsg.yellow.push_back(p);
                break;
            default: // Any other label is treated as a large orange cone. (small_orange is intentionally never populated — pre-existing behaviour, kept faithful.)
                detectionsMsg.big_orange.push_back(p);
                break;
        }
    }

    // Step 6 — optional visual debugging overlay, published for RViz/Foxglove.
    if (visualisation) {
        cv::Mat annotated;
        draw_objects(frame, annotated, detections, per_det_dist, CLASS_COLORS);
        sensor_msgs::msg::Image::SharedPtr imageMsg = cv_bridge::CvImage(msg->header, "bgra8", annotated).toImageMsg();
        image_publisher->publish(*imageMsg);
    }

    // Step 7 — publish. car_position always goes out (same cadence as the old pose thread,
    // now tied to the frame rate); the cone message is gated.
    car_position_publisher->publish(car_pose);

    if (detectionsMsg.yellow.size() > 0 && detectionsMsg.blue.size() > 0) { // Only publish if we can see at least one cone on each side of the track. Pre-existing gate, preserved — see docs/MIGRATION_BUGS.md for its starvation quirk.
        cone_detection_publisher->publish(detectionsMsg);
    }
}

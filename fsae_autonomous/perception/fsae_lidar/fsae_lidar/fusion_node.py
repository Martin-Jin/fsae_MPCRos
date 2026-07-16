"""Camera-LiDAR fusion node (Component B).

So far this node subscribes to the camera cone detections and the LiDAR cloud,
sets up a TF listener, and projects each camera seed point from the camera
frame into the LiDAR (velodyne) frame. Around each projected seed it runs the
full Component A refinement: crop to a 1 m sphere (A1), remove the ground
(A4/A5) via a local tilted-plane fit plus occluded-base reclaim, cluster and
verify the survivors (A6), and locate the cone's xy centroid by per-point
axis projection using regulation cone geometry (A7).

Logging: each frame prints one compact INFO block listing every cone with a
per-colour number (``#1 yellow cone``), its refined centroid and confidence,
or its drop reason. Per-stage internals (sphere counts, ground split, tilt,
reclaim, seed->refined offset) are at DEBUG — enable with
``--log-level lidar_fusion:=debug`` when tuning.

For RViz: the ground split is published as two clouds (``cone_points`` /
``ground_points``), and the marker topic carries the seed spheres, crop
boundaries, the fitted ground-plane disc, and a flat cylinder at each refined
centroid (namespace ``lidar_fusion_refined``).

Component B (time sync + fused publishing): each camera detection is paired
with the LiDAR cloud whose header stamp is nearest, within
``time_sync_tolerance_ms``. Detections with no matching cloud wait in a
short queue and are dropped once older than ``detection_max_age_ms``. Each
cloud pairs at most once, so the fused output runs at the LiDAR's rate (the
gating sensor). Refined cones are published on ``output_topic`` as a
``ConeDetection`` — positions transformed back into the camera body frame
and ``car_pose`` copied from the source detection — so it is a drop-in
replacement for the raw camera topic downstream (``cone_mapper``). The sync
assumes both sensor drivers stamp from the same ROS clock.

Emission policy, agreed 2026-07: a cone is emitted ONLY with LiDAR
confirmation — if refinement fails, the detection is dropped entirely and
listed with its reason code in the frame summary, with no camera-only
position fallback at any range (inaccurate positions are worse than missing
cones).

Frame note: cone positions in ConeDetection are expressed in the camera BODY frame
(``camera_link`` in the URDF: X-fwd, Y-left, Z-up), NOT the optical frame. Since the
zed-ros2-wrapper conversion this convention is produced by the manual deprojection in
``cone_detection.cpp`` (x=Zc, y=-Xc, z=-Yc); previously it came from the SDK's
RIGHT_HANDED_Z_UP init. Hence the seed frame defaults to ``camera_link`` and we look
up ``camera_link -> velodyne``. The axis signs are only as correct as the §14
verification in ``zed_wrapper_plan.md`` — a wrong sign makes seeds miss the clusters.
"""

from collections import deque

import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.time import Time
from rclpy.duration import Duration

from geometry_msgs.msg import Point, PointStamped
from sensor_msgs.msg import PointCloud2, PointField
from sensor_msgs_py import point_cloud2
from std_msgs.msg import Header
from visualization_msgs.msg import Marker, MarkerArray

from collections import deque #python's duble ended list

from tf2_ros import Buffer, TransformListener
from tf2_ros import LookupException, ConnectivityException, ExtrapolationException
import tf2_geometry_msgs  # noqa: F401  (registers do_transform_point for PointStamped)
from tf2_geometry_msgs import do_transform_point

from fsae_interfaces.msg import ConeDetection

from fsae_lidar.refinement import (
    ALL_POINTS_AT_GROUND, NO_CLUSTER, NO_POINTS_IN_SPHERE,
    crop_sphere, reclaim_cone_base, rescue_ground_dip, split_ground,
    verify_and_locate)


# Camera colour label -> (FusedCone colour code, RGBA marker colour).
# The ConeDetection message groups cones by colour into separate arrays; we keep
# the colour code (matching Cone.msg) alongside each array.
COLOUR_BLUE = 0
COLOUR_ORANGE = 1
COLOUR_YELLOW = 2
COLOUR_OTHER = 3

MARKER_RGBA = {
    COLOUR_BLUE: (0.1, 0.3, 1.0, 0.9),
    COLOUR_ORANGE: (1.0, 0.5, 0.0, 0.9),
    COLOUR_YELLOW: (1.0, 1.0, 0.0, 0.9),
    COLOUR_OTHER: (0.6, 0.6, 0.6, 0.9),
}

# User-facing colour names for the frame summary. Small and big orange are
# both displayed as plain "orange" (the geometry distinction stays internal).
COLOUR_NAMES = {
    COLOUR_BLUE: 'blue',
    COLOUR_ORANGE: 'orange',
    COLOUR_YELLOW: 'yellow',
    COLOUR_OTHER: 'other',
}


class LidarFusionNode(Node):
    """Subscribe to camera + LiDAR, project camera seeds into the LiDAR frame."""

    def __init__(self):
        """Declare parameters, create subscriptions, publishers and TF listener."""
        super().__init__('lidar_fusion')

        # --- parameters (defaults mirror params/lidar_fusion.yaml) ---
        self.camera_topic = self.declare_parameter(
            'camera_topic', '/fsae/perception/cone_detection').value
        self.lidar_topic = self.declare_parameter(
            'lidar_topic', '/velodyne_points').value
        # Frame the camera cones are expressed in (ZED body frame). Seeds are
        # tagged with this frame and projected into lidar_frame via TF.
        self.camera_frame = self.declare_parameter('camera_frame', 'camera_link').value
        self.lidar_frame = self.declare_parameter('lidar_frame', 'velodyne').value
        self.r_sphere = self.declare_parameter('r_sphere', 1.0).value
        # Ground removal (A4/A5): fraction of lowest-z points the local ground
        # plane is fitted to, how far above the plane a point must sit to be
        # cone, and the xy radius around the cone for the base-reclaim pass.
        self.ground_percentile = self.declare_parameter(
            'ground_percentile', 0.40).value
        self.z_offset = self.declare_parameter('z_offset', 0.03).value
        # Base reclaim: polar-footprint acceptance window slack, in metres —
        # range depth beyond the cone's own, and cross-range width beyond the
        # cone's angular width.
        self.reclaim_range_margin = self.declare_parameter(
            'reclaim_range_margin', 0.05).value
        self.reclaim_bearing_margin = self.declare_parameter(
            'reclaim_bearing_margin', 0.05).value
        # Clustering + verification gates (A6). The point minimum is
        # range-aware: min_cone_points within far_range_threshold,
        # min_cone_points_far beyond (far cones physically return few points).
        self.cluster_eps = self.declare_parameter('cluster_eps', 0.12).value
        self.min_cone_points = self.declare_parameter(
            'min_cone_points', 3).value
        self.min_cone_points_far = self.declare_parameter(
            'min_cone_points_far', 2).value
        self.far_range_threshold = self.declare_parameter(
            'far_range_threshold', 6.0).value
        self.max_cone_points = self.declare_parameter(
            'max_cone_points', 250).value
        self.max_width = self.declare_parameter('max_width', 0.30).value
        self.max_height = self.declare_parameter('max_height', 0.35).value
        # Within-ring range-dip rescue for far cones whose single low ring
        # was ground-filtered (runs only when zero points survive A5).
        self.dip_threshold = self.declare_parameter(
            'dip_threshold', 0.30).value
        # Cone geometry for the axis projection (A7) — the training cones in
        # use, not regulation sizes. Big orange kept as a separate pair for
        # when regulation cones arrive, chosen per seed via the colour tag.
        self.cone_base_radius = self.declare_parameter(
            'cone_base_radius', 0.0625).value
        self.cone_height = self.declare_parameter('cone_height', 0.31).value
        self.big_cone_base_radius = self.declare_parameter(
            'big_cone_base_radius', 0.0625).value
        self.big_cone_height = self.declare_parameter(
            'big_cone_height', 0.31).value
        self.r_cone = self.declare_parameter('r_cone', 0.05).value
        # Component B: time sync + fused output. Tolerances kept in seconds
        # to match the buffered float stamps.
        self.output_topic = self.declare_parameter(
            'output_topic', '/cone_detection_fused').value
        self.max_time_diff = self.declare_parameter(
            'time_sync_tolerance_ms', 50).value / 1000.0
        self.detection_max_age = self.declare_parameter(
            'detection_max_age_ms', 200).value / 1000.0
        self.publish_debug_markers = self.declare_parameter(
            'publish_debug_markers', True).value
        self.debug_marker_topic = self.declare_parameter(
            'debug_marker_topic', '/lidar_fusion/seed_markers').value
        self.publish_debug_cloud = self.declare_parameter(
            'publish_debug_cloud', True).value
        self.debug_cone_cloud_topic = self.declare_parameter(
            'debug_cone_cloud_topic', '/lidar_fusion/cone_points').value
        self.debug_ground_cloud_topic = self.declare_parameter(
            'debug_ground_cloud_topic', '/lidar_fusion/ground_points').value

        # --- TF ---
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # --- state ---
        self._latest_cloud = None    # most recent PointCloud2 (stamp fallback)
        self._latest_points = None   # most recent cloud as an (N, 5) array
        # Ring buffer of recent (stamp_sec, msg, points) for time matching
        # against camera detections: 10 frames ≈ 1 s of history at 10 Hz.
        self._cloud_buffer = deque(maxlen=10)
        # Stamps of clouds already paired — each cloud fuses at most once, so
        # the fused output runs at the LiDAR's rate (the gating sensor).
        self._used_cloud_stamps = set()
        # Camera detections waiting briefly for a cloud within tolerance.
        self._pending = deque(maxlen=8)
        # --- subscriptions ---
        self.create_subscription(
            ConeDetection, self.camera_topic, self._detections_cb, 10)
        self.create_subscription(
            PointCloud2, self.lidar_topic, self._cloud_cb, 10)

        # --- publishers ---
        self.marker_pub = None
        if self.publish_debug_markers:
            self.marker_pub = self.create_publisher(
                MarkerArray, self.debug_marker_topic, 10)
        self.cone_cloud_pub = None
        self.ground_cloud_pub = None
        if self.publish_debug_cloud:
            self.cone_cloud_pub = self.create_publisher(
                PointCloud2, self.debug_cone_cloud_topic, 10)
            self.ground_cloud_pub = self.create_publisher(
                PointCloud2, self.debug_ground_cloud_topic, 10)
        self.fused_pub = self.create_publisher(
            ConeDetection, self.output_topic, 10)

        self.get_logger().info(
            f"lidar_fusion up: camera='{self.camera_topic}' "
            f"lidar='{self.lidar_topic}' "
            f"transform {self.camera_frame} -> {self.lidar_frame}")

    # ------------------------------------------------------------------ #
    # Callbacks
    # ------------------------------------------------------------------ #
    def _cloud_cb(self, msg: PointCloud2):
        """Parse and buffer the cloud for time matching, then retry queue."""
        self._latest_cloud = msg
        self._latest_points = self._parse_cloud(msg)
        stamp = Time.from_msg(msg.header.stamp).nanoseconds * 1e-9
        self._cloud_buffer.append((stamp, msg, self._latest_points))
        # Forget used-marks for clouds that have rolled out of the buffer.
        alive = {s for s, _, _ in self._cloud_buffer}
        self._used_cloud_stamps &= alive
        self._drain_pending()

    def _find_closest_cloud(self, det_stamp: float):
        """Return (msg, points) for the unused buffered cloud nearest
        ``det_stamp`` and mark it used, or (None, None).

        (None, None) means the buffer is empty, every cloud is already
        paired, or the closest candidate is farther than max_time_diff away —
        callers queue the detection and retry when the next cloud arrives.
        """
        candidates = [c for c in self._cloud_buffer
                      if c[0] not in self._used_cloud_stamps]
        if not candidates:
            return None, None
        stamp, msg, points = min(
            candidates, key=lambda c: abs(c[0] - det_stamp))
        if abs(stamp - det_stamp) > self.max_time_diff:
            return None, None
        self._used_cloud_stamps.add(stamp)
        return msg, points

    def _drain_pending(self):
        """Retry queued detections against the cloud buffer (B2).

        Age is measured against the newest cloud stamp — both drivers stamp
        from the same ROS clock — so a stalled LiDAR keeps detections queued
        instead of silently expiring them against wall time.
        """
        if not self._cloud_buffer:
            return
        newest = max(s for s, _, _ in self._cloud_buffer)
        still_waiting = deque(maxlen=self._pending.maxlen)
        while self._pending:
            det = self._pending.popleft()
            det_stamp = Time.from_msg(det.header.stamp).nanoseconds * 1e-9
            if newest - det_stamp > self.detection_max_age:
                self.get_logger().warn(
                    f"dropped camera detection aged "
                    f"{(newest - det_stamp) * 1000:.0f} ms: no LiDAR cloud "
                    f"within {self.max_time_diff * 1000:.0f} ms",
                    throttle_duration_sec=5.0)
                continue
            cloud_msg, points = self._find_closest_cloud(det_stamp)
            if cloud_msg is not None:
                self._process_pair(det, cloud_msg, points)
            else:
                still_waiting.append(det)
        self._pending = still_waiting

    def _detections_cb(self, msg: ConeDetection):
        """Pair the detection with a time-matched cloud, or queue it briefly."""
        det_stamp = Time.from_msg(msg.header.stamp).nanoseconds * 1e-9
        cloud_msg, points = self._find_closest_cloud(det_stamp)
        if cloud_msg is None:
            self._pending.append(msg)
            return
        self._process_pair(msg, cloud_msg, points)

    def _process_pair(self, msg: ConeDetection, cloud_msg, points):
        """Refine one synced (detection, cloud) pair; publish fused + debug."""
        transform = self._lookup_transform()
        if transform is None:
            return
        # Inverse (velodyne -> camera_link), to express the fused output in
        # the same frame the raw camera detections use.
        inverse_tf = self._lookup_transform(inverse=True)
        if inverse_tf is None:
            return

        have_cloud = points is not None and points.shape[0] > 0
        if not have_cloud:
            self.get_logger().warn('paired LiDAR cloud parsed empty')

        fused = {'blue': [], 'yellow': [], 'small_orange': [], 'big_orange': []}
        seeds = self._iter_seeds(msg)
        markers = MarkerArray()
        cone_accum = []    # ABOVE_GROUND subsets, concatenated for the debug cloud
        ground_accum = []  # AT_GROUND subsets (discarded), for the debug cloud
        colour_tally = {}  # per-colour cone numbering, restarts every frame
        summary_lines = []
        n_refined = 0
        n_dropped = 0
        n = 0
        for idx, (colour, is_big, pt) in enumerate(seeds):
            seed_lidar = self._project(pt, transform)
            if seed_lidar is None:
                continue
            n += 1

            colour_name = COLOUR_NAMES.get(colour, 'other')
            colour_tally[colour_name] = colour_tally.get(colour_name, 0) + 1
            label = f"#{colour_tally[colour_name]} {colour_name} cone"

            count = -1
            split_note = ''
            plane = None
            refined = None
            reason = NO_POINTS_IN_SPHERE if have_cloud else 'EMPTY_CLOUD'
            if have_cloud:
                seed_xyz = (seed_lidar.x, seed_lidar.y, seed_lidar.z)
                cropped = crop_sphere(points, seed_xyz, self.r_sphere)
                count = cropped.shape[0]
                if count:
                    base_r = (self.big_cone_base_radius if is_big
                              else self.cone_base_radius)
                    cone_h = (self.big_cone_height if is_big
                              else self.cone_height)

                    def _verify(pts, _plane=None, _base_r=base_r,
                                _cone_h=cone_h):
                        return verify_and_locate(
                            pts, _plane,
                            cluster_eps=self.cluster_eps,
                            min_points=self.min_cone_points,
                            min_points_far=self.min_cone_points_far,
                            far_range_threshold=self.far_range_threshold,
                            max_points=self.max_cone_points,
                            max_width=self.max_width,
                            max_height=self.max_height,
                            base_radius=_base_r,
                            cone_height=_cone_h,
                            r_fallback=self.r_cone)

                    above, ground, plane = split_ground(
                        cropped, self.ground_percentile, self.z_offset)
                    n_filtered = above.shape[0]
                    above, ground = reclaim_cone_base(
                        above, ground, base_r, cone_h, plane,
                        self.reclaim_range_margin,
                        self.reclaim_bearing_margin)
                    n_reclaimed = above.shape[0] - n_filtered
                    n_rescued = 0

                    if above.shape[0]:
                        refined, reason = _verify(above, plane)
                    else:
                        refined, reason = None, ALL_POINTS_AT_GROUND

                    if refined is None and reason in (
                            ALL_POINTS_AT_GROUND, NO_CLUSTER):
                        # Far-cone last resort: single low ring swallowed by
                        # the ground filter (possibly with a few noise
                        # stragglers surviving it) — look for a within-ring
                        # range dip and re-verify. Only ever runs for cones
                        # that would otherwise be dropped.
                        rescued, ground = rescue_ground_dip(
                            ground, base_r, self.dip_threshold)
                        if rescued.shape[0]:
                            n_rescued = rescued.shape[0]
                            above = (np.vstack([above, rescued])
                                     if above.shape[0] else rescued)
                            refined, reason = _verify(above, plane)

                    if above.shape[0]:
                        cone_accum.append(above)
                    if ground.shape[0]:
                        ground_accum.append(ground)
                    a, b, c = plane
                    z_at_seed = a * seed_lidar.x + b * seed_lidar.y + c
                    tilt_deg = np.degrees(np.arctan(np.hypot(a, b)))
                    split_note = (
                        f" -> ground z@seed={z_at_seed:.2f} "
                        f"tilt={tilt_deg:.1f}deg, "
                        f"{above.shape[0]} cone ({n_reclaimed} reclaimed, "
                        f"{n_rescued} rescued) / "
                        f"{ground.shape[0]} ground")

            # The camera's own estimate, projected into the LiDAR frame so it
            # is directly comparable with the refined centroid.
            camera_note = (f"camera x={seed_lidar.x:>6.2f} "
                           f"y={seed_lidar.y:>6.2f}")
            if refined is not None:
                n_refined += 1
                offset = np.hypot(refined.x - seed_lidar.x,
                                  refined.y - seed_lidar.y)
                split_note += (
                    f" -> refined=({refined.x:.2f},{refined.y:.2f}) "
                    f"off={offset:.2f}m rings={refined.ring_count} "
                    f"conf={refined.confidence:.2f}")
                summary_lines.append(
                    f"  {label:<16} refined x={refined.x:>6.2f} "
                    f"y={refined.y:>6.2f} conf={refined.confidence:.2f} "
                    f"| {camera_note}")
                fused_pt = self._refined_to_camera(refined, plane, inverse_tf)
                if fused_pt is not None:
                    key = ('blue' if colour == COLOUR_BLUE else
                           'yellow' if colour == COLOUR_YELLOW else
                           'big_orange' if is_big else 'small_orange')
                    fused[key].append(fused_pt)
            else:
                # Per drop policy: no camera fallback — this detection is not
                # emitted; the summary shows the reason.
                n_dropped += 1
                summary_lines.append(
                    f"  {label:<16} dropped ({reason}) | {camera_note}")

            self.get_logger().debug(
                f"seed[{idx}] {label} "
                f"{self.camera_frame}=({pt.x:.2f},{pt.y:.2f},{pt.z:.2f}) -> "
                f"{self.lidar_frame}=("
                f"{seed_lidar.x:.2f},{seed_lidar.y:.2f},{seed_lidar.z:.2f}) "
                f"| {count} pts within {self.r_sphere:.2f} m{split_note}")

            if self.marker_pub is not None:
                markers.markers.append(
                    self._make_marker(idx, colour, seed_lidar))
                markers.markers.append(
                    self._make_boundary_marker(idx, seed_lidar))
                if plane is not None:
                    markers.markers.append(
                        self._make_ground_marker(idx, seed_lidar, plane))
                if refined is not None:
                    # base_r is always bound here: refined requires count > 0.
                    markers.markers.append(self._make_refined_marker(
                        idx, colour, refined, plane, base_r))

        # --- fused output (B3/B5): one message per paired cloud ---
        # Positions are LiDAR-refined, expressed in the camera body frame;
        # colour arrays and car_pose mirror the source ConeDetection, so this
        # topic is a drop-in for the raw camera topic downstream. Dropped
        # detections are simply absent (no camera-only fallback, by policy).
        fused_msg = ConeDetection()
        fused_msg.header.stamp = cloud_msg.header.stamp
        fused_msg.header.frame_id = self.camera_frame
        fused_msg.car_pose = msg.car_pose
        fused_msg.blue = fused['blue']
        fused_msg.yellow = fused['yellow']
        fused_msg.small_orange = fused['small_orange']
        fused_msg.big_orange = fused['big_orange']
        self.fused_pub.publish(fused_msg)

        # TODO(B4, enable_orphan_lidar): orphan-LiDAR pass — find cone-shaped
        # clusters that no camera seed claimed (camera misses from glare,
        # occlusion, image edge) and emit them with colour UNKNOWN. Sketch:
        #   remaining = cloud minus the union of all per-seed spheres
        #   above = split_ground(remaining) on a coarser grid
        #   for each xy connected component that passes the cone gates:
        #       emit FusedCone{colour=UNKNOWN, confidence=MEDIUM}
        # Deliberately left unimplemented in the first iteration — the seeded
        # path is the priority and phantom-risk here needs its own review.

        if summary_lines:
            self.get_logger().info(
                f"cones: {n_refined} refined, {n_dropped} dropped\n"
                + '\n'.join(summary_lines))

        if self.marker_pub is not None:
            self.marker_pub.publish(markers)

        if self.cone_cloud_pub is not None:
            self.cone_cloud_pub.publish(self._make_cloud_msg(
                np.vstack(cone_accum) if cone_accum
                else np.empty((0, 5), dtype=float), cloud_msg))
            self.ground_cloud_pub.publish(self._make_cloud_msg(
                np.vstack(ground_accum) if ground_accum
                else np.empty((0, 5), dtype=float), cloud_msg))

        if n:
            self.get_logger().debug(f"projected {n} camera seeds")

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _parse_cloud(self, msg: PointCloud2) -> np.ndarray:
        """Parse a PointCloud2 into an (N, 5) array of (x, y, z, intensity, ring).

        The ``ring`` field is only needed by the (not-yet-implemented)
        ring-count verification; the crop and ground removal use x/y/z only. So
        if the cloud has no ``ring`` field we degrade gracefully and fill the
        ring column with zeros rather than dropping the whole cloud. Returns an
        empty (0, 5) array only if x/y/z/intensity themselves are missing or
        the cloud is empty.
        """
        try:
            structured = point_cloud2.read_points(
                msg, field_names=['x', 'y', 'z', 'intensity', 'ring'],
                skip_nans=True)
            has_ring = True
        except (KeyError, AssertionError):
            try:
                structured = point_cloud2.read_points(
                    msg, field_names=['x', 'y', 'z', 'intensity'],
                    skip_nans=True)
                has_ring = False
            except (KeyError, AssertionError) as exc:
                self.get_logger().warn(
                    f"cloud missing x/y/z/intensity fields: {exc}")
                return np.empty((0, 5), dtype=float)

        n = structured.shape[0]
        if n == 0:
            return np.empty((0, 5), dtype=float)

        out = np.empty((n, 5), dtype=float)
        out[:, 0] = structured['x']
        out[:, 1] = structured['y']
        out[:, 2] = structured['z']
        out[:, 3] = structured['intensity']
        out[:, 4] = structured['ring'] if has_ring else 0.0
        return out

    def _iter_seeds(self, msg: ConeDetection):
        """Yield (colour_code, is_big, Point) for every cone in ConeDetection.

        ``is_big`` selects the regulation big-cone geometry for the A7 axis
        projection; only the big_orange array carries big cones.
        """
        for pt in msg.blue:
            yield COLOUR_BLUE, False, pt
        for pt in msg.yellow:
            yield COLOUR_YELLOW, False, pt
        for pt in msg.small_orange:
            yield COLOUR_ORANGE, False, pt
        for pt in msg.big_orange:
            yield COLOUR_ORANGE, True, pt

    def _lookup_transform(self, inverse: bool = False):
        """Look up camera_frame -> lidar_frame (latest available), or the
        reverse with ``inverse=True`` (used to express fused output in the
        camera frame). None on failure."""
        target, source = ((self.camera_frame, self.lidar_frame) if inverse
                          else (self.lidar_frame, self.camera_frame))
        try:
            return self.tf_buffer.lookup_transform(target, source, Time())
        except (LookupException, ConnectivityException,
                ExtrapolationException) as exc:
            self.get_logger().warn(
                f"TF {source} -> {target} unavailable: {exc}")
            return None

    def _refined_to_camera(self, refined, plane, inverse_tf):
        """Express a refined centroid (LiDAR frame) in the camera body frame.

        z is set to the ground height at the refined xy purely so the
        rotation transforms a physically sensible point — the refinement
        itself is xy-only and downstream consumers use x/y.
        """
        stamped = PointStamped()
        stamped.header.frame_id = self.lidar_frame
        stamped.point.x = refined.x
        stamped.point.y = refined.y
        if plane is not None:
            a, b, c = plane
            stamped.point.z = a * refined.x + b * refined.y + c
        try:
            return do_transform_point(stamped, inverse_tf).point
        except Exception as exc:  # noqa: BLE001
            self.get_logger().warn(f"fused point transform failed: {exc}")
            return None

    def _project(self, pt: Point, transform) -> Point:
        """Transform a camera-frame point into the LiDAR frame via TF."""
        stamped = PointStamped()
        stamped.header.frame_id = self.camera_frame
        stamped.point = pt
        try:
            out = do_transform_point(stamped, transform)
            return out.point
        except Exception as exc:  # noqa: BLE001
            self.get_logger().warn(f"point transform failed: {exc}")
            return None

    def _make_marker(self, idx: int, colour: int, pt: Point) -> Marker:
        """Build a small solid sphere marker (LiDAR frame) at one seed."""
        m = Marker()
        m.header.frame_id = self.lidar_frame
        m.header.stamp = self.get_clock().now().to_msg()
        m.ns = 'lidar_fusion_seeds'
        m.id = idx
        m.type = Marker.SPHERE
        m.action = Marker.ADD
        m.pose.position = pt
        m.pose.orientation.w = 1.0
        m.scale.x = m.scale.y = m.scale.z = 0.2
        r, g, b, a = MARKER_RGBA.get(colour, MARKER_RGBA[COLOUR_OTHER])
        m.color.r, m.color.g, m.color.b, m.color.a = r, g, b, a
        # lifetime 0 = persist until overwritten, so a one-shot publish stays.
        m.lifetime = Duration(seconds=0).to_msg()
        return m

    def _make_boundary_marker(self, idx: int, pt: Point) -> Marker:
        """Build a translucent sphere showing the r_sphere crop boundary."""
        m = Marker()
        m.header.frame_id = self.lidar_frame
        m.header.stamp = self.get_clock().now().to_msg()
        m.ns = 'lidar_fusion_sphere'
        m.id = idx
        m.type = Marker.SPHERE
        m.action = Marker.ADD
        m.pose.position = pt
        m.pose.orientation.w = 1.0
        diameter = 2.0 * self.r_sphere
        m.scale.x = m.scale.y = m.scale.z = diameter
        m.color.r, m.color.g, m.color.b, m.color.a = 0.2, 0.8, 1.0, 0.15
        m.lifetime = Duration(seconds=0).to_msg()
        return m

    def _make_ground_marker(self, idx: int, pt: Point, plane) -> Marker:
        """Build a translucent disc showing the fitted ground cut plane.

        The disc is centred at the seed xy, at the plane height plus z_offset,
        and tilted to match the fitted plane. Points above it survive the
        height filter (base reclaim aside); points at or below it are
        discarded as ground. Lets RViz show exactly where the cut landed.
        """
        a, b, c = plane
        m = Marker()
        m.header.frame_id = self.lidar_frame
        m.header.stamp = self.get_clock().now().to_msg()
        m.ns = 'lidar_fusion_ground'
        m.id = idx
        m.type = Marker.CYLINDER
        m.action = Marker.ADD
        m.pose.position.x = pt.x
        m.pose.position.y = pt.y
        m.pose.position.z = a * pt.x + b * pt.y + c + self.z_offset
        # Tilt the disc so its axis matches the plane normal (-a, -b, 1):
        # quaternion rotating +z onto the normal, axis = z x n, w = 1 + z.n.
        normal = np.array([-a, -b, 1.0])
        normal /= np.linalg.norm(normal)
        q = np.array([-normal[1], normal[0], 0.0, 1.0 + normal[2]])
        q /= np.linalg.norm(q)
        m.pose.orientation.x, m.pose.orientation.y = q[0], q[1]
        m.pose.orientation.z, m.pose.orientation.w = q[2], q[3]
        m.scale.x = m.scale.y = 2.0 * self.r_sphere
        m.scale.z = 0.005
        m.color.r, m.color.g, m.color.b, m.color.a = 0.9, 0.2, 0.2, 0.25
        m.lifetime = Duration(seconds=0).to_msg()
        return m

    def _make_refined_marker(self, idx: int, colour: int, refined,
                             plane, base_radius: float) -> Marker:
        """Build a flat solid cylinder at the refined cone centroid.

        Sits just above the fitted ground plane at the refined xy (the z is
        display-only — the refinement itself is xy-only), sized to the
        regulation cone base so RViz shows how the footprint lines up with
        the raw cone points, and coloured by the camera colour.
        """
        m = Marker()
        m.header.frame_id = self.lidar_frame
        m.header.stamp = self.get_clock().now().to_msg()
        m.ns = 'lidar_fusion_refined'
        m.id = idx
        m.type = Marker.CYLINDER
        m.action = Marker.ADD
        m.pose.position.x = refined.x
        m.pose.position.y = refined.y
        if plane is not None:
            a, b, c = plane
            m.pose.position.z = a * refined.x + b * refined.y + c + 0.01
        m.pose.orientation.w = 1.0
        m.scale.x = m.scale.y = 2.0 * base_radius
        m.scale.z = 0.02
        r, g, b_, a_ = MARKER_RGBA.get(colour, MARKER_RGBA[COLOUR_OTHER])
        m.color.r, m.color.g, m.color.b, m.color.a = r, g, b_, 1.0
        m.lifetime = Duration(seconds=0).to_msg()
        return m

    def _make_cloud_msg(self, points: np.ndarray, source_msg=None) -> PointCloud2:
        """Build a PointCloud2 (x, y, z, intensity) in the LiDAR frame.

        Used to visualise the cone/ground point splits in RViz. An empty
        ``points`` array publishes an empty cloud, which clears the display.
        ``source_msg``, when given, is the matched cloud this frame's
        refinement actually ran against — its stamp is used so the debug
        cloud lines up in time with what was fused, not just "latest".
        """
        header = Header()
        header.frame_id = self.lidar_frame
        if source_msg is not None:
            header.stamp = source_msg.header.stamp
        elif self._latest_cloud is not None:
            header.stamp = self._latest_cloud.header.stamp
        else:
            header.stamp = self.get_clock().now().to_msg()
        fields = [
            PointField(name='x', offset=0,
                       datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4,
                       datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8,
                       datatype=PointField.FLOAT32, count=1),
            PointField(name='intensity', offset=12,
                       datatype=PointField.FLOAT32, count=1),
        ]
        rows = points[:, :4].tolist() if points.shape[0] else []
        return point_cloud2.create_cloud(header, fields, rows)


def main(args=None):
    """Spin the LiDAR fusion node."""
    rclpy.init(args=args)
    node = LidarFusionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

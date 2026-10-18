2026-10-18_gocart_run3_tierA-control_stanley11pct_night
=======================================================

COPY IN fsae_MPCRos: /velodyne_packets (raw LiDAR, ~90 % of the size) removed so the
bag fits in git. Everything else is as recorded. The full bag stays in ~/fsae_data/bags/
on the laptop that copied it off the Jetson.
(originally recorded as go_cart_testing_3; folder renamed, the .db3 files keep the original prefix)

Summary
- Go-kart, autonomous Stanley steering with fixed no-pad throttle, laps of a cone loop.
- 4.1 min of data, all topics present, recorder stopped cleanly (metadata.yaml written).
- First bag that also records the stack's planning and control outputs (cone map, car pose,
  planned path, Stanley steering, Arduino commands).

When / where
- Date: 2026-10-18, recorded 21:16:35 to 21:20:40 (NZ local time)
- Light: night, low ambient light; the only lighting was a headlight/lamp at the front of the go-kart.
  Camera detection depends on light, so results may not carry over to daylight runs.
- Location / weather: (fill in)

Rig and code
- Rig: go-kart (gocart), Jetson fsae-desktop
- fsae_autonomous branch: test/planning-teleop-ground-test, commit 5af95ec
- URDF: launch default, not overridden
- Mapper: test-branch cone_mapper_shim, not cone_landmark_mapper
- Note: on this branch /cone_detection_fused includes camera-only cones beyond 8 m
  (camera_fallback_range). Re-run fusion from feat/SLAM on replay if that matters.

Launch
  scripts/car.sh start stanley_steer_test.launch.py use_pad:=false nopad_throttle_percent:=11 \
    use_serial:=true use_viz:=false use_rviz:=false use_bridge:=false \
    stanley_scale_left:=6.0 stanley_scale_right:=6.0
- Throttle 11 % fixed (same as run 2; run 1 was 12 %), no pad, no RViz/bridge

Recorder
  ros2 bag record -d 60 -o ~/fsae_data/bags/go_cart_testing_3 \
    /cone_detection_fused /fsae/perception/cone_detection /velodyne_packets /tf /tf_static \
    /zed/zed_node/imu/data /zed/zed_node/odom \
    /fsae/slam/left_track /fsae/slam/right_track /fsae/slam/car_position \
    /fsae/planning/selected_trajectory /fsae/control/drive /fsae/control/cmd_vel \
    /fsae/control/actuator_cmd
- Tier A perception topics plus planning/control outputs.
- /velodyne_packets, not /velodyne_points: re-running fusion needs the Velodyne transform node
  running during replay. No /zed/zed_node/pose, no images.
- The /fsae/slam/*, /fsae/planning/* and /fsae/control/* topics are what the stack produced live.
  Leave them out of `ros2 bag play` (or remap them) when re-running mapper, planner or Stanley,
  or they clash with the re-run nodes' output.
- /fsae/slam/car_position stores yaw (radians) in orientation.w and has no timestamp.

Track
- Cone spacing: about 3 m between same-colour cones along each row (estimated, not measured)
- Track width: (fill in)
- Laps: (fill in)

Contents (ros2 bag info)
- Duration 244.9 s, 235.4 MiB, 80292 messages, sqlite3, files _0 to _4
  | Topic                               | Count | Rate     |
  | /velodyne_packets                   |  2412 |  9.8 Hz  |
  | /fsae/perception/cone_detection     |  2064 |  8.4 Hz  |
  | /cone_detection_fused               |  1671 |  6.8 Hz  |
  | /zed/zed_node/odom                  |  3600 | 14.7 Hz  |
  | /zed/zed_node/imu/data              | 23830 |   97 Hz  |
  | /tf                                 |  4098 |   17 Hz  |
  | /tf_static                          |     2 |   -      |
  | /fsae/slam/left_track               |  4899 |   20 Hz  |
  | /fsae/slam/right_track              |  4899 |   20 Hz  |
  | /fsae/slam/car_position             |  2066 |  8.4 Hz  |
  | /fsae/planning/selected_trajectory  |  2126 |  8.7 Hz  |
  | /fsae/control/drive                 |  2082 |  8.5 Hz  |
  | /fsae/control/cmd_vel               | 14312 |   58 Hz  |
  | /fsae/control/actuator_cmd          | 12231 |   50 Hz  |
- Fused runs at ~81 % of camera frames (6.8 vs 8.4 Hz).
- /tf is about half the rate of runs 1 and 2 (17 vs 31 Hz), and the camera slightly lower
  (8.4 vs 9.1-9.5 Hz). Likely the extra recording load; cause not confirmed. SLAM replay reads
  /zed/zed_node/odom, not /tf, so this does not affect it.

Events / problems
- Jetson rebooted several times this session (power suspected). Not during this bag:
  it was up continuously from 20:49:33.
- Stops, bumps, knocked cones, Wi-Fi dropouts: (fill in with rough times)

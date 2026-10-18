2026-10-18_gocart_run4_tierA-fullcontrol_stanley13pct_viz_night
===============================================================

COPY IN fsae_MPCRos: /velodyne_packets (raw LiDAR, ~90 % of the size) removed so the
bag fits in git. Everything else is as recorded. The full bag stays in ~/fsae_data/bags/
on the laptop that copied it off the Jetson.
(originally recorded as go_cart_testing_4; folder renamed, the .db3 files keep the original prefix)

Summary
- Go-kart, autonomous Stanley steering with fixed no-pad throttle, laps of a cone loop.
- 4.5 min of data, all topics present (track_point empty, expected), recorder stopped cleanly.
- Full planning/control recording: cone map, car pose, planned path, planner debug, Stanley,
  Arduino commands and every node's log (/rosout).
- First run at 13 % throttle, and with the Jetson's RViz markers + zenoh bridge on.

When / where
- Date: 2026-10-18, recorded 21:26:29 to 21:30:59 (NZ local time)
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
  scripts/car.sh start stanley_steer_test.launch.py use_pad:=false nopad_throttle_percent:=13 \
    use_serial:=true use_viz:=true use_rviz:=false use_bridge:=true \
    stanley_scale_left:=6.0 stanley_scale_right:=6.0
- Throttle 13 % fixed (runs 2-3 were 11 %, run 1 12 %), no pad.
- use_viz/use_bridge on (RViz on the laptop via scripts/car.sh viz). Extra Jetson load vs runs 1-3.

Recorder
  ros2 bag record -d 60 -o ~/fsae_data/bags/go_cart_testing_4 \
    /cone_detection_fused /fsae/perception/cone_detection /velodyne_packets /tf /tf_static \
    /zed/zed_node/imu/data /zed/zed_node/odom \
    /fsae/slam/left_track /fsae/slam/right_track /fsae/slam/car_position \
    /fsae/planning/selected_trajectory /fsae/planning/debug/midpoints \
    /fsae/planning/debug/blue_walls /fsae/planning/debug/yellow_walls \
    /fsae/planning/debug/triangulation /fsae/control/drive /fsae/control/drive_vis \
    /fsae/control/cmd_vel /fsae/control/actuator_cmd /fsae/control/track_point /rosout
- /velodyne_packets, not /velodyne_points: re-running fusion needs the Velodyne transform node
  running during replay. No /zed/zed_node/pose, no images.
- The /fsae/slam/*, /fsae/planning/* and /fsae/control/* topics are what the stack produced live.
  Leave them out of `ros2 bag play` (or remap them) when re-running mapper, planner or Stanley.
- /fsae/slam/car_position stores yaw (radians) in orientation.w and has no timestamp.

Track
- Cone spacing: about 3 m between same-colour cones along each row (estimated, not measured)
- Track width: (fill in)
- Laps: (fill in)

Contents (ros2 bag info)
- Duration 270.1 s, 275.4 MiB, 99775 messages, sqlite3, files _0 to _4
  | Topic                               | Count | Rate     |
  | /velodyne_packets                   |  2675 |  9.9 Hz  |
  | /fsae/perception/cone_detection     |  2052 |  7.6 Hz  |
  | /cone_detection_fused               |  1688 |  6.3 Hz  |
  | /zed/zed_node/odom                  |  3947 | 14.6 Hz  |
  | /zed/zed_node/imu/data              | 25826 |   96 Hz  |
  | /tf                                 |  1953 |  7.2 Hz  |
  | /tf_static                          |     2 |   -      |
  | /fsae/slam/left_track, right_track  |  5394 |   20 Hz  |
  | /fsae/slam/car_position             |  2055 |  7.6 Hz  |
  | /fsae/planning/selected_trajectory  |  2204 |  8.2 Hz  |
  | /fsae/planning/debug/* (4 topics)   | ~2204 |  8.2 Hz  |
  | /fsae/control/drive, drive_vis      |  2055 |  7.6 Hz  |
  | /fsae/control/cmd_vel               | 15545 |   58 Hz  |
  | /fsae/control/actuator_cmd          | 13493 |   50 Hz  |
  | /fsae/control/track_point           |     0 |   -      |
  | /rosout                             |  4622 |   17 Hz  |
- Fused runs at ~82 % of camera frames (6.3 vs 7.6 Hz).
- Load trend across the session: camera 9.1-9.5 Hz (runs 1-2) -> 8.4 (run 3) -> 7.6 (run 4);
  /tf 31 -> 17 -> 7.2 Hz. Runs 3-4 recorded more topics and run 4 also had viz + bridge on.
  Cause not confirmed. SLAM replay reads /zed/zed_node/odom (steady ~14.7 Hz), not /tf.
- track_point: Stanley creates the publisher but never publishes, so 0 is expected.

Events / problems
- An earlier go_cart_testing_4 attempt was deleted; this bag is the re-run.
- Jetson rebooted several times this session (power suspected). Not during this bag:
  it was up continuously from 20:49:33.
- Stops, bumps, knocked cones, Wi-Fi dropouts: (fill in with rough times)

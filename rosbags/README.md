# Go-kart rosbags used to validate the NMPC

Two runs from the 2026-10-18 kart session, replayed through `nmpc_controller` with the
shadow-mode settings to check the NMPC against what Stanley did while driving. Results,
and the bugs they found, are in `docs/GOKART_VS_SIMULATOR.md` and in
`src/fsae_autonomous/docs/NMPC_GOKART_GROUND_TEST.md` ("From logged Stanley laps").

| Bag | Run | What it holds |
|---|---|---|
| `2026-10-18_gocart_run3_tierA-control_stanley11pct_night` | 245 s, about 3 laps, 11 % throttle | path, pose, odometry, IMU, cones, Stanley and Arduino commands |
| `2026-10-18_gocart_run4_tierA-fullcontrol_stanley13pct_viz_night` | 270 s, 13 % throttle, no orange cones (the clean reference) | as run 3, plus planner debug and `/rosout` |

- **LiDAR removed.** `/velodyne_packets` (about 90 % of each bag) was dropped so the bags
  fit in git. The NMPC replay does not need it: it reads the fused cones, which are kept.
  Re-running LiDAR fusion or SLAM needs the full bags (`~/fsae_data/bags/` on the laptop
  that copied them off the Jetson).
- **Format:** ROS 2 Humble sqlite3 bags, split every 60 s. Each folder's `README.txt` is
  the log written at the session (lighting, branch and commit, launch and recorder
  commands, topic rates, events).
- **Recorded on** `fsae_autonomous` branch `test/planning-teleop-ground-test` (Stanley
  driving), so `/fsae/control/*` and `/fsae/planning/*` are Stanley's stack, not the NMPC's.
- **Night, headlamp only:** cone colour classification is unreliable, especially orange
  (run 4 reports orange cones where none were placed).

## Replaying one through the NMPC (shadow, never drives)

Build `fsae_interfaces` and `fsae_control` from `src/fsae_autonomous`, then in one terminal:

```bash
ros2 run fsae_control nmpc_controller --ros-args \
  --params-file src/fsae_autonomous/common/fsae_bringup/config/fsae_params.yaml \
  -p use_sim_time:=true -p cmd_topic:=/fsae/control/nmpc_shadow_cmd \
  -p odom_topic:=/zed/zed_node/odom -p odom_velocity_source:=pose_diff -p use_measured_vy:=false \
  -p imu_topic:=/zed/zed_node/imu/data -p v_max:=3.0 -p v_min:=1.0 \
  -p plant_lf:=0.86 -p plant_lr:=0.14 -p plant_v_blend_lo:=8.0 -p plant_v_blend_hi:=9.0 \
  -p plant_max_steer_deg:=25.0 -p state_timeout_s:=1.0 \
  -p nmpc_standstill_speed:=0.1 -p nmpc_standstill_fade_speed:=0.3 \
  -p nmpc_publish_telemetry_enabled:=true
```

and in a second:

```bash
ros2 bag play rosbags/<bag> --clock 100 --topics /fsae/planning/selected_trajectory \
  /fsae/slam/car_position /zed/zed_node/odom /zed/zed_node/imu/data /fsae/perception/cone_detection
```

The parameters are `nmpc_shadow.launch.py`'s. Compare `/fsae/control/nmpc_shadow_cmd`
(steering in degrees, + = left) with the recorded `/fsae/control/drive` (Stanley, + = right).

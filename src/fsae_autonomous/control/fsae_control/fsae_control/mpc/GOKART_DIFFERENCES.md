# How the go-kart NMPC differs from the default design, and why

The NMPC's defaults (`nmpc_controller.py`'s declared parameters, `MPCParams`/`NMPCParams`,
the `nmpc_controller` block of `fsae_params.yaml`) describe a full-size car at racing
speed. They were set and tuned in simulation and are UNVERIFIED on the car or kart. The
kart runs steering-only at walking pace with a ZED camera as its only motion sensor, so
its launches change a set of those values. This file lists every difference and the
reason for it, so the kart setup can be told apart from the default design at a glance.

- **Where the kart values live:** the parameter blocks of `nmpc_gokart.launch.py` (drives
  the steering) and `nmpc_shadow.launch.py` (watches only). The two blocks must stay
  equal; shadow mode is only a fair preview if it runs the same settings.
- **Node code changes** (last section) apply to every launch, car and kart.
- Keep this file in step with those launch files.

## Inputs: where the state comes from

| Setting | Default design | Go-kart | Why |
|---|---|---|---|
| `cmd_topic` | `/fsae/control/cmd_vel` (to `ack_to_can`, CAN) | `/fsae/control/nmpc_cmd` (to `joystick_teleop`'s NMPC steering mode, serial to the Arduino ECU); shadow: `/fsae/control/nmpc_shadow_cmd`, consumed by nothing | the kart has no CAN path; the driver keeps the throttle and holds X + R1 for NMPC steering |
| `odom_topic`, `odom_velocity_source` | `/fsae/slam/car_odom` (no publisher), `twist` | `/zed/zed_node/odom`, `pose_diff` | the ZED odometry is the kart's only speed source. Its twist has not been checked on this rig, so the stamped pose is differentiated instead |
| `use_measured_vy` | true | false | no lateral-velocity measurement worth trusting; the kinematic model below 8 m/s does not need it |
| `imu_topic` | off | `/zed/zed_node/imu/data` | real yaw rate instead of a finite difference of the pose. The camera is pitched 7.7° down, so the reading is 0.991 of the true rate (not corrected) |
| `state_timeout_s` | 0.3 s | 1.0 s | the odometry reaches the node in bursts on the Jetson. The stamps are evenly spaced at 15 Hz, but by arrival time gaps over 0.3 s covered 7-43 % of logged runs (longest 0.84 s, worse with more load). At 0.3 s the speed source dropped to the open-loop estimate on 19 % of ticks. A second-old speed is close enough at kart speeds. UNVERIFIED in closed loop |
| `perception.launch.py` `publish_car_position` | true | false (gokart launch) | `cone_landmark_mapper` (SLAM) owns `/fsae/slam/car_position`, so the camera node must not publish it too. Note: the logged runs used for the checks below took the pose from the camera node, not SLAM |

## Vehicle model

| Setting | Default design | Go-kart | Why |
|---|---|---|---|
| `plant_lr`, `plant_lf` | built-in full-size car | 0.14 m, 0.86 m | the pose is the ZED left lens, 0.14 m ahead of the rear axle (taped). 0.86 m = a 1.00 m CAD wheelbase minus 0.14 m; the wheelbase is UNVERIFIED (not taped) |
| `plant_v_blend_lo` / `_hi` | built-in | 8 / 9 m/s | keeps the model purely kinematic at kart speeds, where only the wheelbase matters. The tyre constants are the full-size car's and are never used below 8 m/s |
| `plant_max_steer_deg` | built-in | 25° | placeholder until the kart's lock is measured. UNVERIFIED |
| `v_max` / `v_min` | 20 / 1.5 m/s | 3 / 1 m/s | the speed the NMPC plans for. The driver sets the real speed, so this only shapes the plan |

## Steering behaviour

| Setting | Default design | Go-kart | Why |
|---|---|---|---|
| `nmpc_standstill_speed` / `nmpc_standstill_fade_speed` | 0.5 / 3.0 m/s | 0.1 / 0.3 m/s | the damping stops the NMPC turning the wheel before the vehicle moves (below the first speed the first steering step costs `nmpc_standstill_steer_r_scale` = 200x more, fading back to 1x by the second). The kart's whole ground-test range, 0.5-1.1 m/s, sat inside the default band: replaying logged laps, the NMPC asked for 0.7° median where the path curvature needs 8.7°. The narrowed band keeps the protection for the moment of setting off and brings the steering to about 75-80 % of the curvature's need. UNVERIFIED on the kart: watch the first launch for an early steer |
| `nmpc_track_halfwidth` | 3.5 m | 2.4 m, changed in the shared defaults (`nmpc_params.py`, yaml), so it applies to every launch | soft bound sized for the kart's hand-laid track (cones about 2.5 m apart). See `docs/NMPC_GOKART_BRINGUP_CHECKLIST.md` |
| `nmpc_alat_ceiling_enabled` | on in the design the weights were tuned with | false in the shared defaults | models a lateral-acceleration limit never measured on the car or kart |
| `auto_steer_sign` (teleop) | n/a | −1 | +S steers right on the kart (measured); the NMPC is + = left |
| `auto_steer_scale_left/right` (teleop) | n/a | 1.0 / 1.0 placeholders | **must be calibrated before NMPC steering** (checklist section 3a). Logged Stanley laps suggest about 4-5 S per degree on the left; at 1.0 the kart would steer at roughly a fifth of what the NMPC asks. The firmware's pulse map is asymmetric, so the right side needs its own value (about 1.7x the left) |
| Throttle and brake | NMPC speed command over CAN | ignored: driver on R2, ECU brake disabled | steering-only ground test |

## Node code changes made for the kart, which apply to every launch

Each was found by replaying logged kart runs through the node. The comments at each change
in `nmpc_controller.py` give the detail; `test/test_nmpc_node_fallbacks.py` covers all three.

| Change | Before | Now | Why |
|---|---|---|---|
| Open-loop `v_x` estimate (no speed source live) | the last published speed command | last `v_x` + `a_cmd / 20 Hz` | the command leads `v_x` by `a_cmd * accel_to_speed_horizon_s`. Fed back as next tick's speed, it added that lead every tick and ran the estimate to `v_max` at 5x the planned acceleration while the kart had not sped up. On the car, which has no speed source, this was the normal path |
| Solver early return | last tick's `delta_cmd`/`a_cmd` read and published again as a fresh command | a safe-stop | `compute()` returns without updating its telemetry when it cannot solve; the node took the old values for new ones |
| Repeated waypoints in the path | passed through; the spline reference rejected the whole path | dropped on arrival | the planner sometimes pads a short path with copies of its last point (3 times in one logged run). Each was a lost tick (and, before the fix above, a repeated command) |

## Known limits of the kart setup

- **Short look-ahead.** The camera sees about two cones ahead confidently. Logged planner
  paths were still 7.9-9.6 m long (10th-90th percentile), and the NMPC's 1 s horizon covers
  under 1 m at walking pace, so the length is not limiting yet. Above roughly 3.5 m/s the
  end-of-path speed cap would start to bind on a 6 m path.
- **Curvature from few cones is noisy.** The NMPC uses path curvature for its steering
  feedforward and for its speed target (`curvature_speed()` in the node). The speed target
  only shapes the plan while the driver sets the speed.
- **Solve time.** 31 ms median, 45 ms p95 (95 % of solves at or below it), 87 ms worst on a laptop CPU against a 50 ms
  tick. Check `solve_ms` on the Jetson in shadow mode before steering.

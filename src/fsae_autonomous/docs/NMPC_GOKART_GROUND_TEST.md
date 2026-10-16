# NMPC go-kart ground test (steering only)

**What runs today:** the NMPC steers the kart. The driver keeps throttle and brake on the
pad triggers the whole time, and must hold the deadman. The NMPC's acceleration output
is computed but not used. This is a first ground test of the steering loop, not
autonomous driving.

One command brings up the full stack plus RViz:

```bash
ros2 launch fsae_bringup nmpc_gokart.launch.py            # RViz on by default
ros2 launch fsae_bringup nmpc_gokart.launch.py use_gui:=true   # + NMPC telemetry dashboard
ros2 launch fsae_bringup nmpc_gokart.launch.py use_rviz:=false # headless Jetson
```

Launch file: [`common/fsae_bringup/launch/nmpc_gokart.launch.py`](../common/fsae_bringup/launch/nmpc_gokart.launch.py).
Background on every NMPC compromise: [`NMPC_INTEGRATION_GAPS.md`](NMPC_INTEGRATION_GAPS.md).

---

## Pad controls (PS4)

| Hold | Steering | Throttle / brake | Use it for |
|---|---|---|---|
| nothing | 0 | 0 / 0 (`armed=false`) | parked; the ECU stays live |
| **X** | left stick (manual) | triggers | the go handshake, manual driving |
| **X + R1** | **NMPC** | triggers | the test itself |
| X + R1, NMPC stale or in safe-stop | 0 | throttle **forced 0**, brake trigger still works | automatic fallback |
| pad lost (no `/joy` for 0.25 s) | frames stop | frames stop | the ECU's 200 ms watchdog trips its failsafe |

- **Go handshake** (at ECU boot or after any trip): hold X and the brake, stick centred,
  throttle off, for 3 s until the ECU prints READY, then let go of the brake. Do it with
  X alone: it needs steering at exactly 0, which a live NMPC command never is.
- **R1 = button 5** is the hid-sony index for the DS4, inferred from the measured X = 1
  and the old L1 = 4 binding. Check it with `ros2 topic echo /joy` and override with
  `button_auto_steer:=<index>` if it differs.
- "NMPC stale" means no command for 0.3 s (`auto_steer_timeout`). "Safe-stop" means the
  NMPC published `frame_id: nmpc_safe_stop`, which it does when it has no pose, no path, a
  stale path, a backwards path, or repeated solve failures.

## What it launches

| Node | From | Role |
|---|---|---|
| `robot_state_publisher` | `description.launch.py` | `gocartv2.urdf.xml` frames |
| ZED wrapper, `cone_detection_node`, Velodyne, `lidar_fusion` | `perception.launch.py` | camera pose/odometry/IMU, cones |
| `cone_landmark_mapper` | `slam.launch.py` | `/fsae/slam/car_position`, track boundaries |
| planner (`planner:=fasttube` default) | `planning.launch.py` | `/fsae/planning/selected_trajectory` |
| `nmpc_controller` | this launch | steering command on `/fsae/control/nmpc_cmd` |
| `joy_node`, `joystick_teleop` | this launch | pad, deadman, NMPC steering mode → `/fsae/control/actuator_cmd` |
| `serial_bridge` | this launch | `S T B` frames to the hub Arduino ECU |
| `base_tf`, `path_viz`, `rviz2` | this launch, `use_rviz:=true` | RViz with `nmpc_gokart.rviz` |
| `nmpc_telemetry_gui` | this launch, `use_gui:=true` | matplotlib dashboard |

**Deliberately not launched:**
- `stanley_controller` / `control.launch.py`: one steering source only.
- `can.launch.py`: the kart uses the serial path.
- `cone_map_viz`: it broadcasts `map → base_link`, but `base_link` already has a parent
  (`odom → zed_camera_link → base_link`). A TF frame can have only one parent.

RViz shows the planner's path, the NMPC's predicted path (`/fsae/viz/nmpc_prediction`),
the commanded steering arrow, the SLAM trajectory and the kart model. Running RViz on a
laptop instead of the Jetson needs a remote-viz setup, which this branch does not have.

## Where each NMPC input comes from

| NMPC input | Topic | How |
|---|---|---|
| path | `/fsae/planning/selected_trajectory` | planner output, must be under 0.5 s old |
| x, y, yaw | `/fsae/slam/car_position` | SLAM-corrected ZED left-lens pose, yaw in `orientation.w` |
| v_x | `/zed/zed_node/odom` | **differentiated** from the stamped pose (`odom_velocity_source: pose_diff`), rotated into the body frame, low-passed. The wrapper's twist is not used because it has not been checked on this rig |
| yaw rate r | `/zed/zed_node/imu/data` | ZED 2i IMU `angular_velocity.z`. Falls back to the odometry-derived rate, then to Δyaw/Δt, if the IMU goes quiet for 0.3 s |
| v_y | none | set to 0 (`use_measured_vy: false`); the model is kinematic at these speeds |
| speed target | internal | from path curvature, between `v_min` 1.0 and `v_max` 3.0 m/s. Only shapes the NMPC's plan; the driver sets the real speed |

- No wheel-speed sensor exists, and the Arduino link is transmit-only, so ZED odometry is
  the only speed source.
- The ZED is pitched 7.7° down, so the IMU's z axis reads yaw rate × cos 7.7° = 0.991 of
  the true value. Not corrected.
- Check before the first run: `ros2 topic hz /zed/zed_node/imu/data` and
  `ros2 topic echo /zed/zed_node/odom --field header.stamp` (stamps must advance).

## Kart measurements used

| Quantity | Value | Source | Confidence |
|---|---|---|---|
| Rear axle → ZED left lens (the pose reference point), forward | 0.14 m | `gocartv2.urdf.xml`, tape-measured | measured |
| Wheelbase | 1.00 m | `go_cart_base.stl` tyre contact patches at x = 0.00 and 0.995 m | **CAD only, not taped** |
| NMPC `lr` / `lf` | 0.14 / 0.86 m | lens offset; wheelbase − lens offset | follows from the two above |
| Track width | 0.90 m | same mesh, contact patches at y = ±0.45 | CAD only, not used by the NMPC |
| ZED pitch | 7.70° down | ZED IMU gravity vector, URDF | measured |
| Road-wheel steering limit | 25° (`plant_max_steer_deg`) | the FSDS value, kept as a placeholder | **unmeasured** |
| Actuator degrees per road-wheel degree | 1.0 (`auto_steer_scale`) | ECU protocol says S is road-wheel degrees | **unverified**: the ECU maps ±180 servo degrees onto the full pulse range and is marked "to be changed to match servo tuning" |
| Steering lag `tau_delta` | 0.08 s | FSDS value | unmeasured |
| Mass, yaw inertia, cornering stiffness | FSDS car's | not used: the model is kinematic below 8 m/s (`plant_v_blend_lo/hi` 8/9) | n/a for this test |

### Measurements still needed

1. **Wheelbase**, tape-measured, front axle centre to rear axle centre. Then set
   `plant_lf:=<wheelbase − 0.14>`.
2. **Road-wheel steering lock**, left and right, at full servo travel. Sets
   `plant_max_steer_deg`.
3. **Steering calibration**: command `S10` and `S20` and measure the road-wheel angle,
   both directions. The ratio gives `auto_steer_scale`. If the wheels do not reach 10°
   and 20°, NMPC steering is wrong by that factor.
4. Optional, for later speed work: steering response time (sets `tau_delta`), and the
   throttle-percent → acceleration map.

## Known behaviour on tight arcs

In an offline closed-loop check (kinematic kart, 6 m radius, 2 m/s), the NMPC settles at
9.0° of steering against a kinematic 9.5°, but runs about **0.5 m wide** of the path with
a steady −8° heading error. The NMPC measures heading error at the front axle, where the
path tangent leads the kart's own heading by about lf / R (8.2° here), and trades lateral
error to reduce it. The effect shrinks with radius. Expect the kart to sit slightly
outside the line in tight corners.

## Bring-up checklist

1. Wheels off the ground. Launch, check `/joy` indices, do the go handshake.
2. Hold X + R1 with a path published. The steering should follow the NMPC arrow in RViz,
   with the correct sign: a left bend steers left.
3. Release R1: manual steering returns. Release X: neutral.
4. Pull the planner (or stop SLAM): steering must go to 0 and throttle to 0 within 0.3 s.
5. On the ground at walking pace, the driver on the triggers, then build speed slowly.

## Not done yet

- **No throttle or brake from the NMPC.** `a_cmd` reaches `/fsae/control/accel_cmd` only.
- **The cone-proximity brake does nothing here**: it zeroes the NMPC's speed command,
  which this test ignores. The driver is the brake.
- The tyre model, mass and inertia are the FSDS car's.
- The steering slew limit in the ECU firmware is off; `joystick_teleop.max_steer_rate`
  is 0 (off) too.
- Frozen-input check: the ECU trips if throttle and steering both stay unchanged for 5 s.
  The NMPC's steering normally moves, but a long, perfectly straight run at constant
  throttle could trip it.

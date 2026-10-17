# NMPC go-kart ground test (steering only)

**What runs today:** the NMPC steers the kart. The driver keeps the throttle on the pad
trigger the whole time, and must hold the deadman. The NMPC's acceleration output is
computed but not used. This is a first ground test of the steering loop, not autonomous
driving.

**Nothing here has run on the kart yet.** The NMPC's weights and the vehicle constants
the launch does not override were tuned in simulation. UNVERIFIED on the kart.

> **There is no service brake.** In the current ECU firmware (`autonomous_gokart` `main`
> and `feat/ground-testing`, `KART_BRAKE_ENABLED 0`) the brake actuator is disabled, and the
> `B` field is only read for the go handshake. Pressing L2 does not slow the kart. To slow
> down, release R2 and coast; to stop hard, release X (neutral) or pull the string e-stop
> (cuts HV).

One command brings up the full stack plus RViz:

```bash
ros2 launch fsae_bringup nmpc_gokart.launch.py            # RViz on by default
ros2 launch fsae_bringup nmpc_gokart.launch.py use_gui:=true   # + NMPC telemetry dashboard
ros2 launch fsae_bringup nmpc_gokart.launch.py use_rviz:=false # headless Jetson
```

Before this test: [`NMPC_VALIDATION_AND_TESTING.md`](NMPC_VALIDATION_AND_TESTING.md) covers the unit
tests, the bench test (no vehicle) and shadow mode (the NMPC watches while something else
drives). In none of those does an NMPC command reach the kart.

**To-do list for getting it running (measurements, checks, first runs):**
[`NMPC_GOKART_BRINGUP_CHECKLIST.md`](NMPC_GOKART_BRINGUP_CHECKLIST.md).

Launch file: [`common/fsae_bringup/launch/nmpc_gokart.launch.py`](../common/fsae_bringup/launch/nmpc_gokart.launch.py).
Background on every NMPC compromise: [`NMPC_INTEGRATION_GAPS.md`](NMPC_INTEGRATION_GAPS.md).
The node's inputs and outputs as a flow chart:
[`MPC_NODE_DOCS.md`](../control/fsae_control/fsae_control/mpc/MPC_NODE_DOCS.md#inputs-and-outputs-flow-chart).
Where it sits in the whole stack: [`ARCHITECTURE.md`](ARCHITECTURE.md) diagrams 1-3.

---

## Pad controls (PS4)

| Hold | Steering | Throttle / brake | Use it for |
|---|---|---|---|
| nothing | 0 | 0 / 0 (`armed=false`) | parked; the ECU stays live |
| **X** | left stick (manual) | triggers | the go handshake, manual driving |
| **X + R1** | **NMPC** | triggers | the test itself |
| X + R1, NMPC stale or in safe-stop | 0 | throttle **forced 0** | automatic fallback |
| pad lost (no `/joy` for 0.25 s) | frames stop | frames stop | the ECU's command watchdog trips its failsafe (HV cut, steering limp). Its timeout depends on the flashed firmware: 200 ms on `main`, 500 ms on `feat/ground-testing`, 1 s on `feat/brake-control` |

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
| speed target | internal | from path curvature, between `v_min` 1.0 and `v_max` 3.0 m/s. Only shapes the NMPC's plan; the driver sets the real speed. The curvature-to-speed mapping is untuned (UNVERIFIED) |

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
| Wheelbase | 1.00 m | `go_cart_base.stl` tyre contact patches at x = 0.00 and 0.995 m | **CAD only, not taped.** UNVERIFIED |
| NMPC `lr` / `lf` | 0.14 / 0.86 m | lens offset; wheelbase − lens offset | `lr` measured; `lf` UNVERIFIED (CAD wheelbase) |
| Track width | 0.90 m | same mesh, contact patches at y = ±0.45 | CAD only, not used by the NMPC |
| ZED pitch | 7.70° down | ZED IMU gravity vector, URDF | measured |
| Road-wheel steering limit | 25° (`plant_max_steer_deg`) | simulation vehicle value, kept as a placeholder | **unmeasured.** UNVERIFIED |
| Steering sign | `auto_steer_sign` −1: **+S steers RIGHT** | measured 2026-10-14 on the Stanley steering test (`test/planning-teleop-ground-test`), matches teleop's `invert_steer: true` | measured. The ECU firmware comment (+S = left) is wrong for this kart |
| ECU S per road-wheel degree, left / right | 1.0 / 1.0 (`auto_steer_scale_left/right`) | placeholder | **unmeasured**. The firmware's S → pulse map is asymmetric (−180 spans 1403 µs, +180 only 847 µs), so each side needs its own value |
| Steering lag `tau_delta` | 0.08 s | simulation vehicle value | **unmeasured.** UNVERIFIED |
| Mass, yaw inertia, cornering stiffness | simulation vehicle's | not used: the model is kinematic below 8 m/s (`plant_v_blend_lo/hi` 8/9) | UNVERIFIED, n/a for this test |

### Measurements still needed

None of these are recorded on `feat/teleop-node-ground-testing` or on
`test/planning-teleop-ground-test`. The latter has the same values as placeholders
(`steering_viz.wheelbase` 1.0, `stanley_controller.front_axle_dist` 1.0 "UNMEASURED guess",
`stanley_scale_left/right` 1.0) and the bench procedure, which this branch now carries as
[`scripts/steer_calibrate.py`](../scripts/steer_calibrate.py).

1. **Steering calibration** (wheels off the ground, stack stopped):
   `scripts/steer_calibrate.py` steps S through 0, ±30 … ±180 at 50 Hz with throttle and
   brake hard-coded to 0. At each step, measure both front wheels' angle (a 1 m straight
   edge on the wheel face: angle = atan(toe offset / 1 m)) and take the mean. Stop on a
   side as soon as the wheels reach the mechanical lock. Then:
   - `auto_steer_scale_left` / `_right` = S per road-wheel degree on each side, the slope
     through the origin over the range the NMPC uses (up to the lock).
   - `plant_max_steer_deg` = the full lock in road-wheel degrees, smaller side.
   - teleop `max_angle` (in `fsae_params.yaml`) = S at full lock, if the lock comes before
     ±180, so neither the stick nor the NMPC can stall the servo against the stop.
   - Confirm the sign while there: +S should steer right.
   - What the firmware does with S (`SteeringControl.cpp`, `feat/ground-testing`): S is
     **not** road-wheel degrees. ±180 maps linearly onto each half of the pulse range
     around the measured centre 1453 µs: −S toward 50 µs (7.79 µs per S), +S toward
     2300 µs (4.71 µs per S). The servo's own potentiometer sets how far the wheels
     travel. That asymmetry is why each side has its own scale.
2. **Wheelbase**, rear axle centre to front axle centre. Then `plant_lf:=<wheelbase − 0.14>`.
3. **R1 index**: hold R1 with `ros2 topic echo /joy` running and note which `buttons[]`
   entry goes to 1. Pass `button_auto_steer:=<n>` if it isn't 5.
4. Optional, for later speed work: steering response time (sets `tau_delta`), and the
   throttle-percent → acceleration map.

The ZED offset (0.14 m ahead of the rear axle) is the tape-measured value in this branch's
URDF. `test/planning-teleop-ground-test` still has an older 0.201 m in its URDF.

## Known behaviour on tight arcs

**Expect the kart to sit slightly outside the line in tight corners.** In an offline
closed-loop check against a simple kinematic kart model (a unit-test harness, 6 m radius,
2 m/s), the NMPC settles at 9.0° of steering against a kinematic 9.5°, but runs about
**0.5 m wide** of the path with a steady −8° heading error. Offline kinematic-model check;
UNVERIFIED on the kart. The NMPC measures heading error at the front axle, where the
path tangent leads the kart's own heading by about lf / R (8.2° here), and trades lateral
error to reduce it. The effect shrinks with radius.

## Bring-up checklist

1. Wheels off the ground. Launch, check `/joy` indices, do the go handshake.
2. Hold X + R1 with a path published. The steering should follow the NMPC arrow in RViz,
   with the correct sign: a left bend steers left. The launch already passes
   `auto_steer_sign:=-1` for the measured +S = right; if the wheels turn the wrong way,
   stop and flip it.
3. Release R1: manual steering returns. Release X: neutral.
4. Pull the planner (or stop SLAM): steering must go to 0 and throttle to 0 within 0.3 s.
5. On the ground at walking pace, the driver on the triggers, then build speed slowly.

## Not done yet

- **End of the path:** the speed target is capped so the car can stop
  `path_end_margin_m` (0.5 m) before the last waypoint at `path_end_decel` (1.5 m/s²),
  allowing `path_end_lag_s` (1.0 s) for the NMPC to follow a lowered target
  (`control_utils.path_end_speed_cap`). It lowers the speed the cost tracks; it is not a
  constraint. Offline closed-loop check on a straight: stops at the margin from 3 and
  6 m/s. A closed-loop (full-lap) path, whose end lies within 10 m of its start and
  which is at least 50 m long, is never capped. `path_end_decel: 0` turns it off.
  UNVERIFIED on the kart or car.
  On the kart the driver sets the speed, so this only shapes the NMPC's plan. The
  planner's path ends where the visible cones end, so the cap also limits the planned
  speed to what the visible path allows.
- **No throttle or brake from the NMPC.** `a_cmd` reaches `/fsae/control/accel_cmd` only.
- **The cone-proximity brake does nothing here**: it zeroes the NMPC's speed command,
  which this test ignores. With no service brake either, the driver stops the kart by
  releasing the throttle, releasing X, or pulling the e-stop.
- The tyre model, mass and inertia are the simulation vehicle's (UNVERIFIED on the kart;
  unused below 8 m/s).
- The NMPC weights were tuned in simulation (UNVERIFIED on the kart).
- The steering slew limit in the ECU firmware is a TODO (`MAX_STEER_RATE_DEG_S` unused),
  and `joystick_teleop.max_steer_rate` is 0 (off) too, so the servo jumps to each command.
- Frozen-input check: on `main` the ECU trips if throttle and steering both stay unchanged
  for 5 s. A long, perfectly straight run at constant throttle could trip it.
  `feat/ground-testing` disables this check (`KART_FROZEN_CHECK_ENABLED 0`).

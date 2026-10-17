# NMPC go-kart bring-up checklist

Everything still to do, in order, to get the steering-only NMPC running on the kart. Tick
each box. The *why* behind each item is in
[`NMPC_GOKART_GROUND_TEST.md`](NMPC_GOKART_GROUND_TEST.md); this page is the to-do list.

## Status: tested so far, and what is left

| Check | Status |
|---|---|
| Unit tests (`colcon test --packages-select fsae_control`) | pass on a PC |
| Scripted node test: NMPC + teleop NMPC mode with fake path/pose/odometry/IMU/pad | pass on a PC. Deadman, R1 mode, stale and safe-stop fallbacks, steering sign mapping |
| Bench test (`nmpc_bench.launch.py`): end-of-path hold, no command to any vehicle | pass, run by hand on a PC |
| Shadow mode (`nmpc_shadow.launch.py`) publishes only on its own topic | pass on a PC with scripted inputs |
| End-of-path speed cap | offline closed-loop check only; in simulation with a live planner the speed stayed around 6 to 7 m/s, by design (UNVERIFIED on the kart) |
| Steering weights updated to the newer simulation-tuned set (section 6) | unit tests and bench test pass on a PC; UNVERIFIED on the kart |
| **Steering sweep, wheelbase, R1 index** (section 3) | **not done** |
| **Sensor checks on the kart** (section 4) | **not done** |
| **Shadow mode on the kart** (section 4b) | **not done** |
| **NMPC steering the kart** (section 5) | **not done, never run on the kart** |

Every steering calibration value below is a placeholder until section 3 is done. The
NMPC weights and the vehicle constants the launch does not override were tuned in
simulation (UNVERIFIED on the kart).

---

## 1. Software on the Jetson

- [ ] Get the branch:
  ```bash
  cd ~/ros2_ws/src/fsae_autonomous && git fetch && git switch feat/mpc_ground_test && git pull
  ```
  The commit must include "measured +S = right sign". An older push of this branch
  (`d22d512`) steers the wrong way.
- [ ] Python deps (pip-only, not rosdep): `pip install -r requirements.txt`. The NMPC needs
  `osqp` and `scipy`; check with `python3 -c "import osqp, scipy"`.
- [ ] Build. `~/ros2_ws` is not a symlink install, so rebuild after every pull:
  ```bash
  cd ~/ros2_ws
  colcon build --packages-select fsae_interfaces fsae_control fsae_can_bridge \
      fsae_serial_bridge fsae_visualization fsae_description fsae_bringup
  source install/setup.bash
  ```
- [ ] Check the new pieces installed:
  ```bash
  ros2 pkg executables fsae_control | grep nmpc_controller
  ls install/fsae_bringup/share/fsae_bringup/launch/nmpc_gokart.launch.py
  ls install/fsae_control/share/fsae_control/mpc/nmpc_gokart.rviz
  ```

## 2. Hardware and firmware checks

- [ ] **Which ECU firmware is flashed?** Ask whoever flashed it, or reflash. It sets the
  watchdog and the frozen-input check (`autonomous_gokart`, `go-kart-ecu/KartConfig.h`):

  | Firmware branch | No-command cutout | Frozen-input check | Brake actuator |
  |---|---|---|---|
  | `main` | 200 ms | on (5 s) | disabled |
  | `feat/ground-testing` (newest, recommended) | 500 ms | **off** | disabled |
  | `feat/brake-control` | 1 s | on (5 s) | see that branch |

- [ ] **Know that there is no service brake.** With the brake actuator disabled, L2 does
  nothing except the go handshake. Slow down by releasing R2; stop by releasing X or
  pulling the string e-stop.
- [ ] Arduino port: `ls -l /dev/serial/by-id/` shows
  `usb-FTDI_FT232R_USB_UART_A5069RR4-if00-port0`.
- [ ] Serial permission: `groups` includes `dialout`.
- [ ] Pad: `ls -l /dev/input/js0`.
- [ ] Triggers at rest: with `ros2 run joy joy_node` running, `ros2 topic echo /joy`
  **before touching the triggers**. `axes[3]` (L2) and `axes[4]` (R2) must both read 1.0.
  If they read 0.0, press and release both once and check again.
- [ ] **R1 index**: hold R1 and note which `buttons[]` entry goes to 1. Write it here: ____.
  If it isn't 5, pass `button_auto_steer:=<n>` (and change the default in the launch file).
- [ ] Servo power switch within reach. The string e-stop and serial `e` cut HV but leave
  the steering live.

## 3. Measurements

Wheels off the ground, motor power off if possible, ROS stack **stopped** (the script
refuses to start while anything holds the serial port).

### 3a. Steering sweep

- [ ] Run `scripts/steer_calibrate.py`. It sends `S<v> T0 B0` at 50 Hz and steps on each
  Enter through 0, +30 … +180, 0, −30 … −180, 0. **The wheels move even though the ECU is
  disarmed.** Stop on a side as soon as the wheels reach the mechanical lock.
- [ ] At each step measure both front wheels' angle: a 1 m straight edge on the wheel
  face, angle = atan(toe offset / 1 m). Record the mean.

  | S | Left wheel ° | Right wheel ° | Mean ° | Turns L / R |
  |---|---|---|---|---|
  | 0 | | | | |
  | +30 | | | | |
  | +60 | | | | |
  | +90 | | | | |
  | +120 | | | | |
  | +180 | | | | |
  | −30 | | | | |
  | −60 | | | | |
  | −90 | | | | |
  | −120 | | | | |
  | −180 | | | | |

- [ ] When the script exits the ECU failsafe trips and the steering goes limp. Reset the
  Arduino to clear it.

From the table:

| Value | How | Launch argument | Placeholder now |
|---|---|---|---|
| Sign | +S should turn RIGHT (measured on the Stanley test, 2026-10-14). If +S turns LEFT, use +1 | `auto_steer_sign` | −1.0 |
| S per wheel degree, left | slope through the origin of the S < 0 rows (S / mean °), up to the lock | `auto_steer_scale_left` | 1.0 |
| S per wheel degree, right | same for the S > 0 rows | `auto_steer_scale_right` | 1.0 |
| Steering lock | full lock in wheel degrees, smaller side | `plant_max_steer_deg` | 25.0 (simulation vehicle value, UNVERIFIED) |
| S at lock | the S where the wheels hit the stop, if before ±180 | teleop `max_angle` in `fsae_params.yaml` | 180.0 |

The two sides need separate scales: the firmware maps −180 … 0 onto 1403 µs of servo pulse
but 0 … +180 onto only 847 µs.

### 3b. Geometry

| Value | How | Launch argument | Placeholder now |
|---|---|---|---|
| Wheelbase | tape, rear axle centre to front axle centre | `plant_lf` = wheelbase − 0.14 | 0.86 (from a 1.00 m CAD value, UNVERIFIED) |
| ZED lens ahead of the rear axle | tape; only if the camera mount has moved since 2026-09-30 | `plant_lr` (and the URDF `camera_joint` plus its inverse) | 0.14 |

### 3c. Optional (later speed work, not needed for this test)

- Steering response time from a step command (sets `plant_tau_delta`, now 0.08 s, a simulation
  vehicle value, UNVERIFIED).
- Throttle % → acceleration, for when the NMPC drives the throttle.

### 3d. Make the values permanent

- [ ] Try them first as launch arguments, e.g.
  ```bash
  ros2 launch fsae_bringup nmpc_gokart.launch.py auto_steer_scale_left:=2.4 \
      auto_steer_scale_right:=3.1 plant_max_steer_deg:=22 plant_lf:=0.87
  ```
- [ ] Then change the defaults in `common/fsae_bringup/launch/nmpc_gokart.launch.py`
  (remove the UNMEASURED notes), update the measurements table in
  `NMPC_GOKART_GROUND_TEST.md`, rebuild `fsae_bringup`, commit, and mirror to `fsae_MPCRos`.

## 4. Sensor checks with the stack running

Launch: `ros2 launch fsae_bringup nmpc_gokart.launch.py`. **For a dry run, leave the
Arduino USB unplugged**: `serial_bridge` then logs that it cannot open the port and idles,
so nothing reaches the servo.

- [ ] `ros2 topic hz /zed/zed_node/odom` around 15-20 Hz, and
  `ros2 topic echo /zed/zed_node/odom --field header.stamp` advancing.
- [ ] `ros2 topic hz /zed/zed_node/imu/data` publishing.
- [ ] Turn the kart by hand, nose left: `ros2 topic echo /zed/zed_node/imu/data --field
  angular_velocity.z` goes **positive**. If negative, pass `imu_yaw_rate_sign:=-1.0` on
  `nmpc_controller` (add it to the launch's parameter block).
- [ ] `ros2 topic hz /fsae/slam/car_position` and `/fsae/planning/selected_trajectory`
  both publishing with cones of both colours in view.
- [ ] The `nmpc_controller` log shows `v_x_src=car_odom+imu`. `last_cmd (open-loop)` means
  the odometry is not arriving.
- [ ] Push the kart forward by hand at walking pace: the logged speed reads about 1 m/s,
  not 0 and not wildly noisy.
- [ ] RViz shows the path, the green NMPC predicted path and the steering arrow.

### 4b. Shadow mode before the first NMPC-steered run

- [ ] With the kart driven by something else (the pad, or Stanley), run
  `ros2 launch fsae_bringup nmpc_shadow.launch.py`. The NMPC publishes only on the unused
  `/fsae/control/nmpc_shadow_cmd`, so it cannot steer.
- [ ] The predicted path follows the planner path and the NMPC's arrow turns the same way
  into bends as the kart. See
  [`NMPC_VALIDATION_AND_TESTING.md`](NMPC_VALIDATION_AND_TESTING.md#3-shadow-mode-on-the-kart-validate-prediction-nmpc-never-drives).
- [ ] Stop shadow mode before launching `nmpc_gokart.launch.py`: both start a node named
  `nmpc_controller`.

### Running over SSH

- RViz and the dashboard need a screen. Over plain SSH, add `use_rviz:=false use_gui:=false`
  on the Jetson and open them on a laptop on the same network with the same
  `ROS_DOMAIN_ID` (`rviz2 -d <path to nmpc_gokart.rviz or nmpc_shadow.rviz>`,
  `ros2 run fsae_control nmpc_telemetry_gui`), or plug a monitor into the Jetson.
  UNVERIFIED: the bandwidth of ROS traffic over the kart's Wi-Fi.
- Run the launch inside `tmux` so a dropped SSH session does not kill it. If it does
  die, frames stop and the ECU watchdog trips its failsafe.

## 5. First runs

- [ ] **Wheels off the ground, Arduino plugged in.** Do the go handshake with X alone:
  hold X and L2, stick centred, throttle off, 3 s until `READY`, then let go of L2.
- [ ] Hold **X + R1** with a path ahead. The wheels follow the NMPC: a bend to the left
  turns the wheels left. **If they turn the wrong way, stop** and flip `auto_steer_sign`.
- [ ] Release R1: the stick steers again. Release X: everything neutral.
- [ ] Block the camera or stop the planner: within 0.3 s the steering goes to 0 and the
  throttle is cut.
- [ ] With the planner running, the `nmpc_controller` log prints
  `Near the end of the path: speed target capped at ...` often. That is the end-of-path
  cap keeping the NMPC's planned speed to what the visible path allows; expected, and it
  does not limit the kart (the driver sets the speed).
- [ ] **On the ground at walking pace**, driver on R2, then build speed slowly. Expect the
  kart to run slightly wide in tight corners (about 0.5 m on a 6 m radius in an offline
  kinematic-model check; UNVERIFIED on the kart).

## 6. Values that may need retuning on the kart

**Measure first (section 3), then judge the steering in shadow mode (section 4b), then retune only what a symptom points at.** Every value below was tuned in simulation on a different vehicle model (dynamic, with a lateral-acceleration limit, with the NMPC also driving the speed). On the kart the model is kinematic, that limit is off, and only the steering half of the cost matters. UNVERIFIED on the kart.

### How to change one

- `nmpc_gokart` and `nmpc_shadow` read these from the `nmpc_controller:` block of `common/fsae_bringup/config/fsae_params.yaml`, not from launch arguments. Edit the YAML, rebuild `fsae_bringup` (not a symlink install), relaunch. The node reads parameters only at start-up.
- Change one value at a time, by about 20 to 30 percent, and re-check in shadow mode before steering.
- Once a value is settled, copy it into `mpc_params.py`/`nmpc_params.py` too. `control.launch.py` passes the dataclass defaults as launch arguments, which override the YAML, so the two must stay equal.

### The steering set: tuned as one set, change with care

These were tuned together. `r_rate_delta` 100 assumes the zone schedule eases the rate cost into and through corners, and the jerk term carries part of the smoothing. Changing one in isolation gives an untested combination.

| Field | Value | What it does | Symptom that points at it |
|---|---|---|---|
| `q_e_y` | 6.4 | cost on lateral offset from the path | runs wide or cuts corners: raise. Hunts side to side: lower |
| `q_e_psi` | 1.65 | cost on heading error | slow to line up after a bend: raise |
| `q_r` | 1.0 | under the NMPC, cost on the heading-error rate | overshoots the heading out of a bend: raise |
| `r_delta` | 1.8 | cost on steering angle | under-steers everywhere: lower |
| `r_rate_delta` | 100 | cost on steering rate, scaled by the zone schedule | late, lazy turn-in: lower. Twitchy wheel: raise |
| `nmpc_rjerk_delta` | 150 | cost on steering acceleration; makes wiggles expensive and smooth ramps cheap | small fast wiggles on straights: raise |
| `nmpc_rrate_zone_enabled` | true | scales `r_rate_delta` by where the kart is: straight, corner ahead, in corner | turn this off only as a diagnosis step |
| `nmpc_rrate_zone_boost_straight` | 2.0 | rate-cost multiplier on a straight | wanders on straights: raise |
| `nmpc_rrate_zone_ease_approach` | 0.80 | multiplier when a corner is in the prediction horizon | turns in late: lower |
| `nmpc_rrate_zone_floor_corner` | 0.15 | multiplier mid-corner | cannot add lock mid-corner: lower |
| `nmpc_corner_factor_k` | 27 | how fast "corner" saturates with curvature | see below |

**`nmpc_corner_factor_k` depends on the track.** The zone schedule only reaches its corner values when `k * |kappa| / (1 + k * |kappa|)` gets close to 1 at the tightest corner (`kappa` = 1 / radius). 27 suits a tightest radius of about 5 m (gives 0.84). For a different tightest radius `R`, `k ~= target * R / (1 - target)`, e.g. 0.85 at 3 m radius gives `k ~= 17`.

### Track and vehicle values

| Field | Value | Note |
|---|---|---|
| `nmpc_track_halfwidth` | 2.4 m | soft bound on lateral offset from the centreline. Set for cones about 2.5 m apart (±1.25 m), at about twice the cone half-width so it guards against leaving the track rather than acting near the cones. The track is set up by hand: measure its narrowest gap and keep the bound near 2 × (gap / 2). Lowering it towards the cones makes it active in normal driving, which is untested |
| `nmpc_alat_ceiling_enabled` | false | **keep off.** Models a lateral-acceleration limit never measured on the kart |
| `plant_*`, steering scale and sign | section 3 | measured values, not tuning |

### Only matter once the NMPC drives the throttle

`q_e_v` 1.5, `r_a_accel` 0.9, `r_a_brake` 0.6, `r_rate_a` 2.0 and `SPEED_TARGET_DEFICIT_MAX` 2.55 m/s (a constant in `nmpc_controller.py`, not a parameter) shape the speed half of the cost. In this steering-only test the driver sets the speed and the NMPC's speed command is ignored, so leave them alone until the throttle is wired.

## 7. After each session

- [ ] Note what was measured or changed in `NMPC_GOKART_GROUND_TEST.md`.
- [ ] Commit to `feat/mpc_ground_test` and mirror the changed files to `fsae_MPCRos`
  (branch `mpc-ground-test` there, same relative path under `src/fsae_autonomous/`).

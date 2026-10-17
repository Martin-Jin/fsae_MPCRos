# NMPC go-kart bring-up checklist

Everything still to do, in order, to get the steering-only NMPC running on the kart. Tick
each box. The *why* behind each item is in
[`NMPC_GOKART_GROUND_TEST.md`](NMPC_GOKART_GROUND_TEST.md); this page is the to-do list.

**Status:** the code builds and passes its unit tests and a scripted node test on a PC
(no kart, no sensors). It has **never run on the kart**. Every steering calibration value
below is a placeholder until step 3 is done.

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
| Steering lock | full lock in wheel degrees, smaller side | `plant_max_steer_deg` | 25.0 |
| S at lock | the S where the wheels hit the stop, if before ±180 | teleop `max_angle` in `fsae_params.yaml` | 180.0 |

The two sides need separate scales: the firmware maps −180 … 0 onto 1403 µs of servo pulse
but 0 … +180 onto only 847 µs.

### 3b. Geometry

| Value | How | Launch argument | Placeholder now |
|---|---|---|---|
| Wheelbase | tape, rear axle centre to front axle centre | `plant_lf` = wheelbase − 0.14 | 0.86 (from a 1.00 m CAD value) |
| ZED lens ahead of the rear axle | tape; only if the camera mount has moved since 2026-09-30 | `plant_lr` (and the URDF `camera_joint` plus its inverse) | 0.14 |

### 3c. Optional (later speed work, not needed for this test)

- Steering response time from a step command (sets `plant_tau_delta`, now 0.08 s).
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

## 5. First runs

- [ ] **Wheels off the ground, Arduino plugged in.** Do the go handshake with X alone:
  hold X and L2, stick centred, throttle off, 3 s until `READY`, then let go of L2.
- [ ] Hold **X + R1** with a path ahead. The wheels follow the NMPC: a bend to the left
  turns the wheels left. **If they turn the wrong way, stop** and flip `auto_steer_sign`.
- [ ] Release R1: the stick steers again. Release X: everything neutral.
- [ ] Block the camera or stop the planner: within 0.3 s the steering goes to 0 and the
  throttle is cut.
- [ ] **On the ground at walking pace**, driver on R2, then build speed slowly. Expect the
  kart to run slightly wide in tight corners (about 0.5 m on a 6 m radius, offline).

## 6. After each session

- [ ] Note what was measured or changed in `NMPC_GOKART_GROUND_TEST.md`.
- [ ] Commit to `feat/mpc_ground_test` and mirror the changed files to `fsae_MPCRos`
  (branch `mpc-ground-test` there, same relative path under `src/fsae_autonomous/`).

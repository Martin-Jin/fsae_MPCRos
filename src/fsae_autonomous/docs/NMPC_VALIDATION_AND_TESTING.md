# NMPC validation and testing

Four ways to check the NMPC, from no hardware to the kart driving. Only the last one lets
the NMPC move anything.

| Check | Launch / command | Hardware | Does the NMPC drive? | What it proves |
|---|---|---|---|---|
| 1. Unit tests | `colcon test --packages-select fsae_control` | none | no | maths, signs, limits, plant overrides, bench geometry |
| 2. Bench test | `nmpc_bench.launch.py` | none | **no**, its command goes nowhere | the NMPC's output for a clean, scripted state |
| 3. Shadow mode | `nmpc_shadow.launch.py` next to a driving launch | the kart, driven by something else | **no**, its command goes nowhere | the NMPC's predicted path and steering against real sensors and the real planner |
| 4. Ground test | `nmpc_gokart.launch.py` | the kart | **yes**, steering only, deadman held | the closed loop. See [`NMPC_GOKART_GROUND_TEST.md`](NMPC_GOKART_GROUND_TEST.md) and [`NMPC_GOKART_BRINGUP_CHECKLIST.md`](NMPC_GOKART_BRINGUP_CHECKLIST.md) |

For the node itself (topics, parameters, the input/output chart) see
[`MPC_NODE_DOCS.md`](../control/fsae_control/fsae_control/mpc/MPC_NODE_DOCS.md).

## 1. Unit tests

```bash
# from the workspace root
colcon build --packages-select fsae_control
source install/setup.bash
colcon test --packages-select fsae_control --pytest-args -v
colcon test-result --verbose
```

Working: every test passes. The files:

| Test file | Covers |
|---|---|
| `test_nmpc_core_math.py` | solver self-consistency: scalar vs vectorised model, Jacobians, SQP cost decrease, the Frenet round trip RViz uses |
| `test_nmpc_signs_magnitudes.py` | steering sign and size for offsets and heading errors, accel/brake sign, output limits |
| `test_nmpc_plant_overrides.py` | the `plant_*` kart overrides, the steering limit, the kinematic arc angle in a closed-loop kinematic check |
| `test_bench_scenarios.py` | bench path shapes, the random start offset, the mock pose held after the end of the path |

## 2. Bench test (no vehicle)

> **No command reaches any vehicle.**
> - The bench NMPC's command goes to `/fsae/control/nmpc_bench_cmd` (and its raw
>   acceleration to `/fsae/control/nmpc_bench_accel_cmd`). Nothing consumes either: every
>   node in `nmpc_bench.launch.py` has `/fsae/control/cmd_vel` remapped away, so even a CAN
>   or kart stack running on the same ROS network cannot receive it.
> - **It only tests whether the NMPC computes the right output** (steering sign, size,
>   smoothness, predicted path) for a given, clean state.
> - **The mocked car follows a script and never responds to the NMPC**, so it never
>   "corrects" or converges in RViz. A large steering command against a held offset is
>   the bench working, not failing.

### What the bench mocks

| | On the kart (`nmpc_gokart.launch.py`) | On the bench (`nmpc_bench.launch.py`) |
|---|---|---|
| Sensors | ZED camera, LiDAR, cone detection | none run |
| Pose (`/fsae/slam/car_position`) | SLAM pose: noise, latency, drift, occasional jumps | scripted by `mock_pose_path_publisher`, perfect: no noise, latency, drift or jumps |
| Path (`/fsae/planning/selected_trajectory`) | live planner path from the cones, changes every update | one fixed, smooth line-and-arc path from `bench_scenarios.py` |
| Speed source (v_x) | ZED odometry, differentiated | no odometry: falls back to an open-loop estimate from the node's own acceleration command (red `last_cmd (open-loop)` in the GUI) |
| Yaw rate | ZED IMU | no IMU: Δyaw/Δt of the mock pose |
| Proximity brake | cone detections | no cones, never fires |
| Closed loop | the kart moves when steered | none: nothing moves the car |
| Command path | `nmpc_cmd` → `joystick_teleop` (deadman, R1 mode, steering sign and per-side scale to ECU S units) → `serial_bridge` → Arduino | `nmpc_bench_cmd`, consumed by nothing. `joystick_teleop`, `serial_bridge`, the Arduino and CAN do not run, so **steering sign, scale and the hardware path are never tested** |
| Vehicle model | kart overrides: `plant_lf` 0.86, `plant_lr` 0.14 (UNVERIFIED wheelbase), kinematic below 8 m/s, `v_max` 3.0 / `v_min` 1.0 | built-in model, no `plant_*` overrides; the yaml's `v_max` 20 / `v_min` 1.5 |
| Display | `gocartv2` URDF, real message timing | `gocartv1` URDF; idealised timing (every topic at a steady 20 Hz) |

### Build

```bash
# from the workspace root
colcon build --packages-select fsae_control fsae_bringup fsae_visualization fsae_description
source install/setup.bash
```

### Runs

The default sweep sends the car's lateral offset back and forth (sine, `amplitude_m` 1.0,
`period_s` 8.0) along a 100 m straight at `forward_speed_mps` 3.0. `use_gui` defaults on,
`use_viz` (RViz) defaults off.

| Run | Command | Working looks like |
|---|---|---|
| Default (straight, sweep) | `ros2 launch fsae_bringup nmpc_bench.launch.py use_viz:=true` | Steering opposite in sign to the offset (car left of the path → steer right, negative), oscillating at the sweep period with a small lag. The predicted path in RViz bends back toward the line. |
| Gentle turn | `ros2 launch fsae_bringup nmpc_bench.launch.py use_viz:=true scenario:=gentle_turn turn_radius_m:=25.0 turn_arc_deg:=30.0` | Car drives the arc with zero offset (sweep off by default on curves). Steering near 0 on the straights, steady and positive (left) through the arc. |
| Sharp turn | `ros2 launch fsae_bringup nmpc_bench.launch.py use_viz:=true scenario:=sharp_turn turn_radius_m:=8.0 turn_arc_deg:=90.0` | As above, with a larger steady left angle through the arc. |
| S-curve | `ros2 launch fsae_bringup nmpc_bench.launch.py use_viz:=true scenario:=s_curve turn_radius_m:=15.0 turn_arc_deg:=45.0` | Left through the first bend, near 0 on the short straight, right through the second. No overshoot spikes at the joins. |
| Hardest | `ros2 launch fsae_bringup nmpc_bench.launch.py use_viz:=true scenario:=s_curve turn_radius_m:=8.0 turn_arc_deg:=90.0 randomize_start:=true randomize_start_max_lateral_m:=1.5 randomize_start_max_heading_deg:=20.0 sweep_on_curve:=true period_s:=6.0` | Steering always pushes back toward the path; it may sit at the 25° limit while the offset is large. No sign flips that the offset does not explain, no solver failures in the log (`NMPC safe-stop` or `compute() raised`). |

Steady arc angles on the bench come out below the kinematic `atan(L / R)`, because the
scripted pose never lets a tracking error build. That is expected for an open-loop rig;
the exact values are UNVERIFIED as a target.

Watch the command directly:

```bash
ros2 topic echo /fsae/control/nmpc_bench_cmd
```

`steering_angle` is in degrees, + = left. `speed` is the NMPC's speed request; the
mocked car ignores it.

#### Scenario options

| Argument | Default | Effect |
|---|---|---|
| `scenario` | `straight` | `straight`: flat line, isolates `e_y`. `gentle_turn` / `sharp_turn`: 20 m straight, one left arc, 20 m straight. `s_curve`: 15 m straight, left arc, 10 m straight, right arc, 15 m straight |
| `turn_radius_m`, `turn_arc_deg` | 15.0, 45.0 | arc radius and angle (both bends of the S-curve) |
| `sweep_on_curve` | on for `straight`, off for curves | the sine sweep; on a curve it is perpendicular to the local tangent |
| `amplitude_m`, `period_s`, `forward_speed_mps` | 1.0, 8.0, 3.0 | sweep size, sweep period, scripted speed along the path |
| `path_length_m` | 100.0 | length of the `straight` path |
| `randomize_start` | off | offsets the start pose's `y` and yaw by a bounded random amount (`randomize_start_max_lateral_m` 1.0, `randomize_start_max_heading_deg` 15). The offset stays for the whole run. `randomize_start_seed` (0) makes it reproducible |

#### End of the path

When the scripted distance reaches the path's length, the mocked car **holds its final
pose** (position, sweep offset and heading all frozen) and `mock_pose_path_publisher`
logs `End of path reached ... holding the final pose` once. It does not loop; restart the
launch to run again. The path keeps being published, so the NMPC keeps solving against a
stationary car and its steering settles to a constant. Curved scenarios are short (the
S-curve above is about 60 m), so lower `forward_speed_mps` for a longer run.

The NMPC's speed target drops to 0 as the car nears the end (the end-of-path cap, see
"Not done yet" in [`NMPC_GOKART_GROUND_TEST.md`](NMPC_GOKART_GROUND_TEST.md)). On the
bench the mocked car does not stop for it; watch `speed` on `nmpc_bench_cmd` fall to 0.

### What RViz shows (`use_viz:=true`)

`nmpc_bench.launch.py` starts `rviz2` with `mpc/nmpc_bench.rviz` (Fixed Frame `map`):

- **Car body:** `robot_state_publisher` serves `gocartv1.urdf.xml`. Its root is
  `base_link`, placed at the mock pose by `cone_map_viz`'s `map → base_link` transform.
- **Camera follows the car:** the view's Target Frame is `base_link`.
- **Planner path:** `/fsae/viz/centerline` (red cubes).
- **NMPC predicted path:** `/fsae/viz/nmpc_prediction` (orange line).
- **Steering arrow:** `/fsae/viz/steering_arrow`, a 2 m magenta arrow along
  `car_yaw + steering_angle`, from the bench command.

If `rviz2` does not open under WSLg (a taskbar icon but no window), run `wsl --shutdown`
from a Windows terminal and reopen. The bench runs whether or not RViz renders.

### Telemetry dashboard (`use_gui:=true`, the default)

`nmpc_telemetry_gui` shows a bird's-eye view (car, planner path, predicted path),
rolling 15 s charts of `e_y`, `e_psi` and steering, and a stat panel (`e_v`, `kappa`,
`solve_ms`, throttle/brake, `v_x` source). On the bench the `v_x` source reads red
`last_cmd (open-loop)` (no odometry, see the table above). It reads the bench command,
not `cmd_vel`. `use_gui:=false` turns it off.

## 3. Shadow mode on the kart (validate prediction, NMPC never drives)

> **The NMPC never drives in shadow mode.**
> - Its command goes to `/fsae/control/nmpc_shadow_cmd` and its raw acceleration to
>   `/fsae/control/nmpc_shadow_accel_cmd`. Nothing consumes either. It publishes nothing on
>   `cmd_vel` or `nmpc_cmd`.
> - Something else drives (Stanley, or the driver on the pad). The NMPC watches the same real inputs
>   and shows what it **would** do.

**Use it to:** check the NMPC's predicted path and steering against the real planner path,
SLAM pose, ZED odometry and IMU, at real speeds and with real noise, before letting it
steer.

`nmpc_shadow.launch.py` starts only:

- `nmpc_controller` with the kart's vehicle model (same `plant_*` values as
  `nmpc_gokart.launch.py`; the 1.00 m CAD wheelbase is UNVERIFIED), ZED odometry and IMU
  inputs, prediction and telemetry publishing on;
- `base_tf` (identity `map → odom`, so RViz has a `map` frame; `use_base_tf:=false` if the
  driving launch already runs `viz.launch.py`);
- a private `path_viz` copy whose arrow shows the NMPC's unsent steering
  (`/fsae/viz/nmpc_shadow_steering_arrow`);
- `rviz2` with `mpc/nmpc_shadow.rviz` (`use_rviz`, default on);
- `nmpc_telemetry_gui`, reading the shadow command (`use_gui`, default on).

It starts no perception, SLAM, planner, pad, serial bridge or URDF; the driving launch
provides those.

```bash
# terminal 1: the driving launch, which must also run perception, SLAM and a planner
# terminal 2:
ros2 launch fsae_bringup nmpc_shadow.launch.py                  # RViz + dashboard
ros2 launch fsae_bringup nmpc_shadow.launch.py use_gui:=false   # RViz only
ros2 topic echo /fsae/control/nmpc_shadow_cmd                   # the unsent command
```

**Working looks like:**

- The `nmpc_controller` log shows `v_x_src=car_odom+imu`. `last_cmd (open-loop)` means the
  ZED odometry is not arriving.
- The orange predicted path in RViz lies along the planner path ahead of the kart and
  bends with it.
- The NMPC arrow points into bends in the same direction the driving controller steers.
  It may differ in size: the two controllers are tuned differently.
- No `NMPC safe-stop` lines while a path and pose are flowing.

**Limits:**

- The prediction assumes the NMPC's own steering. Because the kart follows the other
  controller, the predicted path and the real path will drift apart; compare the first
  part of the prediction, not its end.
- Do not run it with `nmpc_gokart.launch.py`: both start a node named `nmpc_controller`.
- RViz and the dashboard need a display. Over SSH to the Jetson, run
  `use_rviz:=false use_gui:=false` there and open RViz and the dashboard on a laptop on the
  same network and `ROS_DOMAIN_ID`, or plug a monitor into the Jetson.
- Checked on a PC with scripted inputs only: about 140 commands in 8 s on the shadow
  topic and none on `cmd_vel`, `nmpc_cmd` or `accel_cmd`. **Never run on the kart yet
  (UNVERIFIED).**

## What the bench and shadow mode do not test

- **Convergence:** whether the kart settles onto the path under the NMPC. Only the ground
  test closes the loop.
- **The actuator conversion:** steering sign, per-side scale, the deadman and the ECU.
  Neither runs `joystick_teleop`'s NMPC mode or sends anything to the Arduino.
- **Sensor noise and latency** (bench only): shadow mode does see real sensors.
- **The kart's geometry** (bench only): the bench runs the built-in vehicle model.

For those, follow [`NMPC_GOKART_BRINGUP_CHECKLIST.md`](NMPC_GOKART_BRINGUP_CHECKLIST.md)
and [`NMPC_GOKART_GROUND_TEST.md`](NMPC_GOKART_GROUND_TEST.md).

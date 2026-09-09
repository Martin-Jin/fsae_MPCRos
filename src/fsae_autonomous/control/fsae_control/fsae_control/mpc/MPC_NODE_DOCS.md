# The NMPC controller: how it fits into ROS2

This is a practical guide to `nmpc_controller.py`: what topics it needs, what
it publishes, how to launch it, and copy-paste commands for the RViz
visualization and hardware-free bench rig that ship alongside it. For the
math (state vector, model derivation, SQP solve procedure), see
[`fsae_MPCTest`'s `docs/nmpc.md`](https://github.com/Martin-Jin/fsae_MPCTest/blob/main/docs/nmpc.md)
in the sim/tuning repo — this doc only covers the ROS2 integration side.
For the full list of hardware/sensor gaps and how each is worked around, see
[`docs/NMPC_INTEGRATION_GAPS.md`](../../../../docs/NMPC_INTEGRATION_GAPS.md)
(**read that before running this on the car**).

## What's in this folder

| File | What it is |
|---|---|
| `nmpc_core.py` | The solver itself: Frenet-frame nonlinear bicycle model, Gauss-Newton SQP, OSQP for the inner QP. Ported verbatim from the sim repo. |
| `nmpc_params.py`, `mpc_params.py` | Every tunable weight/flag (`NMPCParams`, `MPCParams` dataclasses), declared as ROS2 parameters. |
| `control_limits.py` | The handful of constants/helpers `nmpc_core.py` needs from the sim repo's LTV-QP module, lifted out so this repo doesn't need `cvxpy`/`clarabel`. |
| `nmpc_controller.py` | **The ROS2 node.** Subscribes to the path/pose/sensor topics below, calls `nmpc_core.py` once per tick, publishes the command. This doc is about this file. |
| `mock_pose_path_publisher.py` | Hardware-free bench stimulus — see "Bench-testing with no car" below. |

## How it fits into the pipeline

```
planner ──/fsae/planning/selected_trajectory──►┐
SLAM ──────/fsae/slam/car_position─────────────►│
(placeholder) /fsae/slam/car_odom ─────────────►│  nmpc_controller
/fsae/hardware/curr_vel ────────────────────────►│  (this node)
/fsae/hardware/drive_status ────────────────────►│
/fsae/perception/cone_detection ────────────────►┘
                                                   │
                                                   ├──► /fsae/control/cmd_vel ──► ack_to_can ──► CAN bus
                                                   ├──► /fsae/control/accel_cmd  (placeholder, unconsumed)
                                                   └──► /fsae/viz/nmpc_prediction_raw ──► fsae_visualization ──► RViz
```

Selected by the `controller:=nmpc` launch arg (default is `stanley`), so
running this node is strictly opt-in and nothing about the existing default
launch behaviour changes.

## Topics: what it needs, what it publishes

### Subscribes

| Topic | Type | Required? | Notes |
|---|---|---|---|
| `/fsae/planning/selected_trajectory` | `geometry_msgs/PoseArray` | **Required** | The planner's centreline. Must have ≥2 points and be refreshed at least every `PATH_TIMEOUT` (0.5 s), or the node safe-stops. |
| `/fsae/slam/car_position` | `geometry_msgs/Pose` | **Required** | `x`, `y` in `.position`; **yaw in radians is stuffed into `.orientation.w`** (repo convention, not a real quaternion — see gap A5). No solve happens until at least one message arrives. |
| `/fsae/slam/car_odom` | `nav_msgs/Odometry` | Optional (placeholder) | No publisher exists in this repo yet. Preferred source for `v_x`/`v_y`/yaw rate when present — see gaps A1/A2/A3/A7. |
| `/fsae/hardware/curr_vel` | `ackermann_msgs/AckermannDriveStamped` | Optional (placeholder) | 2nd-choice `v_x` source; this topic already exists in the repo's naming convention but nothing publishes it yet. |
| `/fsae/hardware/drive_status` | `ackermann_msgs/AckermannDriveStamped` | Optional | 3rd-choice `v_x` source, from `can_decoder`'s 1 m/s-resolution CAN byte. |
| `/fsae/perception/cone_detection` | `fsae_interfaces/ConeDetection` | Optional | Proximity emergency-brake input, car-local frame. Empty/absent just makes the brake a no-op. |

If none of `car_odom`/`curr_vel`/`drive_status` are publishing (true today
outside a bench rig), `v_x` falls back to the node's own last commanded
speed — open-loop, degrades gracefully, does not block the node from running.

### Publishes

| Topic | Type | Notes |
|---|---|---|
| `/fsae/control/cmd_vel` | `ackermann_msgs/AckermannDriveStamped` | The actual command: speed (m/s) + steering (deg). Consumed by `ack_to_can`. |
| `/fsae/control/accel_cmd` | `ackermann_msgs/AckermannDriveStamped` | Placeholder (gap B1) — the NMPC's raw signed acceleration in `.drive.acceleration`. Nothing consumes this yet; it exists so the value isn't silently discarded. |
| `/fsae/viz/nmpc_prediction_raw` | `geometry_msgs/PoseArray` | RViz visualization only, gated by `nmpc_publish_prediction_enabled` (default off, see below). `"map"`-frame Cartesian conversion of the predicted horizon. |

## Running it

```bash
colcon build --packages-select fsae_control
source install/setup.bash
ros2 launch fsae_bringup control.launch.py controller:=nmpc
```

`controller:=stanley` (the default) is unchanged from before this port. Any
`MPCParams`/`NMPCParams` field (69 + 24 of them) is also a launch argument,
auto-generated from the dataclasses (not hand-written), so a weight can be
overridden directly:

```bash
ros2 launch fsae_bringup control.launch.py controller:=nmpc nmpc_q_e_y:=12.0
```

To drive against a precomputed CSV path instead of the live planner topic:

```bash
ros2 launch fsae_bringup control.launch.py controller:=nmpc path_map_path:=/path/to/raceline.csv
```

## Visualizing the predicted trajectory in RViz

Off by default (zero added per-tick cost when unset). Turn it on with:

```bash
ros2 launch fsae_bringup control.launch.py controller:=nmpc nmpc_publish_prediction_enabled:=true
```

Then, separately, start the visualization nodes and RViz:

```bash
ros2 launch fsae_bringup viz.launch.py
rviz2
```

In RViz: set **Fixed Frame** to `map`, then **Add → By topic** and add a
`MarkerArray` display for each of:

- `/fsae/viz/centerline` — the planner's chosen path (already existed, red cubes)
- `/fsae/viz/nmpc_prediction` — the NMPC's own predicted trajectory (new, orange line)

Watching both together shows the planned path and what the controller
actually intends to do about it, side by side, updating live at 20 Hz.

`viz.launch.py` only starts the marker-publishing nodes
(`cone_map_viz`/`path_viz`/`pursuit_viz`/`base_tf`) — it does not open an
RViz window itself; run `rviz2` separately as shown above.

## Bench-testing with no car

`mock_pose_path_publisher.py` publishes a fixed straight reference path plus
a car pose whose lateral offset sweeps back and forth (a sine wave
perpendicular to the path, yaw held fixed at the path's own heading so the
sweep isolates `e_y` alone, not a combined `e_y`+`e_psi` disturbance). This
lets `nmpc_controller` run and be watched with **no car, camera, CAN bus, or
perception/planning/SLAM node running at all**.

```bash
colcon build --packages-select fsae_control fsae_bringup
source install/setup.bash
ros2 launch fsae_bringup nmpc_bench.launch.py use_viz:=true
```

Optional sweep overrides:

```bash
ros2 launch fsae_bringup nmpc_bench.launch.py use_viz:=true \
    amplitude_m:=2.0 period_s:=6.0 forward_speed_mps:=2.0
```

Watch the response directly:

```bash
ros2 topic echo /fsae/control/cmd_vel
```

`steering_angle` should oscillate out of phase with the swept lateral
offset, tracking `period_s`'s timescale with some lag from the MPC's own
prediction horizon. With `use_viz:=true`, add the same two RViz Displays as
above to watch the predicted line bend toward the path and straighten as
the sweep crosses zero.

**This is not a closed-loop plant simulation.** The mocked pose is an
open-loop scripted trajectory; nothing consumes `/fsae/control/cmd_vel` to
move the mocked car. It validates only "does the controller react correctly
to a given instantaneous state," not the full closed loop. It also doesn't
replace `test_nmpc_signs_magnitudes.py`'s automated pytest sign/magnitude
checks (those call `NMPCController.compute()` directly, no ROS graph at
all) — this is the live, ROS-topic-level, human-in-the-loop counterpart, for
manual bring-up/demo/debugging.

## Running the tests

```bash
colcon build --packages-select fsae_control
source install/setup.bash
colcon test --packages-select fsae_control --pytest-args -v
colcon test-result --verbose
```

- `test_nmpc_core_math.py` — solver self-consistency: model parity between
  the scalar and vectorised rollout paths, forward-vs-central-difference
  Jacobians, SQP cost monotonic convergence, and the `xy_at()`/`project()`
  Frenet round trip the RViz visualization depends on.
- `test_nmpc_signs_magnitudes.py` — behavioral contract tests: correct
  steering sign/magnitude for a lateral or heading offset, correct
  accel/brake sign for a speed error, output limits respected under
  adversarial input.

## Before running any of this on the real car

Read [`docs/NMPC_INTEGRATION_GAPS.md`](../../../../docs/NMPC_INTEGRATION_GAPS.md)
in full. The short version: several of this controller's inputs
(`v_x`/`v_y`/yaw rate, an acceleration command channel) have no real sensor
or CAN channel in this repo yet and fall back to a documented degraded
estimate or placeholder. None of that blocks it from running (bench or
sim), but it does mean the tuning weights and a few sign conventions are
unverified against the physical car until that document's bring-up ladder
is followed.

# fsae_control

## What this is

This is the steering/speed controller for the car, built for ROS2. It uses a
**nonlinear Model Predictive Control (NMPC)** controller ported from this
project's separate simulator repo — instead of just reacting to where the
car is right now, it looks about a second ahead, tries out several "if I
steer/accelerate like this" plans against a model of how the car actually
moves, and picks whichever one stays closest to the intended path while
still being smooth on the wheel and pedals.

This repo intentionally only tracks the files directly relevant to the
controller and its config/launch wiring — not the rest of the car's ROS2
workspace. Everything here mirrors its file's exact relative path inside the
full `fsae_autonomous` workspace (e.g. this repo's
`src/fsae_autonomous/control/fsae_control/...` is that workspace's
`control/fsae_control/...`), so a diff against that workspace is direct.

## Status: replaces an earlier, different port in this repo's history

An earlier version of this repo (see `git log`) contained a **different**
controller — a linear time-varying MPC (`MPCController`, `cvxpy`-based) in
its own `control_utils.py`, wired up by a top-level `mpc_controller.py`. That
work is **superseded by this NMPC port**, not merged with it:

- **`control_utils.py` has been replaced.** It no longer contains
  `MPCController` — it's now a different file entirely (see below), ported
  verbatim from the same simulator repo the NMPC itself comes from.
- **`mpc_controller.py` (the old top-level node) and
  `test/test_mpc_controller.py` are still present in this commit but are
  now broken** — both import `MPCController`/`MAX_STEER_RAD`/`MAX_ACCEL`/
  `MAX_BRAKE` from `control_utils.py`, none of which exist there any more.
  They are left in place rather than deleted so the old work stays visible
  and diffable in this commit, but they will not import, build, or run as
  they stand. Recommended follow-up: delete both (the old `MPCController`
  is still fully recoverable via `git log`/`git show` on this repo if it's
  ever needed again), or restore them under a renamed path if the LTV-QP
  approach is wanted again alongside the NMPC.

## What's in here

- **`control/fsae_control/fsae_control/mpc/nmpc_core.py`** — the NMPC
  solver itself: a Frenet-frame nonlinear bicycle-model plant, a
  Gauss-Newton SQP solve (OSQP for the inner QP), delay compensation, and
  an adaptive-gain schedule for the steering-rate cost. Ported verbatim
  from the simulator repo's `fsae_planning/control/fsae_control/fsae_control/mpc/nmpc_core.py`
  — only its import of `mpc_core.py` (the *other* MPC, the LTV-QP one, which
  this repo does not carry) is redirected to `control_limits.py` below.
- **`control/fsae_control/fsae_control/mpc/control_limits.py`** — the
  handful of constants and weight-shaping helper functions `nmpc_core.py`
  needs from the simulator's LTV-QP module, lifted out on their own so this
  repo doesn't need `cvxpy`/`clarabel` at all (`osqp` alone is enough for
  the NMPC path).
- **`control/fsae_control/fsae_control/mpc/mpc_params.py`,
  `nmpc_params.py`** — the ~92 tunable weights/flags (`MPCParams`,
  `NMPCParams` dataclasses), declared as ROS2 parameters and overridable
  from `fsae_params.yaml` or the launch command line.
- **`control/fsae_control/fsae_control/mpc/nmpc_controller.py`** — the
  ROS2 node. Subscribes to the planned path and the car's live position,
  calls the NMPC once per 50 ms tick, and publishes the resulting
  steering/speed command. Unlike the sim-side node this is based on, it is
  NMPC-only (no LTV-QP fallback) and `cmd_vel`-only (no FSDS-simulator
  direct-command mode) — see its own module docstring.
- **`control/fsae_control/fsae_control/control_utils.py`** — plain
  Python/NumPy helpers the node above uses for its target-speed logic
  (`curvature_speed`, `dynamic_speed_cap`, `tracking_error_speed_gate`) and
  CSV track-file loaders. No ROS dependency of its own. This is a different
  file from the pre-NMPC version of this repo — see "Status" above.
- **`control/fsae_control/package.xml`, `setup.py`** — the ROS2 package
  manifest and entry points (`nmpc_controller` alongside the existing
  Stanley `controller` entry point).
- **`common/fsae_bringup/config/fsae_params.yaml`,
  `common/fsae_bringup/launch/control.launch.py`** — the launch-time
  wiring. `controller:=stanley` (default, unchanged behaviour) or
  `controller:=nmpc` selects which node runs; every `MPCParams`/
  `NMPCParams` field is also a launch argument.
- **`requirements.txt`** — adds `osqp` (pip-only, no rosdep key), the one
  new solver dependency the NMPC needs.
- **`docs/NMPC_INTEGRATION_GAPS.md`** — the important one. A full list of
  every input the NMPC needs that the car's current sensors/CAN bridge
  cannot yet supply (speed, yaw rate, lateral velocity, an acceleration
  command channel, ...), how each is worked around for now (a placeholder
  topic, a degraded estimate, or an explicit "not done yet"), and what
  closing each gap properly would take. **Read this before running the
  NMPC controller on the car.**
- **RViz visualization of the NMPC's predicted trajectory** (default off,
  `nmpc_publish_prediction_enabled`): `nmpc_core.py`'s `PathReference.xy_at()`
  converts the predicted horizon back to Cartesian; `nmpc_controller.py`
  publishes it as a `PoseArray` on `/fsae/viz/nmpc_prediction_raw` (`map`
  frame); `visualization/fsae_visualization/.../visualise_trajectories.py`
  republishes it as an orange `LINE_STRIP` `MarkerArray` on
  `/fsae/viz/nmpc_prediction`, alongside the pre-existing
  `/fsae/viz/centerline` (the planner's own path). Zero added cost when
  disabled (the default).
- **A hardware-free bench rig**
  (`control/fsae_control/fsae_control/mpc/mock_pose_path_publisher.py` +
  `common/fsae_bringup/launch/nmpc_bench.launch.py`): publishes a reference
  path plus a car pose, so `nmpc_controller`'s actual command response can
  be watched live with no car/camera/CAN/perception/planning/SLAM running
  at all — `ros2 launch fsae_bringup nmpc_bench.launch.py use_viz:=true`.
  Not a closed-loop plant simulation (the mocked pose doesn't react to the
  commanded output) and not a replacement for
  `test_nmpc_signs_magnitudes.py`'s automated sign/magnitude checks — a
  live, human-in-the-loop counterpart to them.
- **A test-path scenario library**
  (`control/fsae_control/fsae_control/mpc/bench_scenarios.py`): the bench
  rig's `scenario` param selects `straight` (default, unchanged), a
  `gentle_turn`/`sharp_turn` (constant-radius arc, same code path, different
  radius/arc numbers), or an `s_curve` (two opposite-sign arcs). An
  independent `randomize_start` axis offsets the car's initial pose from
  the path start by a bounded, seeded-reproducible random amount. See
  `control/fsae_control/fsae_control/mpc/MPC_NODE_DOCS.md`'s "Test
  scenarios" section for the full param table and example commands.
- **A live telemetry GUI**
  (`control/fsae_control/fsae_control/mpc/nmpc_telemetry_gui.py`): a small
  matplotlib dashboard — a bird's-eye triangle car marker plus the planner
  path and predicted trajectory, scrolling `e_y`/`e_psi`/steering strip
  charts (a bounded rolling window, not an ever-growing plot), and a stat
  panel including the active `v_x` fallback source, colour-coded so a
  placeholder source is obvious rather than silently shown as a real
  reading. Subscribes to five standard topics with **no mock-vs-live
  branching** — it works identically in bench mode
  (`nmpc_bench.launch.py use_gui:=true`, on by default there) and live mode
  (`autonomous.launch.py controller:=nmpc use_gui:=true`). Reads a new
  `/fsae/viz/nmpc_telemetry` topic (`std_msgs/String`, JSON — see
  `nmpc_params.py`'s `nmpc_publish_telemetry_enabled`, default off, same
  zero-cost-when-disabled convention as the RViz prediction publish above).
  See `MPC_NODE_DOCS.md`'s "Live telemetry GUI" section for the full
  command set.

## How to use it

### Requirements
- ROS2 (developed against Jazzy)
- Python packages: `numpy`, `scipy`, `osqp`

Install the Python dependencies if they're not already present:
```bash
pip install numpy scipy osqp --break-system-packages
```

### Running the controller
This package is meant to sit inside a full ROS2 colcon workspace (alongside
the rest of the car's packages — path planner, localization, CAN bridge,
etc.), since `nmpc_controller.py` depends on messages published by those. It
subscribes to:
- `/fsae/planning/selected_trajectory` — the path to follow
- `/fsae/slam/car_position` — the car's current position/heading
- `/fsae/slam/car_odom`, `/fsae/hardware/curr_vel`, `/fsae/hardware/drive_status`
  — speed/yaw-rate feedback, in priority order (see
  `docs/NMPC_INTEGRATION_GAPS.md` gaps A1-A3 — the first of these with an
  actual publisher wins; today none of the first two exist, and the node
  degrades accordingly)
- `/fsae/perception/cone_detection` — proximity e-brake

and publishes to:
- `/fsae/control/cmd_vel` — the steering/speed command
- `/fsae/control/accel_cmd` — the NMPC's raw acceleration command (see
  `docs/NMPC_INTEGRATION_GAPS.md` gap B1 — nothing consumes this yet, it
  exists so the value isn't silently discarded)

Build and run it like any other ROS2 Python node:
```bash
colcon build --packages-select fsae_control
source install/setup.bash
ros2 launch fsae_bringup control.launch.py controller:=nmpc
```
(`controller:=stanley`, the default, is unchanged from before this port.)

### Running the tests
`control/fsae_control/test/test_nmpc_core_math.py` (solver self-consistency:
model parity, Jacobians, SQP convergence, the `xy_at()`/`project()` Frenet
round trip) and `test_nmpc_signs_magnitudes.py` (behavioral sign/magnitude
checks) cover the NMPC port; the old `test_mpc_controller.py` tested the
now-removed LTV-QP `MPCController` and no longer applies (see "Status"
above).

```bash
colcon build --packages-select fsae_control
source install/setup.bash
colcon test --packages-select fsae_control --pytest-args -v
colcon test-result --verbose
```

## A couple of things worth knowing

Nearly everything worth knowing is in `docs/NMPC_INTEGRATION_GAPS.md` in
detail — this is just the headline version:

- **This car currently has no direct speed or yaw-rate sensor.** The node
  falls back through `/fsae/hardware/curr_vel` -> `/fsae/hardware/drive_status`
  -> its own last commanded speed for longitudinal speed, and to a
  finite-differenced yaw estimate for yaw rate, and defaults lateral
  velocity to zero. All three are documented compromises, not silent ones —
  see gaps A1-A3.
- **There is no acceleration command channel to the car.** The CAN bridge
  (`ack_to_can.py`, outside this repo) rejects negative acceleration
  outright and silently keeps the last good frame on any rejected one. The
  node works around this by converting the NMPC's acceleration output into
  a speed target itself (gap B3), and clamps every output field before
  publishing so a bad tick can never get silently dropped and leave the car
  stuck on a stale command (gap B6).
- **The tuning weights (`mpc_params.py`/`nmpc_params.py`) were tuned
  offline, in a separate simulator project, against the simulated car's
  own physical parameters** — not the real vehicle's. See gap group D in
  `docs/NMPC_INTEGRATION_GAPS.md` before trusting any of them on the car
  without re-validation.
- **No track data or telemetry logging exists in this repo** (gaps C2,
  F1-F3) — the controller falls back to deriving a target speed live from
  path curvature instead of a precomputed profile, and nothing is logged to
  CSV yet.

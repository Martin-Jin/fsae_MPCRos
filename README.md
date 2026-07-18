# fsae_control

## What this is

This is the steering/speed controller for the car, built for ROS2. It uses
Model Predictive Control (MPC) — instead of just reacting to where the car
is right now, it looks about a second and a quarter ahead, tries out several
"if I steer/accelerate like this" plans, and picks whichever one stays
closest to the intended path while still being smooth on the wheel and
pedals.

This repo intentionally only tracks the files directly relevant to the MPC
controller and its test suite — not the rest of the car's ROS2 workspace.

## What's in here

- **`control_utils.py`** — the actual controller (`MPCController` class).
  Given the path to follow and the car's current position/heading/speed, it
  returns a steering command and a throttle/brake command. This is plain
  Python/NumPy plus the `cvxpy` optimizer — it has no ROS dependency on its
  own.
- **`mpc_controller.py`** — the ROS2 node that wires the controller above
  into the rest of the car's software. It subscribes to the planned path and
  the car's live position, calls the controller once per position update,
  and publishes the resulting steering/speed/acceleration command.
- **`test_mpc_controller.py`** — a `pytest` suite that exercises the
  controller directly (no ROS2 needed) with a series of hand-built
  scenarios — car offset left/right of the path, heading errors, corners,
  speeding up/braking, sudden solver failures — and checks the output
  behaves sensibly (correct direction, right ranges, safe fallbacks).
- **`package.xml`** — the ROS2 package manifest (name, dependencies,
  maintainer info).

## How to use it

### Requirements
- ROS2 (developed against Jazzy)
- Python packages: `numpy`, `scipy`, `cvxpy`, and at least one of
  `osqp` / `clarabel` (the solvers `cvxpy` uses under the hood)

Install the Python dependencies if they're not already present:
```bash
pip install numpy scipy cvxpy osqp clarabel --break-system-packages
```

### Running the controller
This package is meant to sit inside a full ROS2 colcon workspace (alongside
the rest of the car's packages — path planner, localization, CAN bridge,
etc.), since `mpc_controller.py` depends on messages published by those. On
its own, it subscribes to:
- `/fsae/planning/selected_trajectory` — the path to follow
- `/fsae/slam/car_position` — the car's current position/heading

and publishes to:
- `/fsae/control/drive`, `/fsae/control/drive_vis`, `/fsae/control/cmd_vel`
  — the resulting steering/speed/acceleration command

Build and run it like any other ROS2 Python node:
```bash
colcon build --packages-select fsae_control
source install/setup.bash
ros2 run fsae_control mpc_controller
```

### Running the tests
The test suite only needs the Python dependencies above — it calls the
controller directly and doesn't require the rest of the ROS2 workspace to
be running.
```bash
colcon build --packages-select fsae_control
source install/setup.bash
colcon test --packages-select fsae_control --pytest-args -v
colcon test-result --verbose
```

## A couple of things worth knowing

- **This car currently has no direct speed/turn-rate sensor, cone map, or
  live "go" signal.** `mpc_controller.py` works around these gaps (see the
  `NOTE (missing input)` comments in that file for exactly what's missing
  and what would need to change to remove each workaround).
- **Braking commands currently don't reach the car.** There's a known issue
  further downstream (outside this repo) where negative acceleration values
  get silently dropped before reaching the car's hardware — so today the
  car can be commanded to speed up, but not to actively brake through this
  pipeline. This is flagged in `mpc_controller.py` but needs to be fixed
  elsewhere.
- **The tuning weights in `control_utils.py` (`Q_diag`/`R_diag`/`R_rate_diag`)
  were tuned offline**, in a separate simulator project, and are simply
  hardcoded here — nothing in this repo re-tunes them automatically.
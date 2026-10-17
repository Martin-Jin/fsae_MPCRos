# fsae_control NMPC (mirror of fsae_autonomous)

This repo tracks only the files of the `fsae_autonomous` ROS 2 workspace that make up the
**nonlinear model predictive controller (NMPC)** and its config, launch and docs. Every
file sits at its exact relative path under `src/fsae_autonomous/`, so a diff against that
workspace is direct.

The NMPC looks about a second ahead: it tries steering and acceleration plans against a
vehicle model and picks the one that stays closest to the planned path while staying
smooth. Its weights and most of its vehicle constants were tuned in simulation and are
**UNVERIFIED on the car or the kart**; see `docs/NMPC_INTEGRATION_GAPS.md`.

## Branches

| Branch here | Mirrors `fsae_autonomous` | Contents |
|---|---|---|
| `main` | `main` + the NMPC port | the NMPC for the car (CAN path) |
| `mpc-ground-test` | `feat/mpc_ground_test` | the port on top of `feat/teleop-node-ground-testing`, plus the steering-only go-kart test, shadow mode and the bench test. Shared files such as `fsae_params.yaml` and `autonomous.launch.py` are that branch's versions |

Every change on `feat/mpc_ground_test` is mirrored here to `mpc-ground-test`, and back.

## Where to start (`mpc-ground-test`)

| Doc | For |
|---|---|
| `src/fsae_autonomous/docs/NMPC_GOKART_BRINGUP_CHECKLIST.md` | the to-do list: software, firmware checks, measurements, first runs |
| `src/fsae_autonomous/docs/NMPC_GOKART_GROUND_TEST.md` | what the kart test runs (steering only), pad controls, measurements used and still needed |
| `src/fsae_autonomous/docs/NMPC_VALIDATION_AND_TESTING.md` | unit tests, the bench test (no vehicle) and shadow mode (the NMPC watches while something else drives) |
| `src/fsae_autonomous/control/fsae_control/fsae_control/mpc/MPC_NODE_DOCS.md` | the node: topics, parameters, the input/output flow chart, launches |
| `src/fsae_autonomous/docs/NMPC_INTEGRATION_GAPS.md` | every input or channel the car cannot supply yet, and the workaround |
| `src/fsae_autonomous/docs/ARCHITECTURE.md` | the whole stack, with the NMPC in its three flow charts |

## Launches

```bash
ros2 launch fsae_bringup control.launch.py controller:=nmpc   # car, CAN path
ros2 launch fsae_bringup nmpc_gokart.launch.py                # kart, steering only, deadman
ros2 launch fsae_bringup nmpc_shadow.launch.py                # kart, NMPC never drives
ros2 launch fsae_bringup nmpc_bench.launch.py use_viz:=true   # no vehicle, no command sent
```

## What's in here

- `control/fsae_control/fsae_control/mpc/`
  - `nmpc_core.py`: the solver (Frenet bicycle model, Gauss-Newton SQP, OSQP).
  - `nmpc_controller.py`: the ROS 2 node.
  - `mpc_params.py`, `nmpc_params.py`: every weight and flag, as ROS parameters.
  - `control_limits.py`: steering/acceleration limits and weight-shaping helpers.
  - `mock_pose_path_publisher.py`, `bench_scenarios.py`: the bench test stimulus.
  - `nmpc_telemetry_gui.py`: live dashboard.
  - `*.rviz`: RViz configs for the bench, kart and shadow launches.
- `control/fsae_control/fsae_control/control_utils.py`: target-speed helpers.
- `control/fsae_control/test/`: unit tests.
- `control/fsae_can_bridge/fsae_can_bridge/joystick_teleop.py` (`mpc-ground-test`): the
  NMPC steering mode used on the kart.
- `common/fsae_bringup/`: `fsae_params.yaml` and the launch files above.
- `docs/`: the docs listed above, plus `docs/diagrams/` (SVG renders of the flow charts).
- `requirements.txt`: adds `osqp`.

## Requirements

- ROS 2 Jazzy (the kart's Jetson runs its own ROS 2 install; see the checklist).
- Python: `numpy`, `scipy`, `osqp` (`pip install -r requirements.txt`).

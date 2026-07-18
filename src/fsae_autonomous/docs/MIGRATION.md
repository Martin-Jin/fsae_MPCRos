# Migration summary: `autonomous` → `fsae_autonomous`

Summary of the refactor from the old `autonomous` repo into this clean rebuild.
Stages 1-3 are done and the stack has been colcon-built and system-tested on the Jetson;
issues found during bringup are logged in `MIGRATION_BUGS.md`. (The original plan lived in
`refactor plan.txt` on the Jetson; it was never committed to this repo.)

## 1. Structure

- **No top-level `src/` wrapper.** This repo is cloned into a workspace's `src/`
  (`~/ros2_ws/src/fsae_autonomous/`). The old repo *was* the workspace.
- **15+ packages → 9**, grouped into 5 navigation folders (not ROS packages; colcon
  ignores them): `common/`, `perception/`, `planning/`, `control/`, `visualization/`.
- Manifests target **Humble** (format-3, Jazzy-friendly).

## 2. Package mapping

| Old | New | Change |
|---|---|---|
| `fsae_interfaces` | `common/fsae_interfaces` | moved |
| `fsae_control` | `control/fsae_control` | moved |
| `fsae_planning` | `planning/fsae_planning` | moved (1 planner dropped) |
| `fsae_perception/zed_perception` | `perception/fsae_camera` | renamed + moved |
| `fsae_perception/fsae_slam` | `perception/fsae_slam` | moved up |
| `gocart/gocart_bringup` | `common/fsae_bringup` | renamed + moved |
| `gocart/gocart_description` | `common/fsae_description` | renamed + moved |
| `gocart/gocart_control` + `gocart_driver` + `CanTalk` | `control/fsae_can_bridge` | **merged** (CanTalk now vendored as `candapter_node`, launch-commented) |
| `scrutineering` | `planning/fsae_mission_control` | replaced/generalised (port-as-is for now) |
| `visualisation/{base_tf, cone_map_foxglove_visualiser, path_planning_visualiser, pure_pursuit_visualiser}` | `visualization/fsae_visualization` | **merged (4→1)** |
| (none) | `perception/fsae_lidar` | new — camera-LiDAR **fusion** node (sphere-crop milestone; ported from the old `fsae_lidar_fusion` on the `lidar_ground_removal` branch) |
| `gocart/trolly_description` | `common/fsae_description` (URDF + meshes) | **partially ported** — trolley URDF + meshes folded into `fsae_description` as the **default** platform (the rig autonomy is actually tested on); standalone package not recreated |
| `third_party/`, FSDS sim, foxglove-bridge submodule | — | **removed** |

## 3. Interfaces

- **`Detections` → `ConeDetection`** (pure rename, fields unchanged). Propagated to every
  consumer: camera, slam, planning (`fasttube_without_kalman`), visualisation.
- **Pruned (Stage 4, done)** — 8 msgs + 1 srv with zero live references removed:
  `AllStates`, `BoundaryStamped`, `OccupancyGrid`, `Pulse`, the whole
  `Cone`/`ConeMap`/`ConeMapStamped`/`ConeStamped` family, and `srv/CANSendReq`.
  Dropping `AllStates` (its only `ackermann_msgs` user) also removed the `ackermann_msgs`
  dependency from the package. Remaining defs: `AllTrajectories`, `CAN`, `CANStamped`,
  `ConeDetection`, `HardwareStates(Stamped)`, `MissionStates(Stamped)`, `Track`.

## 4. Topics — `/fsae/<subsystem>/<signal>`

Dropped the legacy `moa/` prefix, the `zed/` prefix, and bare/absolute names. Key renames:

| Old | New |
|---|---|
| `zed/cone_detection` (camera) / `cone_detection` (consumers) | `/fsae/perception/cone_detection` |
| `zed/image` | `/fsae/perception/image` |
| `zed/car_position` / `car_position` | `/fsae/slam/car_position` |
| `left_track` / `right_track` | `/fsae/slam/left_track` / `right_track` |
| `moa/selected_trajectory` / `selected_trajectory` | `/fsae/planning/selected_trajectory` |
| `cmd_vel`, `cmd_val`, `drive`, `drive_vis` | `/fsae/control/cmd_vel`, `.../cmd_vel`, `.../drive`, `.../drive_vis` |
| `pub_raw_can` / `/raw_can` | `/fsae/hardware/can_tx` / `can_rx` |
| `/battery_state`, `/drive_status`, `/glv_state` | `/fsae/hardware/{battery_state,drive_status,glv_state}` |
| `as_status`, `moa/curr_vel`, `mission_status`, `moa/hardware_state` | `/fsae/mission/as_status`, `/fsae/hardware/curr_vel`, `/fsae/mission/mission_status`, `/fsae/hardware/hardware_state` |
| `visualization_*`, `control_visualization` | `/fsae/viz/{cones,car,detections,centerline,trajectories,control}` |

**Inconsistencies fixed by the rename:** planning published `moa/selected_trajectory` but
control subscribed `selected_trajectory` (never connected); the `cmd_val` typo; the camera
published `zed/cone_detection` while consumers used bare `cone_detection`.
**TF frames:** `global_frame`→`map`, `local_frame`→`base_link`; tree `map → odom → base_link`.

## 5. Config

- Central **`common/fsae_bringup/config/fsae_params.yaml`** (single source of truth, keyed
  by node name). Hardcoded values extracted from code: Stanley gains/velocity, planner
  look-forward/plot, SLAM KF + prune params, CAN ids/thresholds, mission/mock params.
- Several nodes were **renamed** so their internal node name matches their YAML key
  (ROS loads params by node name): e.g. `Stanley_Controller`→`stanley_controller`, the 3
  planners given distinct names, `stimulus_node`→`mock_stimulus`, `CAN_decoder`→`can_decoder`.

## 6. Dropped / removed

Foxglove (entirely — viz reimplemented as RViz MarkerArray), FSDS simulator, `third_party/`,
`simple_centerline_planner`, the alt controllers (`trajectory_follower_p_controller`,
`pure_pursuit`), viz demo nodes + `image_throttler`, scrutineering's `test_node`.

## 7. Launches (Stage 3)

Per-event mission launches composed from reusable subsystem launches (in `fsae_bringup/launch/`):
- **Missions:** `autonomous` (planner + use_viz args, auto-skips SLAM for the no-kalman
  fallback), `scrutineering`, `teleop`, `bench`.
- **Subsystems:** `description`, `perception`, `slam`, `planning`, `control`, `can`, `viz`.

## 8. Known bugs — ported faithfully, NOT fixed (team to decide)

- `stanley_controller`: `target_speed` read without `.double_value` in `__init__` (harmless; overwritten before use).
- `can_decoder`: ~~`AckermannStamped` import~~ **FIXED** → `AckermannDriveStamped` (see `MIGRATION_BUGS.md` Fixed). Still open: 16-bit CAN values combined with `+` instead of bit-packing.
- ~~`state_publisher`: assigns a float to a Quaternion field and never calls `sendTransform`~~ **FIXED** — identity quaternion + `sendTransform` added; now broadcasts a placeholder `odom→base_link` (see `MIGRATION_BUGS.md`).
- ~~`can_id`: code default `300` vs `0x300` in the old launch~~ — RESOLVED. This was not a
  ported bug but a **refactor regression**: the old launches all passed `0x300` (768), the
  refactor baked in the unused node default (300). Fixed to `768` in `fsae_params.yaml`. See
  `MIGRATION_BUGS.md` (Fixed).

## 9. Deferred work & tech debt (not bugs — improvements to make deliberately)

**Deferred / blocked:**
- **CanTalk** — now **vendored** as `candapter_node` (`fsae_can_bridge.candapter`) and wired to `can_tx`/`can_rx`, but left **commented out** in `can.launch.py` (opens a serial device; Jetson-only). Remaining work: uncomment + test on hardware, and confirm the USB-serial line speed. See `CANTALK_INTEGRATION.md`.
- ~~**`fsae_camera` build** — Jetson only (ZED SDK 5 + CUDA + TensorRT). Not yet compiled.~~
  **DONE** — built on the Jetson, then converted to subscribe to the zed-ros2-wrapper
  (no direct SDK linkage any more; wrapper must be in the workspace) and live-tested.
- **`fsae_lidar`** — camera-LiDAR fusion node ported (camera seed → TF-project into the `velodyne` frame → 1 m sphere crop, with RViz debug markers/cloud). Only the sphere crop (step A1) exists; ring bucketing, ground removal, clustering and circle fit are still unwritten. Standalone launches (`fsae_lidar_fusion.launch.py`, `velodyne_vlp16.launch.py`); **not yet wired into `autonomous.launch.py`**, and unexercised against real lidar data. Velodyne driver is apt (`ros-$ROS_DISTRO-velodyne`), not vendored.
- **`fsae_mission_control`** — ported as the inspection routine only; the multi-event state machine (acceleration/skidpad/autocross/trackdrive as `mission:=` params) is future work.
- **`replay.launch`** — bag → slam → planning → control for off-car (Level-3) testing; pending confirmation that rosbags exist.

**Tech debt / best practices:**
- **No command mux/arbiter** on `/fsae/control/cmd_vel` — 4 nodes can publish it; only the launch structure prevents conflict. A proper mux + e-stop gate is worth adding before real driving.
- ~~**`fasttube_planner` DEBUG override**~~ **REMOVED** — the hardcoded single-cone-colour hard-turn is deleted; one-sided frames now fall through to the real boundary logic (see `MIGRATION_BUGS.md`).
- **`fsae_slam` periodic reset** — `cone_mapper` calls `reset_map()` every 60 frames, wiping the whole map. Questionable for a persistent map (no loop closure); revisit with real SLAM.
- **TF-tree ownership (refactor-added, latent conflict)** — corrected from an earlier wrong
  note: it is **`visualise_cone_map` (a viz node)**, not `cone_mapper`, that broadcasts
  `map→base_link` (from `car_position`). `base_tf` broadcasts a placeholder `map→odom`;
  `state_publisher` `odom→base_link` (but it's the no-op above, so that edge is dead). In the
  old repo `base_tf`'s broadcaster was commented out and the viz broadcast no TF, so the old
  tree was effectively dead — this is new structure, not a regression. Today only the viz edge
  is live (so RViz works with Fixed Frame = `map`); the two-parent conflict is **latent** and
  only appears once `state_publisher` is fixed. Cleanup: one owner per edge, and move the
  ego-pose broadcast out of the viz node (viz should consume TF, never publish it).
- **Magic constants still in code** — Stanley `car_yaw - 4.71` (frame correction); `ack_to_can` Ackermann→CAN scalings (`*4`, `*100`, `0x80`).
- **Model artifacts** — `.engine` is gitignored (GPU-specific, regenerable); track the source YOLOv8 ONNX (`cone_detection_model.onnx`, currently only on the Jetson in the old repo dir) in git-LFS and back it up off the Jetson.
- **No CI / not linted** — nothing colcon-built; declared linters (flake8/pep257/copyright) never run.

**Stage 4 cleanup:** unused interfaces pruned (§3, done). Remaining: delete the old packages, archive `autonomous` → `autonomous_archive`.

## 10. Status

- Stages 1-3 done. **colcon-built and system-tested on the Jetson** — perception
  (cone detection), SLAM (`car_position`), planning (`selected_trajectory`) and RViz viz
  all confirmed carrying live data. Work committed (see `git log`).
- Bringup issues found and logged in `MIGRATION_BUGS.md`. **Bug-origin audit (applying the
  "did it work in the old repo?" test):** the refactor introduced exactly **two** true
  regressions — `centerline viz` interface (resolved) and `can_id` 768→300 (resolved this pass,
  `fsae_params.yaml` → 768). Everything else is either pre-existing (carried faithfully from the
  old repo: `can_decoder` import [now FIXED], `state_publisher`, `track_point` dead feature, `fasttube`
  debug override, magic constants), refactor-*added* but not a regression (duplicate C++ SLAM
  stub, the new TF broadcasts), or environment/toolchain (numpy 2 / setuptools / fsd_path_planning
  / numba — all resolved). So no outstanding *refactor* bugs remain; the rest are pre-existing
  items to fix on their own merits.
- `fsae_camera` has since been **converted to the zed-ros2-wrapper** (see
  `MIGRATION_BUGS.md` and the ARCHITECTURE diagrams) and rebuilt/live-tested on the Jetson.
- Next: clear the outstanding bugs; remaining Stage 4 cleanup is deleting the old packages and
  archiving `autonomous` → `autonomous_archive` (interface prune §3 now done).

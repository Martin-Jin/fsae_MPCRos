# Go-kart NMPC vs the simulator NMPC: what differs and why

The production NMPC (`src/fsae_autonomous`, branch `mpc-ground-test`) was ported from the
simulator stack (`fsae_planning` in the FSDS tree, tuned offline in `fsae_MPCTest`). The
go-kart runs it steering-only at walking pace with a ZED camera as its only motion sensor,
so several inputs, values and code paths differ from the design the simulator validated.

- **Kart-vs-default detail, with every value:** `src/fsae_autonomous/control/fsae_control/fsae_control/mpc/GOKART_DIFFERENCES.md`.
  That file may not name the simulator (production rule), so this one carries the
  simulator side of the comparison.
- **Anything listed here is UNVERIFIED on the kart** unless it says measured.

## Inputs

| | Simulator NMPC | Go-kart NMPC | Why it matters |
|---|---|---|---|
| Speed `v_x` | FSDS ground truth (`/fsae/slam/car_odom` twist from the bridge) | ZED odometry pose, differentiated (`pose_diff`) | noisier and delivered in bursts on the Jetson (arrival gaps over 0.3 s covered 7-43 % of logged runs), hence `state_timeout_s` 1.0 on the kart |
| Yaw rate | ground truth | ZED IMU, camera pitched 7.7° (0.991 scale, not corrected) | |
| Pose | `PoseStamped` with a capture stamp | `Pose` without a stamp (yaw in `orientation.w`), age from arrival time | delay compensation sees arrival age, not capture age |
| Output | acceleration and steering to the simulated car | steering only, via `joystick_teleop` to the Arduino ECU in S units; driver on the throttle | the S-per-degree scale is a placeholder (1.0); logged laps suggest about 4-5 on the left |
| Speed fallback | never used (ground truth always present) | open-loop estimate when odometry is stale | the production fallback had a runaway (fixed, see below), invisible in the simulator because it never runs there |

## Values

| Field | Simulator | Go-kart | Why |
|---|---|---|---|
| `nmpc_standstill_speed` / `_fade_speed` | 0.5 / 3.0 m/s | 0.1 / 0.3 m/s (kart launches) | designed for launching a racing car; the kart drives at 0.5-1.1 m/s, inside the band, where it cut steering to about 7 % of the path's need |
| `nmpc_track_halfwidth` | 3.35 m | 2.4 m | the kart's hand-laid track is narrower |
| `nmpc_alat_ceiling_enabled` | on | off | models the simulator's lateral-acceleration ceiling, not a property of the kart |
| `v_max` / `v_min` | car values | 3 / 1 m/s | plan for walking pace |
| Vehicle model | full-size car, dynamic above the blend band | `lr` 0.14 m (measured), `lf` 0.86 m (CAD), kinematic below 8 m/s | |

## Code fixed in production only

Found by replaying the 2026-10-18 kart rosbags (runs 3 and 4) through `nmpc_controller`
in shadow mode. None of these paths run in the simulator, so they were never exercised
there.

| Fix | Effect before |
|---|---|
| Open-loop `v_x` estimate integrates `a_cmd` over one tick | the last speed command (which leads `v_x` by `a_cmd * 0.25 s`) was fed back each tick, running the estimate to `v_max` at 5x the planned acceleration |
| Safe-stop when `compute()` returns early | the previous tick's command was published again as fresh |
| Repeated waypoints dropped from the planner path | the spline reference rejected the whole path, losing the tick |

## Open-loop replay results (rosbag, NMPC never drove)

| Check | Result |
|---|---|
| Steering sign vs Stanley (when Stanley > 3°) | 96 % agree |
| Steering size, default standstill band | 0.7° median vs 8.7° curvature need |
| Steering size, kart band | 75-80 % of curvature need; correlation with Stanley 0.67-0.72 |
| Solve time, laptop CPU | 31 ms median, 45 ms p95, 87 ms worst (50 ms tick) |

The left veer at the orange cones seen on runs 1-3 is not isolated here. Run 4 (no orange
cones) is the clean reference; run 3's overall figures match it.

## The kart track in the offline simulator

The loop the kart drove on 2026-10-18 is the offline track `gokart_night_loop_20261018`
(17 blue, 22 yellow, 1 orange cone): run 2's rosbag replayed through the production SLAM
node (`cone_landmark_mapper`, built from `src/fsae_autonomous`), its final map converted
with `fsae_MPCTest`'s `tuner/tools/rosbag_cone_map.py --slam`. Copy in
`fsae_MPCTest/fsds_simulator/tracks/`; method and results in `fsae_MPCTest`'s
`docs/guides/offline_guide.md`.

This was also the first run of the SLAM node on kart data (offline replay, not live):

| Run | SLAM result |
|---|---|
| 2, 3 | 39 cones each, the two runs agree to 0.012 m median after alignment. Cone pairs seen in one camera frame match the map to 0.011 m median (odometry-only map: 0.04-0.06 m) |
| 4 (odometry drifts about 1 m per lap) | one clean loop of 41 cones where odometry alone gave 107 (duplicated rings) |
| 1 (odometry jumps about 6 m mid-run) | fails: 77 cones, two offset loops. No relocalisation, so re-seen cones miss the association gate after the jump |

The cones were adjusted between runs, so cross-run numbers mix map error with moved cones.
The orange start-gate cones sat inside the loop, where the kart veered left on runs 1-3.

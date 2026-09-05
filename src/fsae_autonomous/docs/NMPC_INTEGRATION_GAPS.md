# NMPC integration gaps

The nonlinear MPC controller (`control/fsae_control/fsae_control/mpc/nmpc_core.py`,
ported from the sim tree's `fsae_planning` repo) needs six things about the car every
tick that this repo did not previously produce, plus one thing it cannot cleanly send.
This document lists every mismatch found while porting it, how each one is handled in
the port, and what closing it properly would take. Code carries a one-line
`# GAP <id>:` comment at each affected line; this document is the full explanation, not
the comment.

**Handling key**: *placeholder* = a topic on this repo's naming convention now exists
and is subscribed/published, but nothing (or only a partial source) produces/consumes
it yet. *compromise* = a degraded value is computed from what already exists, with no
change to any other node. *deferred* = documented, not addressed, needs a separate
piece of work (usually outside `fsae_control`) before it can be closed.

## Why this exists at all

The NMPC's per-tick entry point needs:

```
compute(path, car_pos, car_yaw, car_speed, desired_speed,
        car_yaw_rate=0.0, pose_age_s=0.0, car_vy=0.0)
```

The state vector it builds from these is
`[s, e_y, e_psi, v_x, v_y, r, delta_act, a_act]` (arc-length position, lateral error,
heading error, longitudinal speed, lateral speed, yaw rate, and two internally
integrated actuator lag states). Everything except `path`, `car_pos`, and `car_yaw`
needed a new source.

For contrast, the existing Stanley controller (`stanley_controller.py`) uses only
`(x, y, yaw)` from `/fsae/slam/car_position` and a fixed speed parameter, which is why
none of this was needed before.

---

## A — State estimation

| ID | Gap | Handling |
|---|---|---|
| A1 | No longitudinal velocity | placeholder + compromise |
| A2 | No lateral velocity | placeholder + compromise |
| A3 | No yaw rate | placeholder + compromise |
| A4 | Pose has no timestamp | compromise |
| A5 | Yaw convention unverified post-camera-frame-fix | compromise, resolve at bring-up |
| A6 | Pose is raw drifting visual odometry | deferred |
| A7 | Fallback state is not atomic across sources | resolved once A1-A3's placeholder is filled |

### A1 — No longitudinal velocity (`v_x`)

Nothing in the repo measures the car's own speed today. `/fsae/hardware/curr_vel`
(`ackermann_msgs/AckermannDriveStamped`) already exists in the repo's topic naming and
already has two subscribers (`inspection_mission.py`, `sys_status.py`), but **zero
publishers** — it has simply never been wired to anything. `can_decoder_jnano.py`
publishes a different topic, `/fsae/hardware/drive_status`, whose speed field is a
single unshifted CAN byte (1 m/s resolution, no timestamp on the value itself, and the
decoder's own comment marks it "not sure if this is needed").

`v_x` is `x0[3]` in the state vector. It sets both front and rear tyre slip angles,
the kinematic/dynamic model blend (below 1.0 m/s the plant is pure kinematic, above
2.5 m/s pure dynamic), and the `e_v` (speed-tracking) cost term. Stanley never needed
this because it uses the `target_velocity` *parameter* as `v` in its denominator, not a
measurement.

**Handling**: the node subscribes the placeholder `/fsae/hardware/curr_vel` as the
preferred source, falls back to `/fsae/hardware/drive_status` (coarse but real) if that
has no publisher, and falls back to the controller's own last commanded speed
(effectively open-loop, same assumption Stanley already makes) if neither publishes.
See `nmpc_controller.py`'s `_resolve_state()`.

**Closing it properly**: wire an actual publisher onto `/fsae/hardware/curr_vel` —
either MoTeC decoding wheel speed onto a CAN frame `can_decoder` already reads, or a
dedicated speed sensor. Once that lands, no controller change is needed.

### A2 — No lateral velocity (`v_y`)

No IMU subscription anywhere in the repo, no wheel speed sensors. A previous attempt
existed (`perception/fsae_camera/velocity/velocity.cpp`, IMU-accel integration) but it
is **not in the CMake build glob** and its own comment reads
`### THIS DOES NOT OUTPUT ACCURATE VELOCITY DATA ###`.

`v_y` is `x0[4]`. The sim-side node's own docstring warns against collapsing `(v_x,
v_y)` into a single `hypot()` speed, because that silently drops the `vy*cos(e_psi)`
term the error-state derivative needs.

**Handling**: placeholder `/fsae/slam/car_odom` (`nav_msgs/Odometry`, see below) is the
only source; with no publisher, `v_y` defaults to `0.0`. This is not a neutral
approximation, but the plant model's own kinematic/dynamic blend already assumes
`v_y ~ 0` at low speed (below `v_blend_lo = 1.0 m/s` it is pure kinematic), so the
error is smallest exactly where bring-up testing runs and grows with speed. This is the
reason the bring-up ladder (see the plan) caps speed until `car_odom` is real.

**Closing it properly**: publish `nav_msgs/Odometry` with a real lateral-velocity
estimate on `/fsae/slam/car_odom` — from an IMU, from the ZED's own VIO twist (see A3),
or from a dedicated state estimator.

### A3 — No yaw rate (`r`)

The ZED wrapper *does* publish a full twist on `/zed/zed_node/odom`
(`nav_msgs/Odometry`), but `cone_detection_node` only subscribes
`/zed/zed_node/pose` (`geometry_msgs/PoseStamped`) and keeps just x, y, and yaw.

`r` is `x0[5]` and drives `e_psi_dot = r - kappa*s_dot` — the term whose *absence* from
the older LTV bicycle model is the documented reason the NMPC was built in the first
place (see the sim tree's `docs/reference/control_mechanisms.md`).

**Handling**: placeholder `/fsae/slam/car_odom`, same topic as A2. With no publisher,
`r` is estimated by finite-differencing the pose's own yaw across the 20 Hz control
tick, with a light low-pass filter. This is noisy and one tick delayed — adequate to
get the node solving and driving at low speed, not adequate as a permanent source.
`nmpc_controller.py` tags this estimate in telemetry so a live run can be told apart
from one using a real yaw rate.

**Closing it properly**: the ZED wrapper's odom twist is already available on
`/zed/zed_node/odom` and already carries `angular.z`. The straightforward fix is a
node that republishes that (and the wrapper's linear twist, for A1/A2) onto
`/fsae/slam/car_odom` in the repo's existing `car_position`-style contract. That work
was deliberately **not** done as part of this port — it is perception-owned work, not
a controller concern, and is recorded here rather than built speculatively.

### A4 — Pose has no timestamp

`/fsae/slam/car_position` is `geometry_msgs/Pose`, not `PoseStamped`. Without a
timestamp, `pose_age_s` (how stale the pose is by the time the controller acts on it)
is unavailable, and `delay_compensation_enabled`'s nonlinear state rollforward cannot
run.

**Handling (compromise)**: the node stamps the pose with its own **arrival time** the
moment the subscription callback fires. This under-counts staleness by however long
the perception pipeline itself took to produce the message, but is otherwise a normal,
if approximate, `pose_age_s`. No message or upstream node changes.

**Closing it properly**: change `/fsae/slam/car_position` to `PoseStamped` with the
camera's own capture-time stamp (as `/fsae/perception/cone_detection` already carries,
per `cone_detection.cpp`'s `header.stamp = msg->header.stamp`). Out of scope here since
Stanley and both planners consume the unstamped message today.

### A5 — Yaw convention unverified

Yaw is packed into `orientation.w` of the `Pose` message (a repo-wide convention, not
NMPC-specific). `stanley_controller.py`'s own in-file warning says its `-4.71`
(~270°) yaw-offset correction was tuned for the ZED's *old*, pre-fix coordinate frame,
that the ZED init has since changed to `RIGHT_HANDED_Z_UP_X_FWD`, and that the
constant is now "almost certainly WRONG" — untested, left unchanged because it could
not be tested at the time.

A wrong yaw convention is far more consequential for a model-based controller than for
Stanley: Stanley's cross-track term still corrects a wrong heading over a few ticks,
while a 90° yaw error fed into the NMPC's plant model corrupts every slip-angle and
tyre-force calculation immediately.

**Handling**: the NMPC node reads the same `orientation.w` convention Stanley and the
planners already use, unmodified — no new assumption. **This is resolved on the rig**,
not in code: bring-up rung 2 (jacked up, steering only) is specifically where the yaw
sign and any residual offset get verified against physical steering direction before
any driving is attempted.

### A6 — Pose is raw drifting visual odometry

`area_memory: false` on the ZED wrapper, no loop closure, `cone_mapper` is
mapping-only with no pose correction feeding back, and `base_tf` publishes an
identity `map -> odom` placeholder transform. The Frenet frame's `s0` (arc-length
position) is path-relative, so slow VO drift is partly self-correcting there, but
`e_y`/`e_psi` inherit VO noise directly into a rate-weighted cost term.

**Handling**: deferred. Nothing in this port changes localisation. Recorded so a
future odd tracking-error pattern is not misattributed to the controller.

### A7 — Fallback state is not atomic

Each A1-A3 fallback source can arrive from a different node at a different rate;
mixing a pose from time *t* with a yaw-rate estimate from *t - 40ms* injects a
phantom slip angle that isn't physically present. The sim tree's `sim_perception.py`
exists specifically to avoid this, bundling all six state quantities into one 20 Hz
snapshot published together.

**Handling**: this resolves itself the moment `/fsae/slam/car_odom` gets a real
publisher, since `nav_msgs/Odometry` carries pose and twist in one message from one
instant. Until then, the fallback ladder in `_resolve_state()` is a known,
documented approximation, not a hidden one.

---

## B — Actuation and command interface

| ID | Gap | Handling |
|---|---|---|
| B1 | No acceleration command channel | placeholder + compromise |
| B2 | Speed command is 1 m/s integer-quantised | deferred |
| B3 | NMPC emits no speed target itself | compromise |
| B4 | Steering limit mismatch (25° vs 30°) | compromise |
| B5 | Steering command resolution is 0.25° | deferred |
| B6 | An out-of-range command silently latches the last one | worked around, publish-side |
| B7 | `jerk`/`steering_angle_velocity` must be in [0,1] | handled, zeroed explicitly |
| B8 | CAN bridge to hardware is currently disconnected | prerequisite, not done here |
| B9 | `fs_msgs` (FSDS-only) is not a dependency of this repo | removed from the port |
| B10 | No command mux / e-stop gate on `cmd_vel` | deferred, recommended follow-up |

### B1 — No acceleration command channel

The NMPC's second control output is a signed acceleration in m/s² (range roughly
−7 … +12 in the sim tuning). The CAN frame (`0x300`) has a byte nominally meant for
`acceleration`, but `ack_to_can.py`'s parser (`ackermann_to_can_parser`) requires
`0 <= acceleration <= 255` and returns `None` — dropping the whole message — for
anything outside that range. **Braking (negative acceleration) is therefore rejected
outright**, and it is unconfirmed whether MoTeC even consumes that byte today.

**Handling**: a new placeholder topic, `/fsae/control/accel_cmd`
(`ackermann_msgs/AckermannDriveStamped`, `.drive.acceleration` carries the signed
value), is published alongside `cmd_vel` so the raw command is not silently thrown
away. Nothing consumes it yet. It exists so a future MoTeC channel, or a revised
`ack_to_can`, has something to read directly instead of the lossy speed-integration
compromise below.

**Closing it properly**: confirm with whoever owns the MoTeC configuration which CAN
byte(s), if any, the ECU actually reads for acceleration/torque, and update
`ack_to_can.py` to accept a signed range and forward it. That is a CAN-bridge change,
explicitly out of scope for this port (`ack_to_can.py` is untouched).

### B2 — Speed command is 1 m/s integer-quantised

`ack_to_can.py:191` does `int(speed)` into a single byte with no scaling — 1 m/s
resolution, anything below 1.0 m/s transmits as 0, negative values are rejected before
reaching that line. The NMPC's longitudinal loop resolves far finer than this.

**Handling**: deferred, documented. Not addressed by this port; `ack_to_can.py` is
untouched. Bring-up rung 3 (low speed, straight line) is specifically where this
quantisation's effect on tracking is characterised.

### B3 — NMPC emits no speed target itself

The NMPC returns a raw or normalised acceleration command, not a speed. On the sim
side, `fsds_bridge.py` closes that loop (integrating acceleration into a simulator
speed command); **that module does not exist in this repo** and was not ported (it is
FSDS-specific).

**Handling (compromise, the one genuinely new piece of control logic in this port)**:
`_publish_command()` integrates the commanded acceleration forward over a short fixed
horizon to get a speed the CAN frame can actually carry:

```
v_cmd = clip(v_meas + a_cmd * ACCEL_TO_SPEED_HORIZON_S, 0.0, v_max)
```

`ACCEL_TO_SPEED_HORIZON_S` starts at `0.25 s` as a declared ROS2 parameter (not a
literal), and is expected to need tuning on the rig — it is not derived from anything
already validated, unlike the rest of the ported weights.

### B4 — Steering limit mismatch (25° vs 30°)

Three different numbers currently describe the car's steering limit, none verified
against the physical rack: the NMPC's `control_limits.MAX_STEER_RAD` is
`radians(25.0)` (used for output normalisation inside the solver), the repo's
`max_steer_angle` parameter is `30.0` degrees, and `ack_to_can.py` hard-rejects
anything outside `±30`.

**Handling (compromise)**: `_publish_command()` clamps to
`min(25.0, max_steer_angle)` before publishing — the tighter of the two — so the
solver's own internal limit and the published command are never inconsistent with
each other, and the published value can never exceed what `ack_to_can` accepts (see
B6 for why that second property specifically matters).

**Closing it properly**: measure the physical rack's actual maximum steering angle and
make all three numbers agree.

### B5 — Steering command resolution is 0.25°

`ack_to_can.py` encodes `steering_angle * 4` into a single sign-magnitude byte
(one bit sign, 7 bits magnitude), i.e. 0.25° steps. The sim-side anti-chatter tuning
(`nmpc_steer_rate_anti_hunt_enabled`, the corner-blend rate weights) was validated
assuming continuous steering output.

**Handling**: deferred, documented. Watch for chatter attributable to this
quantisation specifically (a period matching the byte's LSB) versus chatter from an
actual tuning issue, during bring-up.

### B6 — An out-of-range command silently latches the previous one

`AckToCan_publish_callback` only publishes when `ackermann_to_can_parser()` returns
non-`None`; on any rejected field it returns `None` and the callback publishes
**nothing at all**, leaving the CAN bus holding whatever frame was sent last tick.
This is a real hazard paired with a solver that has a documented divergent failure
mode (a "wrong-way full-lock ramp" from one failed subproblem, per the sim tree's
`docs/reference/control_mechanisms.md`): a single NaN or out-of-range tick from the
NMPC would not stop the car, it would freeze the *previous* steering command.

**Handling**: worked around entirely on the publishing side, without touching
`ack_to_can.py`:
- every field is clamped to `ack_to_can`'s accepted range **before** publish (B4
  above is one instance of this generally),
- a finite/NaN guard runs on every field; on failure the node publishes an explicit
  safe command (speed 0, steer 0) rather than skipping the publish,
- `compute()` itself is wrapped in try/except onto that same safe command,
- a watchdog latches the safe command if no successful solve has published within a
  small number of ticks.

**Closing it properly**: `ack_to_can.py` publishing a zeroed/safe frame on parse
failure instead of silently dropping would remove the need for this workaround
entirely, and would protect every other `cmd_vel` publisher (teleop, inspection,
mock) too. Recorded as a recommendation, not made — it is a CAN-bridge change and
touches a shared safety path used by every command source, not something to change
as a side effect of adding one new controller.

### B7 — `jerk`/`steering_angle_velocity` must be in [0, 1]

Same parser: both fields are range-checked to `[0, 1]` and the whole message is
dropped otherwise.

**Handling**: `_publish_command()` sets both explicitly to `0.0`, exactly as
`stanley_controller.py` already does.

### B8 — CAN bridge to hardware is currently disconnected

`candapter_node` is commented out in `common/fsae_bringup/launch/can.launch.py`, so
`/fsae/hardware/can_tx` has no subscriber and `/fsae/hardware/can_rx` has no
publisher — the command path is severed at the hardware boundary today, independent
of anything in this port.

**Handling**: recorded as a prerequisite for on-car testing. Not re-enabled as part
of this change (that is a decision about live hardware access, not a controller
change) — see the plan's bring-up ladder, rung 1 explicitly runs with it disabled.

### B9 — `fs_msgs` (FSDS-only) is not a dependency of this repo

The sim-side node defaults to `standalone_output=True`, publishing
`fs_msgs/ControlCommand` to `/fsds/control_command` and subscribing
`fs_msgs/GoSignal`. `fs_msgs` is an FSDS-simulator-only message package and is not a
dependency anywhere in `fsae_autonomous`.

**Handling**: removed from the port outright, not merely defaulted off — a
default-off parameter still imports the message type at module load and would fail
immediately. `nmpc_controller.py` publishes only `/fsae/control/cmd_vel` (and the new
`/fsae/control/accel_cmd` placeholder from B1).

### B10 — No command mux / e-stop gate on `cmd_vel`

Four nodes already publish `/fsae/control/cmd_vel` today (Stanley, `joystick_teleop`,
`inspection_mission_node`, `mock_stimulus`) with no arbitration; safety currently
rests entirely on launching only one of them at a time. Adding a fifth publisher
behind a nonlinear solver increases the cost of that assumption being violated.

**Handling**: deferred. The node's own safe-command fallback (see B6) protects
against *this* controller's own failures, but does nothing about two controllers
being launched simultaneously. A real mux/e-stop gate is recommended as a follow-up
applying to the whole command layer, not built here.

---

## C — Planning and reference

| ID | Gap | Handling |
|---|---|---|
| C1 | No speed profile from planning | compromise (curvature-based fallback) |
| C2 | No track data in the repo | deferred |
| C3 | Path carries positions only | none needed |
| C4 | Path publish rate is variable and gated | documented |
| C5 | SLAM map resets fully every 60 frames | documented |
| C6 | Path has no meaningful timestamp | compromise |
| C7 | Path direction/order is not guaranteed | new lightweight check |

### C1 — No speed profile from planning

Planning publishes geometry only (`geometry_msgs/PoseArray`, positions with no
heading, curvature, or speed). Target speed today is the single static
`target_velocity` parameter (`8.0` m/s). The sim side's `map_path` /
`speed_profile.csv` / `precomputed_speed_at()` machinery has nothing to load from in
this repo.

**Handling (compromise)**: `curvature_speed()` + `dynamic_speed_cap()`, ported
verbatim in `control_utils.py`, derive a target speed from the live path's own shape
every tick — this is exactly the sim tree's "live-planner mode" and needs no track
files at all.

### C2 — No track data in the repo

There is no `tracks/` directory, no `cone_map.json`, no `centerline.csv`, no CSV of
any kind in `fsae_autonomous`. The sim-tree finding that switching the tracked line
from a raceline to a plain centreline cut steering reversals from 13 to 1 cannot be
reproduced here, because there is no raceline/centreline artifact to compare.

**Handling**: deferred. `load_speed_profile_csv` / `load_path_profile_csv` /
`load_path_heading_profile_csv` are ported (in `control_utils.py`, for file-parity
with the sim side) but are inert — nothing calls them yet, and `path_map_path` /
`map_path` parameters have no file to point at.

### C3 — Path carries positions only

No heading, curvature, or speed per point. **No action needed**: `PathReference`
(inside `nmpc_core.py`) derives arc length, heading, and curvature itself via a
`CubicSpline` fit over the raw `(x, y)` points. This was true on the sim side too
before any track CSVs existed.

### C4 — Path publish rate is variable and gated

The planner has no timer of its own; it runs directly from the pose-callback (see
`centerline_planner.py`'s `set_car_position` → `self.loop()`), so path updates arrive
at camera frame rate, not a fixed rate. Compounding this, `cone_detection.cpp`
(line ~567) only publishes cone detections when **both** boundary colours are visible
in frame, so the path stops updating entirely whenever one boundary temporarily
leaves the camera's field of view.

**Handling**: the NMPC node's own 20 Hz timer decouples solving from path arrival —
it always solves against the most recent path it has. `PATH_TIMEOUT`-based stale-path
braking (ported unchanged) will likely fire more often here than it does on the sim
track. Documented so a spike in that specific brake event is not mistaken for a
controller problem.

### C5 — SLAM map resets fully every 60 frames

`cone_mapper.py`'s `reset_map()` fires every `reset_count` (default 60) frames,
discarding the whole accumulated cone map and starting over. The published path
therefore changes discontinuously every few seconds of driving — something the sim
tree's static or continuously-built paths never exercise.

**Handling**: documented, not fixed (this is a SLAM design decision, out of scope for
a controller port). Effects to watch for in telemetry at bring-up rung 4: the path's
`PathReference.signature` changing (forcing a spline rebuild), `s0` jumping, and the
solver's warm start becoming briefly stale right after a reset.

### C6 — Path has no meaningful timestamp

Same shape as A4: the `PoseArray` isn't independently timestamped in a way the
controller can rely on for `path_age_s`. **Handling (compromise)**: arrival time,
same as A4.

### C7 — Path direction/order is not guaranteed

Nothing guarantees the published path starts near the car's current position and
runs in the direction of travel — this is a particular risk from the FaSTTUBe-based
planners. `PathReference.project()` finds the nearest waypoint by `argmin` and then
does a perpendicular projection; a reversed or wrapped-around path produces a
wrong-signed `e_y`, which the controller would act on as if it were correct.

**Handling**: a small, new, path-direction sanity check in `nmpc_controller.py`
(compares the path's initial tangent against the car's current heading; on a large
mismatch it brakes rather than steers). This is genuinely new code, not a port,
because nothing in the sim tree needed it (its planners are trusted to emit a
forward-ordered path).

---

## D — Vehicle model and physical parameters

Every constant below is copied unchanged from the sim-side plant model
(`nmpc_core.py`'s `_Plant` dataclass) and describes the **FSDS simulated car**, not
the physical vehicle. None of this is placeholder-able the way a topic is; it is a
straightforward "measure it before trusting the output" list.

| ID | Gap |
|---|---|
| D1 | `lf=0.70, lr=0.85, m=255.0, Iz=150.0, Cf=29155.5, Cr=19512.3, tau_delta=0.08, tau_a=0.02` are all FSDS values. The real vehicle is a kart/trolley chassis (see `gocartv1.urdf.xml` / `trolly.urdf.xml`) with a documented 1.0 m camera-to-front-axle offset, inconsistent with the 1.55 m wheelbase implied above. None of these have been measured on the real car. |
| D2 | `nmpc_alat_ceiling_enabled` defaults `True`. This models an FSDS-simulator artifact (a sustained ~7.5 m/s² lateral-acceleration clamp the simulator itself imposes), not real vehicle physics. **Must be set `false`** for any real-vehicle use — leaving it on would impose a fictitious yaw-restoring moment on the real car. |
| D3 | `MAX_ACCEL = 12.0`, `MAX_BRAKE = 7.0` (in `control_limits.py`) are FSDS capabilities. The real car's are unmeasured and near-certainly lower. |
| D4 | `tau_delta = 0.08 s` is the FSDS simulated steering actuator lag. The NMPC integrates its own internal `delta_act` state from this constant and never reads back an actual measured steering angle, even though `can_decoder_jnano.py` does decode one onto `/fsae/hardware/drive_status`. |
| D5 | All roughly 56 tuned MPC/NMPC weights (`Q`/`R`/`R_rate`, adaptive-gain shape constants) were tuned against the FSDS plant on one specific recorded track. Per this project's own standing finding, the offline simulator does not yet fully predict even FSDS's own live behaviour (documented steering-saturation gap: 4.8% offline vs 21.1% live), so these weights should be treated as an untested starting point on the real car, not a validated set. |

---

## E — Compute and dependencies

| ID | Gap |
|---|---|
| E1 | `osqp` was declared nowhere in this repo before this port (now added to `requirements.txt` and noted in `fsae_control/package.xml` as pip-only, matching the sim tree's convention for the same dependency). `scipy` was similarly undeclared as a rosdep for `fsae_control` specifically — added as `python3-scipy`, needed for `scipy.sparse` and `scipy.interpolate.CubicSpline` inside `nmpc_core.py`. |
| E2 | Solve-time budget is unvalidated on the target hardware. The sim tree measured 9.1 ms mean / 12.4 ms p95 per solve at the shipped horizon length (N=20) on a desktop; the SQP, its Jacobians, and the QP condensing are pure-Python numpy with no compiled/generated solver. Whether `nmpc_solve_budget_ms = 25.0` (half the 50 ms control period) holds on the actual Jetson is unknown until measured there. |
| E3 | Nothing upstream of the controller runs at a fixed rate (perception is camera-rate, SLAM is detection-rate, planning is pose-rate — see C4), so in practice the controller will routinely solve against a pose and a path that are each some ticks old, more often than the sim tree's more uniform pipeline does. |

---

## F — Instrumentation and validation

| ID | Gap |
|---|---|
| F1 | No telemetry infrastructure exists in this repo (no `telemetry_logger.py`, no `scoring.py`, no `fsae_logs/` equivalent). Without per-tick logging there is no way to diagnose a live NMPC failure after the fact, or to compare a live run against an offline rollout the way the sim tree does. Also: this repo has no stated log-retention policy for whatever logging is eventually added here, mirroring the same open gap already noted for the outer FSDS repo's `fsae_logs/`. |
| F2 | No offline self-consistency check exists here yet. The sim tree's `nmpc_offline_check.py` treats its `_step_scalar == _step` numerical-parity assertion (agreement to 1e-12 between the scalar fast-path integrator and the vectorised one) as "not optional," because a silent divergence between the two is a silent wrong-prediction bug that nothing else would catch. |
| F3 | Even once telemetry exists, scoring would stay permanently partial: the composite score's lap-progress term needs a speed profile to compute an optimal-time integral against (see C1/C2), which this repo has no source for. Any score computed here should be read as partial, not comparable to a sim-side score, until C2 is resolved. |

---

## Summary: what would fully close every gap here

In rough priority order, since several gate the others:

1. Confirm what the physical vehicle's steering limit, wheelbase, mass, and yaw
   inertia actually are (D1, D3, B4) — cheapest to get and gates trusting anything
   else.
2. Get a real publisher onto `/fsae/hardware/curr_vel` or `/fsae/slam/car_odom`
   (A1-A3, A7) — the single biggest fidelity improvement available, and turns three
   compromises off in one step.
3. Re-enable `candapter_node` (B8) so anything below can be tested against real
   hardware at all.
4. Decide, with whoever owns the MoTeC configuration, whether an acceleration/torque
   channel exists or can be added (B1, B2) — removes the least-validated new code in
   this port (the `ACCEL_TO_SPEED_HORIZON_S` integration).
5. `ack_to_can.py` failing safe instead of latching on a rejected frame (B6) — small,
   protects every command source in the repo, not just this one.
6. Record a track (any track) once this repo has a working perception+SLAM+planning
   run, to close C2 and unblock F3.

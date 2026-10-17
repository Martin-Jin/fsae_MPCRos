# NMPC integration gaps

**This controller is not car-ready.** It builds and passes its unit tests and the
hardware-free bench rig on a PC. It has never driven the car. The go-kart steering-only
ground test is the first hardware run and is still pending. This section is the short
list of why the car cannot be driven with it today; the rest of the document is the full
inventory of every mismatch between what the controller needs and what this repo
provides.

> **Go-kart ground test (branch `feat/mpc_ground_test`):** a steering-only test path exists,
> see [`NMPC_GOKART_GROUND_TEST.md`](NMPC_GOKART_GROUND_TEST.md). It sidesteps the CAN
> blockers below by using the kart's serial path, takes `v_x` and yaw rate from the ZED's
> odometry and IMU (A1, A3), sets `v_y` to 0 (A2), and leaves throttle and brake with the
> driver (B1-B3). Everything below still applies to the car.

## Critical blockers (read this before anything else)

1. **Never run on hardware.** No bag replay, no on-car or on-kart run has happened. The
   evidence so far is unit tests, a scripted node test and the open-loop bench rig.
2. **The CAN command path is physically disconnected.** `candapter_node` (the node that
   opens the CANdapter USB-serial device onto the car's CAN bus) is commented out in
   `common/fsae_bringup/launch/can.launch.py` as a standing safety default, see the
   comment there. Nothing published by any controller (Stanley or this NMPC) reaches the
   vehicle until someone re-enables it **at the car, with the adapter physically
   connected**. This is a manual, presence-gated step, not a repo change (gap B8).
3. **There is no active braking anywhere in this repo.** A negative `a_cmd` from the
   NMPC is never sent as a brake command. It becomes a *lower requested speed*
   (`v_cmd = clip(car_speed + a_cmd * horizon, 0, v_max)`, gap B3), because the CAN frame
   has no working negative-acceleration field (`ack_to_can.py` rejects it, gaps B1/B2).
   "Braking" today means asking for less speed and relying on the car to coast down. The
   cone-proximity emergency stop sets `v_cmd = 0.0` for the same reason, and that is the
   full extent of braking through this controller.
4. **The car has no speed, yaw-rate or lateral-velocity sensor wired in.** The model
   needs all three every tick. On the car (default topics) `v_x` falls back through an
   unfilled topic to 1 m/s-resolution CAN data to the controller's own last commanded
   speed (open loop), `v_y` is `0.0`, and yaw rate is a one-tick-delayed finite
   difference of the pose (gaps A1-A3). Wrong slip angles fed into a nonlinear vehicle
   model are a worse failure mode than Stanley being wrong, since Stanley has no model.
5. **A rejected CAN frame silently latches the previous command instead of stopping the
   car.** `ack_to_can.py` drops the whole message on any out-of-range field and the bus
   keeps the last frame. The NMPC node works around this on the publishing side
   (clamping, finite-value guards, an explicit safe-stop command), but the CAN-bridge
   behaviour itself is unchanged and remains the most dangerous failure mode in the
   chain (gap B6).
6. **Every physical parameter and every weight comes from a simulated vehicle.**
   Wheelbase, mass, yaw inertia, tyre stiffness, max accel/brake and all Q/R weights were
   set and tuned in simulation (gap group D). UNVERIFIED on the car or kart. The kart
   launch overrides the geometry it has measured; the car has no overrides at all.
7. **The yaw convention is unverified on the car.** `stanley_controller.py` carries an
   unresolved warning that its `-4.71` yaw correction is "almost certainly WRONG" since
   the camera initialisation changed. A wrong yaw sign is more consequential in a
   model-based controller than in Stanley's simple loop (gap A5).

None of the above is fixed. Each is documented, and several are worked around
defensively (clamping, safe-stop fallbacks, a fallback ladder for the state) so nothing
fails silently. "Handled defensively" is not "safe to drive". The order to close these is
in the final section; the [bring-up ladder](#bring-up-ladder-for-the-car) does not skip
any rung before real driving.

---

The NMPC controller (`control/fsae_control/fsae_control/mpc/nmpc_core.py`, ROS node
`nmpc_controller.py`) needs six things about the car every tick that this repo did not
previously produce, plus one thing it cannot cleanly send. Code carries a one-line
`# GAP <id>:` comment at each affected line; this document is the full explanation.

**Handling key**: *placeholder* = a topic on this repo's naming convention exists and is
subscribed/published, but nothing (or only a partial source) produces/consumes it yet.
*compromise* = a degraded value is computed from what already exists, with no change to
any other node. *deferred* = documented, not addressed, needs separate work (usually
outside `fsae_control`).

## Why this exists at all

The NMPC's per-tick entry point needs:

```
compute(path, car_pos, car_yaw, car_speed, desired_speed,
        car_yaw_rate=0.0, pose_age_s=0.0, car_vy=0.0)
```

The state vector it builds from these is
`[s, e_y, e_psi, v_x, v_y, r, delta_act, a_act]` (arc-length position, lateral error,
heading error, longitudinal speed, lateral speed, yaw rate, and two internally
integrated actuator lag states). Everything except `path`, `car_pos` and `car_yaw`
needed a new source. The model and solver are described in `nmpc_core.py`'s module
docstring.

For contrast, Stanley (`stanley_controller.py`) uses only `(x, y, yaw)` from
`/fsae/slam/car_position` and a fixed speed parameter.

---

## A: State estimation

| ID | Gap | Handling |
|---|---|---|
| A1 | No longitudinal velocity sensor | placeholder + compromise |
| A2 | No lateral velocity | placeholder + compromise |
| A3 | No yaw rate on the car's default topics | placeholder + compromise |
| A4 | Pose has no timestamp | compromise |
| A5 | Yaw convention unverified post-camera-frame-fix | compromise, resolve at bring-up |
| A6 | Pose quality on the car is unmeasured | deferred |
| A7 | Fallback state is not atomic across sources | resolved once A1-A3's placeholder is filled |

### A1: No longitudinal velocity (`v_x`)

Nothing on the car measures its own speed. `/fsae/hardware/curr_vel`
(`ackermann_msgs/AckermannDriveStamped`) exists in the repo's topic naming and has two
subscribers (`inspection_mission.py`, `sys_status.py`), but **zero publishers**.
`can_decoder_jnano.py` publishes `/fsae/hardware/drive_status`, whose speed field is a
single unshifted CAN byte (1 m/s resolution, no timestamp on the value, and the decoder's
own comment marks it "not sure if this is needed").

`v_x` is `x0[3]`. It sets both tyre slip angles, the kinematic/dynamic model blend
(pure kinematic below `v_blend_lo`, pure dynamic above `v_blend_hi`) and the `e_v`
(speed-tracking) cost term.

**Handling**, in order of preference (`nmpc_controller.py`'s `_resolve_state()`):
1. `odom_topic` (`nav_msgs/Odometry`, default `/fsae/slam/car_odom`, no publisher on the
   car). `odom_velocity_source: twist` reads the twist; `pose_diff` differentiates the
   stamped pose. The kart launch uses `/zed/zed_node/odom` with `pose_diff`.
2. `/fsae/hardware/curr_vel` (placeholder).
3. `/fsae/hardware/drive_status` (coarse but real).
4. The controller's own last commanded speed (open loop, the same assumption Stanley
   makes).

**Closing it properly**: a real speed source, either wheel speed decoded onto a CAN
frame `can_decoder` already reads and republished on `/fsae/hardware/curr_vel`, or ZED
odometry on the car as on the kart (UNVERIFIED as a speed source on either vehicle).
No controller change is needed.

### A2: No lateral velocity (`v_y`)

No wheel-speed sensors and no lateral-velocity estimator exist. A previous attempt
(`perception/fsae_camera/velocity/velocity.cpp`, IMU-accel integration) is **not in the
CMake build glob** and its own comment reads
`### THIS DOES NOT OUTPUT ACCURATE VELOCITY DATA ###`.

`v_y` is `x0[4]`. It must not be folded into a single `hypot()` speed, because that drops
the `vy*cos(e_psi)` term the error-state derivative needs.

**Handling**: the odometry twist is the only source, and only with
`use_measured_vy: true`. Otherwise `v_y` is `0.0`. This is not neutral, but the model is
pure kinematic (which assumes `v_y ~ 0`) below `v_blend_lo`, so the error is smallest at
bring-up speeds and grows with speed. This is why the bring-up ladder caps speed until a
real `v_y` source exists.

**Closing it properly**: an odometry message with a trusted lateral-velocity estimate,
from an IMU-based estimator or a validated ZED twist.

### A3: No yaw rate (`r`) on the car's default topics

`r` is `x0[5]` and drives `e_psi_dot = r - kappa*s_dot`, the path-curvature coupling
that lets the NMPC turn in before error builds.

**Handling**, in order of preference:
1. `imu_topic` (`sensor_msgs/Imu`, default off). `angular_velocity.z` times
   `imu_yaw_rate_sign`. The kart launch uses `/zed/zed_node/imu/data`.
2. The odometry-derived rate from `odom_topic`.
3. A finite difference of the pose's yaw across the 20 Hz tick with a light low-pass
   filter. Noisy and one tick delayed: enough to run at low speed, not a permanent
   source. Telemetry tags it so a run on this estimate can be told apart.

**Closing it properly**: on the car, set `imu_topic` and `odom_topic` to the ZED wrapper
topics as the kart launch does, after checking their signs (see the kart checklist's
sensor checks). UNVERIFIED on the car.

### A4: Pose has no timestamp

`/fsae/slam/car_position` is `geometry_msgs/Pose`, not `PoseStamped`. Without a stamp,
`pose_age_s` (how stale the pose is when the controller acts on it) is unavailable, and
the delay-compensation rollforward cannot use a real age.

**Handling (compromise)**: the node stamps the pose with its own **arrival time**. This
under-counts staleness by the perception and SLAM latency.

**Closing it properly**: change `/fsae/slam/car_position` to `PoseStamped` carrying the
camera's capture-time stamp (as `/fsae/perception/cone_detection` already does). Out of
scope here, since Stanley and every planner consume the unstamped message.

### A5: Yaw convention unverified

Yaw is packed into `orientation.w` of the `Pose` message (a repo-wide convention).
`stanley_controller.py`'s in-file warning says its `-4.71` (~270°) yaw offset was tuned
for the ZED's old coordinate frame, that the ZED init has since changed to
`RIGHT_HANDED_Z_UP_X_FWD`, and that the constant is now "almost certainly WRONG".

A wrong yaw convention matters more here than for Stanley: Stanley's cross-track term
still corrects a wrong heading over a few ticks, while a 90° yaw error fed into the
NMPC's model corrupts every slip-angle and tyre-force calculation immediately.

**Handling**: the NMPC reads the same `orientation.w` convention as Stanley and the
planners, with no offset. **Resolve on the rig, not in code**: bring-up rung 2 (wheels
off the ground, steering only) checks the yaw sign and any offset against the physical
steering direction before any driving. On the kart this is step 5 of the
[bring-up checklist](NMPC_GOKART_BRINGUP_CHECKLIST.md).

### A6: Pose quality on the car is unmeasured

`cone_landmark_mapper` corrects ZED visual-odometry drift against a cone-landmark pose
graph and publishes the corrected pose on `/fsae/slam/car_position`. The pose can step
when the graph re-optimises. `e_y`/`e_psi` inherit any pose noise or step directly into a
rate-weighted cost term.

**Handling**: deferred; the controller does not change localisation. Pose noise and step
size on the car are UNVERIFIED. Recorded so an odd tracking-error pattern is not
misattributed to the controller.

### A7: Fallback state is not atomic

Each A1-A3 fallback source can arrive from a different node at a different rate. Mixing a
pose from time *t* with a yaw-rate estimate from *t - 40 ms* injects a phantom slip angle.

**Handling**: resolved for the pose and twist when one `nav_msgs/Odometry` source feeds
`odom_topic`, since it carries both from one instant. The IMU and the SLAM pose still
arrive separately. Until then the fallback ladder in `_resolve_state()` is a documented
approximation.

---

## B: Actuation and command interface

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
| B10 | No command mux / e-stop gate on `cmd_vel` | deferred, recommended follow-up |

### B1: No acceleration command channel

The NMPC's second output is a signed acceleration in m/s², bounded by `MAX_ACCEL` and
`MAX_BRAKE` in `control_limits.py` (see D3). The CAN frame (`0x300`) has a byte nominally
for `acceleration`, but `ack_to_can.py`'s parser (`ackermann_to_can_parser`) requires
`0 <= acceleration <= 255` and returns `None` (dropping the whole message) otherwise.
**Braking (negative acceleration) is therefore rejected**, and it is unconfirmed whether
MoTeC consumes that byte at all.

**Handling**: a placeholder topic, `/fsae/control/accel_cmd`
(`ackermann_msgs/AckermannDriveStamped`, signed value in `.drive.acceleration`), is
published alongside the command so the value is not discarded. Nothing consumes it yet.

**Closing it properly**: confirm with whoever owns the MoTeC configuration which CAN
byte(s), if any, the ECU reads for acceleration/torque, and update `ack_to_can.py` to
accept a signed range and forward it.

### B2: Speed command is 1 m/s integer-quantised

`ack_to_can.py` does `int(speed)` into a single byte with no scaling: 1 m/s resolution,
anything below 1.0 m/s transmits as 0, negative values are rejected. The NMPC's
longitudinal loop resolves far finer than this.

**Handling**: deferred; `ack_to_can.py` is untouched. Bring-up rung 3 (low speed,
straight line) is where this quantisation's effect on tracking gets characterised.

### B3: NMPC emits no speed target itself

The NMPC returns an acceleration, not a speed, and the CAN frame carries a speed.

**Handling (compromise)**: `_publish_command()` integrates the commanded acceleration
over a short fixed horizon:

```
v_cmd = clip(v_meas + a_cmd * accel_to_speed_horizon_s, 0.0, v_max)
```

`accel_to_speed_horizon_s` defaults to `0.25 s` (a ROS parameter). It is not derived
from any measurement and needs tuning on the car. UNVERIFIED.

### B4: Steering limit mismatch (25° vs 30°)

Three numbers describe the car's steering limit, none verified against the physical
rack: `control_limits.MAX_STEER_RAD` is `radians(25.0)` (output normalisation inside the
solver, a simulation value, UNVERIFIED), the repo's `max_steer_angle` parameter is
`30.0` degrees, and `ack_to_can.py` hard-rejects anything outside `±30`.

**Handling (compromise)**: `_publish_command()` clamps to `min(25.0, max_steer_angle)`,
so the solver's limit and the published command agree, and the command can never exceed
what `ack_to_can` accepts (see B6). `plant_max_steer_deg` overrides the solver's limit
(the kart checklist measures it).

**Closing it properly**: measure the rack's maximum steering angle and make all three
numbers agree.

### B5: Steering command resolution is 0.25°

`ack_to_can.py` encodes `steering_angle * 4` into one sign-magnitude byte (1 sign bit,
7 magnitude bits), i.e. 0.25° steps. The anti-chatter settings
(`nmpc_steer_rate_anti_hunt_enabled`, the corner-blend rate weights) were tuned in
simulation against continuous steering output. UNVERIFIED with a quantised actuator.

**Handling**: deferred. During bring-up, tell chatter at the byte's LSB apart from
chatter caused by tuning.

### B6: An out-of-range command silently latches the previous one

`AckToCan_publish_callback` only publishes when `ackermann_to_can_parser()` returns
non-`None`; on any rejected field it publishes **nothing**, leaving the bus holding the
last frame. Paired with an iterative solver that can fail on a single tick, one NaN or
out-of-range tick would freeze the *previous* steering command rather than stop the car.

**Handling**: worked around on the publishing side, without touching `ack_to_can.py`:
- every field is clamped to `ack_to_can`'s accepted range **before** publish (B4 is one
  instance),
- a finite/NaN guard runs on every field; on failure the node publishes an explicit safe
  command (speed 0, steer 0) rather than skipping the publish,
- `compute()` is wrapped in try/except onto the same safe command,
- a watchdog latches the safe command if no successful solve has published within a
  small number of ticks.

**Closing it properly**: `ack_to_can.py` publishing a zeroed/safe frame on parse failure
instead of dropping it. That protects every other `cmd_vel` publisher (teleop,
inspection, mock) too. Recorded as a recommendation; it touches a shared safety path used
by every command source.

### B7: `jerk`/`steering_angle_velocity` must be in [0, 1]

Same parser: both fields are range-checked to `[0, 1]` and the message is dropped
otherwise.

**Handling**: `_publish_command()` sets both to `0.0`, as `stanley_controller.py` does.

### B8: CAN bridge to hardware is currently disconnected

`candapter_node` is commented out in `common/fsae_bringup/launch/can.launch.py`, so
`/fsae/hardware/can_tx` has no subscriber and `/fsae/hardware/can_rx` has no publisher.

**Handling**: a prerequisite for on-car testing, not re-enabled here (a decision about
live hardware access). Bring-up rung 1 runs with it disabled.

### B10: No command mux / e-stop gate on `cmd_vel`

Four nodes already publish `/fsae/control/cmd_vel` (Stanley, `joystick_teleop`,
`inspection_mission_node`, `mock_stimulus`) with no arbitration; safety rests on
launching only one at a time. A fifth publisher behind a nonlinear solver raises the
cost of that assumption failing.

**Handling**: deferred. The node's safe-command fallback (B6) covers this controller's
own failures, not two controllers running at once. A mux/e-stop gate for the whole
command layer is the recommended follow-up.

---

## C: Planning and reference

| ID | Gap | Handling |
|---|---|---|
| C1 | No speed profile from planning | compromise (curvature-based fallback) |
| C2 | No recorded track | not supported |
| C3 | Path carries positions only | none needed |
| C4 | Path publish rate is variable and gated | documented |
| C5 | Path can change discontinuously | documented |
| C6 | Path has no meaningful timestamp | compromise |
| C7 | Path direction/order is not guaranteed | direction check |

### C1: No speed profile from planning

Planning publishes geometry only (`geometry_msgs/PoseArray`, positions with no heading,
curvature or speed).

**Handling (compromise)**: `curvature_speed()` in `control_utils.py` derives a target
speed from the live path's shape every tick, between `v_min` and `v_max`. The
curvature-to-speed mapping is untuned for either vehicle. UNVERIFIED.

### C2: No recorded track

There is no recorded path or speed-profile file in this repo.

**Handling**: not supported. The NMPC node has no parameter for a precomputed path or
speed profile and always follows the live planner path. The CSV loaders in
`control_utils.py` (`load_speed_profile_csv`, `load_path_profile_csv`,
`load_path_heading_profile_csv`) are unused by the NMPC.

### C3: Path carries positions only

**No action needed**: `PathReference` (inside `nmpc_core.py`) derives arc length,
heading and curvature itself from a `CubicSpline` fit over the raw `(x, y)` points.

### C4: Path publish rate is variable and gated

The planner has no timer of its own; it runs from the pose callback (see
`centerline_planner.py`'s `set_car_position` → `self.loop()`), so path updates arrive at
pose rate. `cone_detection.cpp` only publishes detections when **both** boundary colours
are in frame, so the path can stop updating when one boundary leaves the camera's view.

**Handling**: the NMPC's own 20 Hz timer decouples solving from path arrival; it solves
against the most recent path. `PATH_TIMEOUT` (0.5 s) safe-stops on a stale path. How
often that fires on the car is UNVERIFIED; a spike in that event is a planning-input
problem, not a controller one.

### C5: Path can change discontinuously

`cone_landmark_mapper` re-optimises its landmark positions as cones are re-observed, so
the boundaries the planner builds from, and hence the path, can shift between updates.

**Handling**: documented, not changed. Watch telemetry at bring-up rung 4 for the
`PathReference.signature` changing (forcing a spline rebuild), `s0` jumping, and the
solver's warm start going briefly stale after a jump. Size and frequency on the car are
UNVERIFIED.

### C6: Path has no meaningful timestamp

Same shape as A4: the `PoseArray` is not timestamped in a way the controller can rely on
for `path_age_s`. **Handling (compromise)**: arrival time, as in A4.

### C7: Path direction/order is not guaranteed

Nothing guarantees the published path starts near the car and runs in the direction of
travel, a particular risk with the FaSTTUBe-based planners. `PathReference.project()`
finds the nearest waypoint by `argmin`, then projects perpendicularly; a reversed or
wrapped-around path gives a wrong-signed `e_y` that the controller would act on.

**Handling**: a path-direction check in `nmpc_controller.py` compares the path's initial
tangent with the car's heading; on a large mismatch it safe-stops rather than steers.

---

## D: Vehicle model and physical parameters

The defaults in `nmpc_core.py`'s `_Plant` dataclass describe a **simulated vehicle**, not
the car or the kart. This is a "measure it before trusting the output" list. The node's
`plant_*` parameters override `lf`, `lr`, `v_blend_lo`, `v_blend_hi`, `tau_delta` and the
steering limit; `m`, `Iz`, `Cf`, `Cr` have no override parameter.

| ID | Gap |
|---|---|
| D1 | `lf=0.70, lr=0.85, m=255.0, Iz=150.0, Cf=29155.5, Cr=19512.3, tau_delta=0.08, tau_a=0.02` are simulation values, UNVERIFIED on the car or kart. The car has no measured values. The kart launch sets `plant_lr` 0.14 (taped) and `plant_lf` 0.86 (from a CAD-only 1.00 m wheelbase, UNVERIFIED), and runs the kinematic model below 8 m/s so the tyre constants do not apply there. |
| D2 | `nmpc_alat_ceiling_enabled` is an optional model of a sustained lateral-acceleration limit that was measured in simulation. It is not known to exist on any real vehicle (UNVERIFIED). The dataclass default is `True`; `fsae_params.yaml` sets it `false`. **Keep it `false`** for real-vehicle use, or the model adds a yaw-restoring moment that may not exist. |
| D3 | `MAX_ACCEL = 12.0`, `MAX_BRAKE = 7.0` (`control_limits.py`) are simulation values, UNVERIFIED and likely higher than either vehicle can do. |
| D4 | `tau_delta = 0.08 s` (steering actuator lag) is a simulation value, UNVERIFIED. The NMPC integrates its own internal `delta_act` from it and never reads a measured steering angle, although `can_decoder_jnano.py` decodes one onto `/fsae/hardware/drive_status`. |
| D5 | All `Q`/`R`/`R_rate` weights and adaptive-gain constants in `mpc_params.py`/`nmpc_params.py` were tuned in simulation on one track. UNVERIFIED on the car or kart; treat them as a starting point, not a validated set. |

---

## E: Compute and solver settings

| ID | Gap |
|---|---|
| E1 | `osqp` is pip-only (`requirements.txt`, noted in `fsae_control/package.xml`). `scipy` is a rosdep (`python3-scipy`), needed for `scipy.sparse` and `scipy.interpolate.CubicSpline` in `nmpc_core.py`. |
| E2 | Solve time is unmeasured on the Jetson. The SQP, its Jacobians and the QP condensing are pure-Python numpy with no generated solver. On a desktop at N=20 with 4 Jacobian and 4 rollout substeps at every speed (the low-speed setting in E4, without its speed gate), mean solve time was about 19 ms, p95 about 24 ms, max about 39 ms, against `nmpc_solve_budget_ms = 25.0` (half the 50 ms tick). The Jetson is expected to be slower. UNVERIFIED on target; measure `solve_ms` in telemetry on the first run. |
| E3 | Nothing upstream of the controller runs at a fixed rate (perception is camera rate, SLAM is detection rate, planning is pose rate, see C4), so the controller often solves against a pose and a path that are each some ticks old. |
| E4 | Integration substeps are speed-gated to avoid a low-speed numerical instability that freezes the output at zero: `nmpc_rk_substeps` 4 below `nmpc_rk_gate_speed` (4.0 m/s), 3 above; `nmpc_jac_substeps` 4 below `nmpc_jac_gate_speed` (8.0 m/s), 2 above. The envelopes come from the simulation vehicle's dynamics; UNVERIFIED with the kart's or car's own `plant_*` values. `nmpc_params.py`'s field docstrings describe each setting. |
| E5 | `nmpc_solve_budget_ms` is checked inside the backtracking line search as well as before each SQP iteration, so it truncates extra line-search halvings once the budget is spent. It bounds tail latency, not typical cost. |
| E6 | The speed-target ramp holds once `desired_speed - car_speed` exceeds `SPEED_TARGET_DEFICIT_MAX` (2.5 m/s, a module constant in `nmpc_controller.py`), so the target cannot run away while the car is stationary or recovering. The value was tuned in simulation; UNVERIFIED. It has no ROS parameter, so promote it if it needs tuning on the car. |
| E7 | `nmpc_standstill_steer_damp_enabled` (default on) raises stage-0 steering effort cost by `nmpc_standstill_steer_r_scale` below `nmpc_standstill_speed`, fading out by `nmpc_standstill_fade_speed`, so the controller does not pre-load steering before the car moves. Values tuned in simulation; UNVERIFIED. |

---

## F: Instrumentation and validation

| ID | Gap |
|---|---|
| F1 | No per-tick log to disk exists. With `nmpc_publish_telemetry_enabled:=true` the node publishes its per-tick telemetry as JSON on `/fsae/viz/nmpc_telemetry`; record that topic with `ros2 bag record` to diagnose a run after the fact. No log-retention policy exists for bags. |
| F2 | Solver self-consistency (scalar vs vectorised rollout, Jacobians, SQP convergence) is covered by `control/fsae_control/test/test_nmpc_core_math.py`. Keep it passing after any change to `nmpc_core.py`. |

---

## Bring-up ladder for the car

1. **Rung 1, no actuation**: full stack running with `candapter_node` disabled (B8).
   Check every input topic and the command on `/fsae/control/cmd_vel`.
2. **Rung 2, wheels off the ground, steering only**: verify the steering sign and yaw
   convention (A5) and the steering limit (B4).
3. **Rung 3, low speed, straight line**: characterise speed quantisation (B2) and the
   accel-to-speed horizon (B3).
4. **Rung 4, low-speed driving with SLAM and planning**: watch path jumps (C5), stale-path
   stops (C4) and solve time (E2). Raise speed only once a real `v_y` source exists (A2).

The kart follows its own steering-only version of rungs 1-2 in
[`NMPC_GOKART_BRINGUP_CHECKLIST.md`](NMPC_GOKART_BRINGUP_CHECKLIST.md).

## Summary: what would close every gap here

In rough priority order, since several gate the others:

1. Measure the car's steering limit, wheelbase, mass and yaw inertia (D1, D3, B4).
   Cheapest to get, and gates trusting anything else.
2. Get a real speed and yaw-rate source onto `odom_topic`/`imu_topic` or
   `/fsae/hardware/curr_vel` (A1-A3, A7). The biggest fidelity improvement available.
3. Re-enable `candapter_node` (B8) so anything below can be tested on hardware.
4. Decide with whoever owns the MoTeC configuration whether an acceleration/torque
   channel exists or can be added (B1, B2). This removes the least-validated logic in
   the node (the `accel_to_speed_horizon_s` integration).
5. Make `ack_to_can.py` fail safe instead of latching on a rejected frame (B6). Small,
   and protects every command source.
6. Measure solve time on the Jetson (E2) and retune the weights on the vehicle (D5).

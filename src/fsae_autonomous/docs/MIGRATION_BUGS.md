# Bug fixes / known issues

Running log of issues found in the refactored stack. Urgent / blocking items
are fixed in-place; the rest is noted for the next person who touches the repo.

## Outstanding (not yet fixed)

### Detections RViz overlay swaps blue/yellow marker colours (VIZ-ONLY — perception data is correct)
- **Symptom:** in RViz/Foxglove the raw-detection cones look colour-swapped — yellow cones draw as blue cubes and blue cones as yellow cubes ("yellow is blue and blue is yellow").
- **Cause:** `visualise_cone_map.py` `detections_callback` passes `msg.yellow` cones `colour=0` and `msg.blue` cones `colour=2` (`visualise_cone_map.py:48-53`), but `convert_to_visualization` renders `colour==0` as **blue** (r0 g0 b1) and `colour==2` as **yellow** (r1 g1 b0) (`visualise_cone_map.py:146-163`). The colour argument is cross-wired for the `/fsae/viz/detections` overlay only.
- **Scope check:** the SLAM-map path in the same file is **correct** — `left_track` (blue cones per `cone_mapper.py`) → `colour=0` → blue marker; `right_track` (yellow) → `colour=2` → yellow marker. So `/fsae/viz/cones` is fine; only `/fsae/viz/detections` is swapped.
- **Important:** the `ConeDetection` message itself is NOT swapped — see the "verified non-bug" entry below. Planning/control see correct colours. Fix is a two-line swap in `detections_callback` (give yellow `colour=2`, blue `colour=0`); left unfixed here because it's outside the fsae_camera migration scope.

### `ConeDetection` publish gate starves the mapper on one-sided views (PRE-EXISTING, intentionally preserved)
- **Symptom:** `/fsae/perception/cone_detection` goes silent whenever the frame does not contain **both** ≥1 blue AND ≥1 yellow cone — e.g. on straights where only one boundary is visible, during spins, or entering/leaving the track. The mapper and planners receive nothing until both colours are back in frame.
- **Cause:** deliberate gate at the end of the detection pipeline (now `cone_detection.cpp` `image_callback`, step 7; previously the same rule in the SDK loop). Rationale was "never give the planner a one-sided picture", but the side effect is starving SLAM of updates it could still use.
- **Status:** preserved exactly through the zed_ros2_wrapper migration (faithful-port policy). If it gets changed later, remember `cone_mapper.py` reads `car_pose` from inside this message — dropping the gate changes the pose update rate too.

## Verified non-bugs (investigated, do not re-derive)

### YOLO channel order and blue/yellow label mapping are CORRECT in fsae_camera
Investigated 2026-07-02 after the on-track "cones look swapped" report (which turned out to be the viz overlay bug above).
- **Model ground truth** (read from `/home/fsae/autonomous/cone_detection_model.onnx` `metadata_props` — the source the `.engine` was compiled from): Ultralytics YOLOv8 8.2.69, input `1x3x704x704`, output `1x9x10164` (4 box + 5 classes), class names `{0: 'Blue_Cone', 1: 'Large_Orange_Cone', 2: 'Orange_Cone', 3: 'Unknown', 4: 'Yellow_Cone'}`. (The `.engine` itself has no metadata — it was built by `Yolo::build_engine()`, not the Ultralytics exporter.)
- **Label mapping:** `cone_detection.cpp` buckets `label 0 → blue`, `label 4 → yellow`, rest → `big_orange`. Matches the ONNX names exactly. ✔
- **Channel order:** Ultralytics models expect **RGB** input. The pipeline delivers it: BGRA frame → `cvtColor(BGRA2BGR)` → `preprocess_img()` letterbox (no colour change, stays BGR) → the CHW serialization loop in `Yolo::run()` writes planes from `uc_pixel[2],[1],[0]`, i.e. performs the BGR→RGB swap while transposing. Net input to the network is RGB. ✔
- **Misleading comments fixed:** old comments claimed the net was "trained on standard 3-channel BGR images" and that `preprocess_img` does "letterbox BGR to RGB" — both wrong (the RGB swap happens in the serialization loop). Comments corrected in `yolo.cpp`; no behaviour was changed.
- **If cones still look mirrored on-car after the viz fix:** suspect the deprojection axis signs (`p.y = -Xc`) in `cone_detection.cpp` — a wrong sign there mirrors the track left/right, which *also* presents as "blue and yellow are on the wrong sides". See `zed_wrapper_plan.md` §7/§14 MUST-VERIFY.

### Detection markers draw ~0.9 m below the RViz grid (EXPECTED — and it confirms the deprojection z sign)
Investigated 2026-07-03 after "cones appear under the ground" in RViz.
- **Cause:** the `map` frame's origin is the **camera's startup pose** (wrapper defaults: `set_gravity_as_origin: true`, `floor_alignment: false`, `initial_base_pose: [0,…]`), i.e. z=0 is at camera height, not the floor. Detection z comes from the deprojection (`p.z = -Yc`, camera-relative), and `visualise_cone_map.py` copies the full 3D point into the marker. Trolley camera is mounted 0.90 m up → ground cones correctly render at z ≈ −0.9. The RViz grid is just the z=0 plane, not "the ground".
- **Why it's useful:** this is a free partial verification of `zed_wrapper_plan.md` §14 — if the vertical sign were wrong, cones would float ~0.9 m *above* the grid. A roughly constant −0.9 across near/far cones also sanity-checks `fy`/`cy` and depth. (x/y sign check still owed.)
- **Cosmetics if wanted:** RViz Grid → Offset Z = −0.9; or zero the marker z in `detections_callback` (cones are on the ground by definition — would also match the SLAM-map markers, which draw at z≈0).
- **Related quirk (pre-existing):** the detections overlay stamps raw **car-local** coordinates straight into `map` without transforming by the car pose — indistinguishable from correct while the rig sits at its startup position, but once it moves the overlay stays anchored at the origin. Only the SLAM-map markers are truly global.

### `track_point` — pursuit viz "next destination" sphere never shows (PRE-EXISTING, not a refactor regression)
- **Symptom:** `pursuit_viz` (launched, `viz.launch.py:11`) never draws the yellow destination sphere. The rest of pursuit viz (steering arc from `drive_vis`) works.
- **Cause — TWO stacked defects, both pre-existing (dead in the old repo too):**
  1. `stanley_controller.py:106` is `self.create_publisher(Pose, "/fsae/control/track_point", 5)` with **no variable assignment** — the handle is discarded, so stanley can never publish. Also, `get_closest_track_point()` returns an *index*, not a `Pose`; nothing builds/publishes the actual point.
  2. So the topic has no publisher at all → `visualise_pure_pursuit.py:31` (`save_pursue_destination`) never fires → `next_destination_marker` stays `None`.
- **Refactor's only contribution:** a *dormant* namespace split — producer `/fsae/control/track_point` vs consumer `/fsae/planning/track_point`. Inconsequential today (nothing publishes either way), but it would bite if defect 1 is fixed without also aligning the namespace.
- **Verdict (corrected):** this is NOT a refactor regression — applying the "did it work in the old repo?" test, it was dead before and dead after. Pre-existing unfinished feature.
- **Fix (optional enhancement, not owed):** either (A) wire it up — assign the publisher, build a `Pose` from `tx[cls_point]/ty[cls_point]`, publish it, AND change viz:31 to `/fsae/control/track_point`; or (B) delete the dead code on both ends. A namespace-only "fix" does nothing visible.

### Duplicate SLAM implementations
- **Symptom:** two mappers publish `Track` on `/fsae/slam/left_track` + `/fsae/slam/right_track`.
- **Cause:** `cone_mapper.py` (Python, the one launched by `slam.launch.py:14`) and `cone_landmark_mapper.cpp` (C++, **not launched anywhere**). Only the Python one runs.
- **Fix:** not a live bug; the C++ mapper is dead/orphaned code. Decide whether to keep or delete to avoid confusing the next person.

### Orphan publishers (no in-tree subscribers)
- `/fsae/hardware/drive_status` (also has the broken type above), `/fsae/slam/times_modified`, `/fsae/slam/car_velocity` publish with nothing consuming them. `sys_status` and `inspection_mission` read car state from `/fsae/hardware/curr_vel`, not `drive_status`. Left as-is — flagging only.

## Non-urgent

### Perception pipeline runs ~15 Hz, not the configured 60 fps (Jetson saturation — measured 2026-07-03)
- **Symptom:** `/fsae/slam/car_position` and `/fsae/perception/cone_detection` at ~15 Hz; expected higher.
- **Measured** (full stack + RViz on the Jetson): wrapper image ~8–15 Hz, depth ~5 Hz, wrapper pose ~17 Hz — the downstream topics just ride the image rate (`image_callback` publishes once per received frame). Wrapper config is HD720 @ 60 with `pub_frame_rate: 0.0` (no throttle), so the config is not the limiter.
- **Cause — platform saturation, not a bug:** GPU 65–98% (`NEURAL_LIGHT` depth + YOLO TensorRT + RViz share the iGPU), all 6 CPU cores 55–80% with CPU clocks held at 1.3 GHz (25W nvpmodel, no `jetson_clocks`), and the wrapper container burns a full core serializing 720p BGRA + float depth over DDS to `cone_detection_node` — a cost the old in-process SDK design never paid.
- **Is it a problem?** Not for bench/trolley work (planner is event-driven; old system's pose was 10 Hz). For real driving, want 25–30 Hz+.
- **Remedies, in order of impact:** (1) run RViz/Foxglove off-board; (2) `sudo nvpmodel -m 0` + `sudo jetson_clocks`; (3) request HD720 @ 30 (`grab_frame_rate: 30` in `zed2i.yaml`) — a sustainable 30 beats an aspirational 60; (4) `visualise: false` when the annotated image isn't needed; (5) **structural fix:** compose `cone_detection_node` into the wrapper's component container with intra-process comms — eliminates the per-frame DDS serialization entirely.

### Old workspace baked into `install/setup.bash` as an underlay
- **Symptom:** plain `source install/setup.bash` pulls the old workspace into `AMENT_PREFIX_PATH`; `ros2 pkg list` shows old packages (`gocart_*`, `pure_pursuit_visualiser`), stray nodes from the wrong workspace.
- **Cause:** first build happened while `~/.bashrc` sourced `/home/fsae/autonomous/install/local_setup.bash`, so colcon recorded it as an underlay (`install/setup.bash` line 25: `COLCON_CURRENT_PREFIX="/home/fsae/autonomous/install"`).
- **Workaround:** source `install/local_setup.bash` instead — skips the chained underlay.
- **Permanent fix:** rebuild from a shell that doesn't source the old workspace:
  ```bash
  cd ~/ros2_ws
  rm -rf build install log
  env -i HOME=$HOME PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
      bash -c "source /opt/ros/humble/setup.bash && colcon build --symlink-install"
  ```

### Stale entries in `ros2 node list` / `ros2 topic hz` after launches restart
- **Symptom:** dead nodes still listed for ~30 s after Ctrl-C; `ros2 topic hz` reports "does not appear to be published yet" on topics that *are* live. This wrongly looked like the localisation thread + planner were dead while debugging the centerline.
- **Cause:** the ROS 2 daemon caches a stale discovery snapshot, especially after restarting launches.
- **Fix / lesson:** confirm with `ros2 topic echo --once` before concluding a node is broken, and refresh the daemon:
  ```bash
  ros2 daemon stop && ros2 daemon start
  ```
- Not a refactor bug — standard daemon behaviour.

## Fixed

### `fasttube_planner` hardcoded DEBUG override removed (was Outstanding)
- **Was:** when only one cone colour was in view, `loop()` emitted a crude 2-point hard turn ("full right"/"full left") and logged `DEBUG: only blue cones -> full right` every tick — short-circuiting the real planner with a `return` before any boundary logic ran (`fasttube_planner.py:58-83`, marked `>>> DEBUG override`/`>>> CHANGED`). The default planner, and not present in the other two.
- **Fix:** deleted the `len(lb)`/`len(rb)` single-colour branch. One-sided frames now return no trajectory — matching `fasttube_without_kalman` / `centerline_planner`.
- **Also:** the per-tick `loop()` log `car pose received = ...` (`fasttube_planner.py:51`) is now **commented out** (kept for quick re-enable).
- **Follow-up crash found on first live run (2026-07-02, fixed):** the original fix note claimed empty boundaries "fall through to the existing `lblocal`/`rblocal` length check" — but that check ran *after* `get_next_points()`, which crashes on an empty array (`np.argmin` of a zero-length `np.linalg.norm` → `ValueError: operands could not be broadcast together with shapes (2,) (0,)`). Triggered every startup: `car_position` arrives at camera rate (~60 Hz) before the first SLAM `left_track`/`right_track` message, so `loop()` always ran once with empty lists and killed the node. Fixed by adding an explicit `if len(lb) == 0 or len(rb) == 0: return` guard *before* `get_next_points()` (`fasttube_planner.py:65`).
- **Origin of the hole (git archaeology, 2026-07-03):** `fasttube` originally had the same pre-`get_next_points` guard as the other two planners. Old-repo commit `f7822f6` ("fasttube steering override", Jul 2025) **deleted that guard** and put the DEBUG override in its slot — the override only handled the two one-sided cases, leaving both-empty unprotected. The refactor ported the hacked version faithfully; removing the override left nothing. So the new guard is a *restoration*, not a new defence.
- **Why it never crashed before the wrapper conversion:** (a) in the **old repo** the planner never received a pose at all — the SDK node published `zed/car_position` while all planners + Stanley subscribed bare `car_position`, with no remap; `loop()` (the only path to the crash) never fired. The refactor's namespace unification connected pose→planner for the first time. (b) On the **new repo with the SDK build**, the pose came from a dedicated ~10 Hz thread while tracks rode the ~frame-rate detection stream, and the planner (slow numba import) subscribed last — so the first message was almost always a track, and once boundaries are populated they never empty again. (c) The **wrapper conversion** made the pose publish from `image_callback` every frame, unconditionally, always ahead of the gated detection→mapper→track chain — the race became a guaranteed loss, hence "triggered every startup".
- **Note:** `fasttube` and `centerline_planner` still carry near-identical copies of `loop()`/`get_next_points()` — the duplication that let one copy silently lose its guard. Consolidation candidate.

### `robot_state_publisher` never launched — `robot_description` not wrapped in `ParameterValue` (found during the LiDAR port)
- **Symptom:** `urdf_model.launch.py` (pulled in by `description.launch.py`, always launched) aborted on jazzy: *"Unable to parse the value of parameter robot_description as yaml."* So `robot_state_publisher` never started → **no static sensor TF was ever published** (worse than the known `state_publisher` issue, which is only the `odom→base_link` edge).
- **Cause:** `robot_description` was passed as a raw `FileContent` substitution; launch tries to parse the URDF XML as YAML unless it's wrapped as an explicit string.
- **Fix:** wrap in `ParameterValue(urdf, value_type=str)`; dropped the redundant `arguments=[urdf]`. Also parameterised the URDF via a `urdf:=` arg, defaulting to the **trolley** (`trolly.urdf.xml`) since that's the platform autonomy is tested on; `urdf:=gocartv1.urdf.xml` selects the go-kart.
- **Verified:** RSP starts; `base_link→velodyne` = `[0.25,0,1.0]` and `camera_link→velodyne` = `[0,0,-0.05]` publish on `/tf_static`.

### `can_decoder` import fixed — `AckermannStamped` -> `AckermannDriveStamped` (was Outstanding)
- **Was:** `can_decoder` died at import — `ImportError: cannot import name 'AckermannStamped' from 'ackermann_msgs.msg'` (`can_decoder_jnano.py:7`, also used at 50/95). Pre-existing bug ported faithfully from the old repo, not a refactor break.
- **Fix:** renamed all 3 sites to `AckermannDriveStamped`. The node's existing field usage (`.drive.speed`, `.drive.steering_angle`, `.header.stamp`) already matches `AckermannDriveStamped`, so no other changes were needed.
- **Effect:** the node can now start. `/fsae/hardware/drive_status` is now typed `AckermannDriveStamped`. No in-tree subscriber (orphan), so the type change is safe in-repo; confirm any external/off-board consumer expects `AckermannDriveStamped`.
- **Residual:** the unrelated `+`-instead-of-bit-packing issue for 16-bit CAN values is still open (see `MIGRATION.md` §8). And the node still needs a hardware link to receive frames — see `candapter_node` (CanTalk, vendored but launch-commented) in `CANTALK_INTEGRATION.md`.

### `can_id` silently changed 768 -> 300 by the refactor (REFACTOR REGRESSION)
- **Symptom:** on-car, the kart ignores drive command frames (`ackermann_to_can` sends on the wrong CAN id). Not visible off-car (no hardware link yet).
- **Cause:** `ack_to_can.py:52` declares `can_id` with a node default of `300` (decimal) in **both** repos. In the old repo this default was **always overridden**: every launch (`base.launch.py`, `gocart_autonomous`, `gocart_autonomous_no_kalman`, and both test launches) passed `default_value='0x300'` (=768), so the running system commanded the car on **768**. The refactor moved config into `fsae_params.yaml` and baked in the *unused node default* (`can_id: 300`) with nothing overriding it — so the effective id dropped to 300. This is one of only two true refactor regressions (the other was the centerline viz, below).
- **Fix:** set `ackermann_to_can.can_id: 768` in `fsae_params.yaml` (= 0x300, used decimal to avoid YAML hex-parse ambiguity). The previous YAML comment was misleading — it anchored on the node default (300) and framed `0x300` as an open question, but the old launches unanimously used 0x300.
- **Residual:** firmware should still confirm 768 is the current command frame id, but it's what the last working system used, so it's the safe restore. 300 is definitely wrong.

### Centerline never rendered in RViz — viz node listened to a dead interface
- **Symptom:** detections show in RViz, centerline never does. `/fsae/viz/centerline` silent.
- **Cause:** `visualise_trajectories.py` (ported from the old foxglove viz) subscribes to the multi-trajectory interface (`AllTrajectories` on `/fsae/planning/trajectories` + `/fsae/planning/inbound_trajectories` + `best_trajectory_index`). The refactor cut planners down to a single `PoseArray` on `/fsae/planning/selected_trajectory`. **Nothing publishes `AllTrajectories`**, so `show_paths()` (the only publisher of `/fsae/viz/centerline`) could never fire.
- **Fix:** added a `PoseArray` subscription to `/fsae/planning/selected_trajectory` + a `show_centerline()` callback (reuses `get_marker_from_pose` / `delete_all_markers`). Sets `orientation.w = 1.0` since the planner leaves it zeroed (RViz rejects a 0-norm quaternion). Old `AllTrajectories` subs left in place (harmless) for a future multi-trajectory planner.
- **Note:** verified live — `car_position`, `cone_detection` (blue + yellow), `selected_trajectory` all carry data. Must **restart** the viz node (Python doesn't reload source, even on a develop install):
  ```bash
  pkill -f publish_path_planning_msgs
  ros2 run fsae_visualization path_viz   # exe is 'path_viz'; node names itself publish_path_planning_msgs
  ```

### numpy 2 migration (apt → pip wheels for matplotlib / scipy / pandas)
- **Symptom:** `_ARRAY_API not found` / `numpy.dtype size changed` crashes on import.
- **Cause:** apt `matplotlib`/`scipy`/`pandas` were built against numpy 1.x; `fsd-path-planning` and `pyzed 5.3` need numpy >= 2. The two ABIs can't coexist in one process.
- **Fix:** go to numpy 2 (pyzed only supports it). pip-install numpy-2 wheels into `~/.local/...`, which shadows the apt copies on the import path:
  ```bash
  pip install --upgrade numpy matplotlib scipy pandas
  pip install -r ~/ros2_ws/src/fsae_autonomous/requirements.txt
  ```
- `requirements.txt` pins `matplotlib>=3.8`, `scipy>=1.11` so reinstalls don't revert to apt.
- **Cosmetic:** matplotlib warns `Unable to import Axes3D ... multiple versions of Matplotlib` — harmless, no 3D plots used.

### `fsd_path_planning` install silently failed (registered as `UNKNOWN`)
- **Symptom:** `ModuleNotFoundError: No module named 'fsd_path_planning'` at runtime.
- **Cause:** system pip 22.0.2 + setuptools 59.6.0 too old to parse the PEP 621 `[project]` table in the package's `pyproject.toml`; project name silently set to `UNKNOWN`, source dir never copied.
- **Fix:**
  ```bash
  pip uninstall -y UNKNOWN                       # remove the broken stub
  pip install --upgrade pip setuptools wheel     # PEP 621 needs setuptools >= 61
  pip install --no-cache-dir 'git+https://github.com/papalotis/ft-fsd-path-planning.git'
  ```

### setuptools 82 breaks all Python package builds
- **Symptom:** every `ament_python` package fails to rebuild — `error: option --editable not recognized` (`--symlink-install`) or `error: option --uninstall not recognized` (plain build). Latent until the first Python rebuild after the upgrade above.
- **Cause:** the `fsd_path_planning` fix pulled setuptools 82; setuptools >= 80 removed the legacy `setup.py install` / `develop` commands colcon invokes.
- **Fix:** pin a version with both PEP 621 support and the legacy commands (`fsd_path_planning` already installed, so unaffected):
  ```bash
  pip install --user 'setuptools==70.0.0'
  ```
- Add `setuptools<80,>=61` to `requirements.txt` / Dockerfile so it can't regress.

### `numba` (transitive of fsd-path-planning) needs newer `coverage`
- **Symptom:** `fasttube` / `fasttube_without_kalman` crash on import with `AttributeError: module 'coverage' has no attribute 'types'`.
- **Cause:** `numba 0.65.1` imports `coverage.types.Tracer`, absent from apt `coverage 6.2`.
- **Fix:**
  ```bash
  pip install --upgrade coverage     # 7.x has coverage.types
  ```

### `state_publisher` crashed + never broadcast — now fixed
- **Was:** node died with `AssertionError` at `state_publisher.py:37` (`t.transform.rotation = 0.0`, a float assigned to a Quaternion field). And even discounting the crash, it **never called `sendTransform`**, so `odom→base_link` was never published.
- **Fix:** set an identity quaternion (`rotation.w = 1.0`) and added `self.broadcaster.sendTransform(t)`. It now broadcasts a placeholder `odom→base_link` (car pinned at the odom origin) at 30 Hz until real odometry is wired in.
- **Verified:** `ros2 run tf2_ros tf2_echo odom base_link` → identity transform, no crash.
- **Note:** this re-introduces the latent two-parent risk on `base_link` (now `odom` via this node + `map` via `cone_map_viz` when `use_viz:=true`). Still needs the TF-ownership pass in `MIGRATION.md` §9.

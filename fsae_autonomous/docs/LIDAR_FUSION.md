# Camera–LiDAR cone fusion: concepts and algorithms

This document explains the *why* and *how* of the LiDAR cone-refinement
pipeline in `perception/fsae_lidar`. It is written for a team member who has
never seen this code: read this first, then the code should read as a direct
translation of these ideas. It deliberately stays at the level of concepts —
parameter values, topic names, and RViz setup live in the README and
`params/lidar_fusion.yaml`.

**Where things live:** all the geometry/maths is in
`fsae_lidar/refinement.py`, which is pure numpy with no ROS imports (and no
SciPy/scikit-learn — the Jetson's SciPy is broken against NumPy 2.x, and
nothing here needs it). The ROS wrapper — subscriptions, TF, parameters,
logging, RViz debug output — is `fsae_lidar/fusion_node.py`. If you are
looking for an algorithm, it is in `refinement.py`; if you are looking for
plumbing, it is in `fusion_node.py`.

---

## 1. Why LiDAR at all?

The car already detects cones with a stereo camera + YOLO. The camera is
excellent at two things LiDAR is hopeless at: *finding* cones and telling
their *colour* (blue/yellow/orange — which side of the track they mark). But
its third output, the cone's 3D position, is its weakest: stereo depth error
grows roughly quadratically with distance, and at racing-relevant ranges the
estimate is decimetres off and drifts with lighting, calibration, and motion.
Planning and SLAM consume positions, so position error propagates into
everything downstream.

The VLP-16 LiDAR is the mirror image: centimetre-accurate range measurements,
utterly colour-blind, and too sparse to *detect* small cones reliably on its
own (a cone at 7 m might return three points).

So the design splits the job by strength:

> **The camera proposes, the LiDAR verifies and locates.**
> Camera: "there is a yellow cone roughly *there*."
> LiDAR: "confirmed — and it is exactly *here*."

A fused cone carries the camera's colour and the LiDAR's position. If the
LiDAR cannot confirm a camera detection, the detection is **dropped entirely**
— by explicit team policy there is *no* camera-only position fallback at any
range, because a cone at a wrong position is more dangerous to the planner
than a missing cone (the cone will be re-detected as the car approaches;
a phantom may steer the car off line).

## 2. The central design decision: seeded local refinement

The single most important idea in the pipeline: **never process the whole
point cloud.** Finding cone-shaped clusters among tens of thousands of points
is a hard global problem (segmentation, global ground removal, model
fitting). But we do not have that problem — the camera already tells us where
to look.

For each camera detection, the seed position is projected into the LiDAR
frame via TF and the cloud is cropped to a **1 m-radius sphere** around it
(step A1). Every subsequent algorithm operates on that sphere's contents —
typically 30–150 points instead of ~30,000. This is what lets every algorithm
downstream be simple, local, and O(N²)-affordable:

- Ground can be modelled as a *single local plane* (any real track is flat
  across 2 m) instead of needing global terrain modelling.
- Clustering degenerates to connected components on a handful of points.
- Everything runs comfortably per-detection at sensor rate in Python.

The refinement (Component A) runs once per camera detection and either
returns a refined cone (xy position + quality metrics) or a machine-readable
failure reason. The sections below walk the sphere's contents through each
stage.

Two global conventions to know before reading on:

- Points are `(N, 5)` numpy arrays: `x, y, z, intensity, ring`. The *ring* is
  which of the VLP-16's 16 lasers produced the point; rings are fixed
  elevation angles, so one ring sweeps a horizontal circle through the scene.
- **Only xy matters for output.** Cones sit on the ground; the planner needs
  their 2D position. z is used internally (heights above ground) but never
  estimated or reported.

## 3. Ground removal (steps A4/A5)

**Problem:** inside the sphere, most points are floor. The cone is a small
bump of elevated points. Separate them.

**Approach: fit a local ground plane, keep points meaningfully above it.**

1. Take the lowest ~40 % of points by z and least-squares fit a tilted plane
   `z = ax + by + c`.
2. Refit once using *all* points within a few cm of that first plane.
3. Classify: a point more than `z_offset` (~3 cm) above the plane is cone
   candidate ("ABOVE_GROUND"); otherwise it is ground ("AT_GROUND").

Principles behind each choice:

- **Why a tilted plane, not a constant height?** The first implementation
  used `z_ground = median of the lowest points` — a horizontal cut. Field
  testing showed ground points surviving the filter near the sensor. Cause:
  the sensor is never perfectly level. Even 2° of mount tilt makes the
  floor's z vary by ~7 cm across a 1 m sphere — more than the whole 3 cm
  threshold. A plane with two slope coefficients absorbs mount tilt and track
  slope exactly. (Useful side effect: the fitted tilt is logged, and a
  consistent non-zero tilt across all spheres is a live measurement of the
  mount error — fix it in the URDF.)
- **Why the two-pass refit?** Selecting points *because they are low* prefers
  downward noise: the first fit lands ~1 cm below the true floor, which
  silently shrinks `z_offset` and lets floor noise through. Refitting on an
  unbiased band around the first fit removes the selection bias. This is the
  standard "seed then refit on inliers" pattern in miniature.
- **Why per-point height and not ring-based classification?** A tempting
  shortcut is "low rings = ground, high rings = cone". It cannot work: a
  single ring sweeping through the sphere hits the floor on either side of
  the cone *and* the cone itself, at the same ring ID. Ground/cone is a
  property of individual points, so only a per-point test can separate them.
  (Ring IDs are still used — but for verification and for the rescue pass,
  never for ground classification.)
- **Degenerate-fit guards.** A plane fitted to three nearly-collinear points
  (a single ring arc) can come out absurdly steep. Any fit steeper than ~17°
  or rank-deficient falls back to a horizontal plane at the median height —
  wrong by millimetres, never by metres.

## 4. Reclaiming the cone base (occlusion reasoning)

**Problem:** the bottom few centimetres of the cone are *physically at ground
height*. The height filter necessarily discards them — and on sparse far
cones, losing the bottom ring can mean losing a third of the evidence. No
`z_offset` value fixes this: lower eats ground, higher eats more cone.

**Approach: reclaim discarded points that lie inside the cone's footprint,
justified by occlusion.** The LiDAR cannot see the floor *behind or beneath*
the cone — the cone blocks it. So a return at ground height *inside the
cone's footprint* is almost certainly the cone's base, not floor.

The footprint test is deliberately done in **polar coordinates (bearing and
range from the sensor), not as a circle on the floor**. This matters and was
learned the hard way:

- A first version reclaimed everything within an xy radius of the cone. When
  a ground ring happened to sweep just in front of the cone, its arc cut a
  chord through that circle and a ~25 cm streak of genuine floor was
  reclaimed as "cone".
- A cone of known size can only occupy a *narrow bearing window* at a given
  range (±atan(base_radius / range) — about ±1° at 5 m) and a *shallow range
  window* (its surface spans one base-radius of depth). The passing arc's
  side arms violate the bearing window immediately; most of its front strip
  violates the range window. A cone-shaped acceptance window in (bearing,
  range) keeps the true base and rejects the arc.
- The window is anchored on the cone **axis**, estimated from the surviving
  points: each survivor's height implies its expected distance from the axis
  (cone geometry, section 6), so `axis_range = mean(range + r(height))`. The
  range window is *asymmetric* around it — all visible surface is in front of
  the axis — which is what accommodates the cone's slant (base closer to the
  sensor than the top).

**Why leaked floor points bias the position in one direction (worth
understanding):** misclassified floor can only ever be *in front of* the cone
— there is no visible floor behind it. Left/right leaks cancel by symmetry in
the averaging step, but "too close" has no "too far" partner to cancel
against, so floor leakage always drags the estimated centroid toward the
sensor. That one-sided-bias argument is why shrinking the leak (polar window)
was worth doing even though the centroid averaging tolerates a few bad
points.

If *no* points survived the height filter there is nothing to anchor on and
the reclaim is skipped — that case belongs to the rescue pass below.

## 5. The far-cone rescue (within-ring range dip)

**Problem:** beyond ~6–7 m, ring spacing (3.5 % of range) exceeds the cone
height, so usually only *one* ring hits the cone. If that ring crosses the
cone low — inside the `z_offset` band — the height filter discards every
cone point. Height carries no signal at all in this case.

**Approach: use range structure within the ring instead.** A laser that hits
a cone stops early; its neighbours on the same ring continue to the floor
metres behind. So along one ring, sorted by azimuth, a cone appears as a
**compact run of consecutive points whose range dips sharply below the
ring's floor level**, with cliff edges either side. That signature:

- survives point jitter (it is a ~1 m range step against ~3 cm noise, unlike
  arc-curvature tests where signal ≈ noise),
- is independent of z entirely (works at exactly the heights where the
  height filter is blind),
- is per-point *within* a ring, so it does not violate the "no ring-level
  classification" rule above.

A run qualifies if it is at least `dip_threshold` (~0.3 m) closer than the
ring's floor range (75th percentile of the ring's ranges — robust when cone
points are a large minority), has ≥ 2 points, and is no wider in azimuth
than a cone of known size could be at that range.

**Scope guard:** the rescue runs *only* when the normal path has already
failed (nothing survived the filter, or too few points to cluster). It can
therefore only add cones that would otherwise be dropped — it can never
change the result for a cone the normal pipeline handles. A camera mis-seed
aimed at empty floor finds no dip (flat floor has no range discontinuity)
and still drops.

## 6. Verification and the centroid (steps A6/A7)

### Clustering and gates

The surviving points are clustered in xy by **single-linkage connected
components** (points within `cluster_eps` of each other are connected; take
the largest component). This is deliberately *not* a library DBSCAN: at ≤100
points a full O(N²) distance matrix is trivial, the behaviour at
`min_samples≈3` is equivalent, and it is ~20 lines of dependency-free numpy.
Points from different rings of the same cone stack vertically — nearly
identical xy — so multi-ring cones merge into one cluster by construction,
and all rings contribute to a single centroid.

The winning cluster must then pass sanity gates before it is trusted:

- **Point count, range-aware.** Expected point count is a function of range
  (dozens at 3 m, a handful at 8 m), so a fixed minimum is the wrong shape:
  3 points minimum up close (a near cone giving 2 points means the camera
  seed is probably wrong — drop it), 2 beyond ~6 m (that *is* what a real
  far cone returns, and the camera seed corroborates it). The upper bound
  (~hundreds) exists only to reject walls and people.
- **Physical extent.** A cluster wider than ~0.3 m in xy or taller than
  ~0.35 m is not a cone, whatever else it looks like.

Every failure returns a **reason code** (`NO_POINTS_IN_SPHERE`,
`ALL_POINTS_AT_GROUND`, `NO_CLUSTER`, `CLUSTER_TOO_WIDE`, …) rather than a
bare failure. The codes matter operationally: they are printed per-cone in
the frame log, they distinguish "LiDAR can't see that far" from "the camera
is probably hallucinating", and they were how the far-cone failure modes in
sections 4–5 were diagnosed in the field.

### The centroid: per-point axis projection

**Problem:** all LiDAR points lie on the cone's *front surface* — a short
arc facing the sensor. The naive centroid of those points sits on that
surface, several cm in front of the true axis. The original plan (fit a
circle to the arc, e.g. Kasa fit) fails on this data for two reasons:

1. **Short noisy arcs make circle fits ill-conditioned.** With 3–15 points
   spanning well under half the circumference and ±3 cm jitter, the fitted
   radius — and with it the centre — swings wildly. Fitting amplifies the
   noise.
2. **The points are not on one circle.** A cone's radius shrinks with
   height, and the points come from rings at different heights: the xy
   projection is a superposition of circles of different radii. A single
   circle is the wrong model even with zero noise.

**Approach: don't fit anything — project each point through the cone.** The
cone's dimensions are known exactly (they are a parameter — measure the
actual cones in use). For each point:

1. Its height above the fitted ground plane gives the cone's radius at that
   height: `r(h) = base_radius × (1 − h/height)`.
2. The beam direction (sensor → point, in xy) points approximately *through*
   the cone's axis, because the surface the beam hit is round.
3. Push the point along its beam by `r(h)`: an independent estimate of the
   axis position.

The refined position is the **mean of all these per-point estimates**,
across every point of every ring. Why this beats fitting:

- Each point votes independently; jitter *averages out* (√N) instead of
  being amplified through a model fit.
- Different rings having different radii is handled exactly, per point.
- It degrades gracefully: it produces a sane answer from 3 points, even 2 —
  precisely the regime far cones live in.
- The residual error is small and mostly self-cancelling: points at the
  edges of the visible arc get pushed slightly sideways, but symmetrically —
  the left and right errors cancel in the mean (the same symmetry argument
  as in section 4, which is also why the *one-sided* floor leakage there was
  the thing worth fixing).

The result carries a **confidence** (a saturating function of point count
and ring count — more rings = better height diversity = better projection)
so downstream consumers (SLAM's Kalman filter) can weight far sparse cones
appropriately. Frame-to-frame smoothing is deliberately *not* done here —
single-frame estimates are kept unbiased and independent, and temporal
fusion is `cone_mapper`'s job.

## 7. How it all fits together

Per LiDAR/camera frame pair, for each camera detection:

```
camera seed (colour, position in camera frame)
        │  TF: camera_link → velodyne
        ▼
A1  crop cloud to 1 m sphere around seed          ── no points? drop: NO_POINTS_IN_SPHERE
        ▼
A4  fit local ground plane (2-pass, tilt-aware)
A5  height filter: keep points > z_offset above plane
        ▼
    reclaim base points inside polar cone footprint (occlusion)
        ▼
    nothing survived, or too few to cluster?
        └─ range-dip rescue on the discarded points ── still nothing? drop
        ▼
A6  connected-components cluster in xy → largest
    gates: range-aware count, width, height        ── fail? drop with reason
        ▼
A7  per-point axis projection → mean = (x, y)
        ▼
RefinedCone { x, y, point_count, ring_count, mean_intensity, confidence }
        + camera's colour  →  fused cone
```

Failures are dropped and logged with their reason; successes are logged with
both the refined and the camera position (their gap is a live read on camera
error and extrinsic calibration). Everything is visualised in RViz — the
kept/discarded point split, the fitted ground plane disc, the crop spheres,
and the refined centroid footprint — because the team's verification
workflow is live testing against real cones, not synthetic tests.

**Component B (time sync + publishing):** each camera detection is paired
with the LiDAR cloud nearest in header-stamp time, within a tolerance
(default 50 ms — at 20 m/s of car speed, 50 ms of skew is already a metre of
position error, which is why "just use the latest cloud" was never
acceptable for fast driving). Detections that miss their cloud wait in a
short queue and expire after ~200 ms. Each cloud pairs at most once, so the
fused output runs at the LiDAR's rate — the slower, gating sensor. The
result is published as a `ConeDetection` on `/cone_detection_fused` with
LiDAR-refined positions expressed back in the camera's frame and the
camera's colours/pose — deliberately the *same message and conventions* as
the raw camera topic, so downstream consumers (SLAM) switch over with a
topic remap and no code changes. Confidence is currently log-only; carrying
it downstream needs a custom message (future work). Still unbuilt: the
optional LiDAR-only "orphan" pass for cones the camera missed (a
clearly-marked TODO stub in the node).

## 8. Recurring design principles

Reading the code you will see the same few ideas over and over; they are the
house style of this pipeline:

- **Locality first.** The sphere crop converts every hard global problem
  into an easy local one. If a proposed feature needs the whole cloud, it
  probably belongs elsewhere.
- **Use known geometry instead of fitting models.** Cone dimensions, beam
  geometry, ring elevations, occlusion — these are certainties. Every
  algorithm above (axis projection, polar footprint, angular-width checks,
  range-dip) substitutes a certainty for a fit. Fits amplify noise; geometry
  does not.
- **Per-point physics beats per-structure heuristics.** Height above plane,
  range along a beam, bearing from the sensor — tests on individual points,
  derived from how the sensor actually works.
- **Every accept/reject decision is asymmetric in cost.** A phantom cone is
  worse than a missing one (hence: drop on failure, strict gates up close,
  no camera fallback). A missing far cone is cheap (it will be seen again,
  closer). Thresholds encode this asymmetry deliberately.
- **Fail with a reason.** Machine-readable reason codes turned two vague
  field complaints ("far cones disappear") into two precise, separately
  fixable failure modes.
- **Pure maths / ROS shell separation.** `refinement.py` can be run and
  probed anywhere numpy exists; the node stays thin. Keep it that way.

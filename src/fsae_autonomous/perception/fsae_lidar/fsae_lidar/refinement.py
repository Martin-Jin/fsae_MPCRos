"""LiDAR cone-refinement algorithm (Component A) — pure numpy, no ROS imports.

This module is kept free of any ROS dependency so the refinement maths stays
self-contained and runnable anywhere. The ROS-coupled parts (parsing a
``PointCloud2`` into a numpy array, TF, publishing) live in ``fusion_node.py``.
Verification is done live in RViz via the debug topics the node publishes.

It also deliberately avoids SciPy/scikit-learn: the target Jetson ships a
system SciPy built against NumPy 1.x while NumPy 2.x is installed, which makes
SciPy's compiled extensions unimportable. Everything here is plain NumPy, which
is fast enough — the sphere crop reduces tens of thousands of points to a small
local subset before any further work.

Point-cloud convention used throughout: an ``(N, 5)`` ``float`` array whose
columns are ``(x, y, z, intensity, ring)``.

Implemented so far: the sphere crop (A1), ground removal (A4/A5) — a local
tilted-plane fit followed by a height-above-plane filter and an
occlusion-based reclaim of the cone base, with a within-ring range-dip rescue
for far cones whose single low ring gets ground-filtered — and cluster
verification plus the axis-projection centroid (A6/A7). Component B
(time-synced fused publishing) is the remaining work and lives in
``fusion_node.py`` when it arrives.
"""

import math
from dataclasses import dataclass

import numpy as np

# Column indices for the (N, 5) point array.
X, Y, Z, INTENSITY, RING = 0, 1, 2, 3, 4


def crop_sphere(cloud: np.ndarray, seed_xyz, r_sphere: float) -> np.ndarray:
    """Return the subset of ``cloud`` within ``r_sphere`` of ``seed_xyz``.

    Keeps points satisfying ``(x-sx)^2 + (y-sy)^2 + (z-sz)^2 <= r_sphere^2``,
    using a vectorised squared-distance test (no kD-tree, no SciPy).

    Parameters
    ----------
    cloud : np.ndarray
        ``(N, 5)`` array of ``(x, y, z, intensity, ring)``.
    seed_xyz : array-like
        3D seed point ``(sx, sy, sz)`` already expressed in the LiDAR frame.
    r_sphere : float
        Sphere radius in metres.

    Returns
    -------
    np.ndarray
        ``(M, 5)`` subset of the input points inside the sphere (possibly empty).
    """
    cloud = np.asarray(cloud, dtype=float)
    if cloud.size == 0:
        return cloud.reshape(0, 5)
    seed = np.asarray(seed_xyz, dtype=float)
    diff = cloud[:, :3] - seed
    dist_sq = np.einsum('ij,ij->i', diff, diff)
    return cloud[dist_sq <= r_sphere * r_sphere]


# A least-squares ground fit steeper than this (rise over run, ~17 deg) is
# treated as ill-conditioned — real track slope plus mount tilt stays well
# under it — and we fall back to a horizontal plane.
MAX_GROUND_SLOPE = 0.30

# Inlier band for the unbiased second-pass ground fit (see fit_ground_plane).
GROUND_REFIT_BAND = 0.04


def _fit_plane_lstsq(sel: np.ndarray):
    """Least-squares ``z = a*x + b*y + c`` through ``sel``, or None if the fit
    is unreliable (fewer than 3 points, degenerate xy geometry, or a slope
    beyond MAX_GROUND_SLOPE — the usual symptom of fitting a near-collinear
    single ring arc)."""
    if sel.shape[0] < 3:
        return None
    design = np.column_stack([sel[:, X], sel[:, Y], np.ones(sel.shape[0])])
    coeffs, _, rank, _ = np.linalg.lstsq(design, sel[:, Z], rcond=None)
    a, b, c = (float(v) for v in coeffs)
    if rank < 3 or math.hypot(a, b) > MAX_GROUND_SLOPE:
        return None
    return a, b, c


def fit_ground_plane(points: np.ndarray, ground_percentile: float = 0.40):
    """Fit the local ground plane inside a cropped sphere (step A4).

    Least-squares fit of ``z = a*x + b*y + c``. A tilted plane (rather than a
    constant z) absorbs sensor mount tilt and track slope, which otherwise
    leak ground points past the height filter: 2 deg of tilt is ~7 cm of
    ground-z variation across a 1 m-radius sphere, more than the offset
    threshold.

    Two passes: the first fit uses the lowest ``ground_percentile`` of points
    by z, but selecting points *because they are low* prefers downward noise
    and biases that fit ~1 cm below the true ground — which silently shrinks
    the caller's z_offset and lets ground noise through the height filter. So
    the first fit only seeds an inlier band: the returned plane is refitted
    on ALL points within +-GROUND_REFIT_BAND of it, an unbiased selection.
    (Cone-base points inside the band join the refit; they are few against
    the ground points and shift the plane negligibly.)

    Falls back to the first-pass fit if the refit is degenerate, and to a
    horizontal plane at the median z of the low subset if both fits are.

    Parameters
    ----------
    points : np.ndarray
        ``(N, 5)`` array of ``(x, y, z, intensity, ring)`` with ``N >= 1``.
    ground_percentile : float
        Fraction of lowest-z points seeding the first fit (default 0.40).

    Returns
    -------
    (float, float, float)
        Plane coefficients ``(a, b, c)``; ground height at (x, y) is
        ``a*x + b*y + c``. The horizontal fallback returns ``(0, 0, median_z)``.
    """
    pts = np.asarray(points, dtype=float)
    n = pts.shape[0]
    n_ground = max(3, math.ceil(n * ground_percentile))
    if n_ground >= n:
        sel = pts
    else:
        idx = np.argpartition(pts[:, Z], n_ground - 1)[:n_ground]
        sel = pts[idx]

    first = _fit_plane_lstsq(sel)
    if first is None:
        return 0.0, 0.0, float(np.median(sel[:, Z]))

    a, b, c = first
    residual = pts[:, Z] - (a * pts[:, X] + b * pts[:, Y] + c)
    refit = _fit_plane_lstsq(pts[np.abs(residual) <= GROUND_REFIT_BAND])
    return refit if refit is not None else first


def split_ground(points: np.ndarray, ground_percentile: float = 0.40,
                 z_offset: float = 0.03):
    """Split a cropped sphere into above-ground and at-ground points (A4 + A5).

    Each point's verdict is its height above the fitted local ground plane:
    ABOVE_GROUND if ``z - (a*x + b*y + c) > z_offset``, else AT_GROUND. This
    is the sole ground/cone classifier — ring IDs play no part (a single ring
    hits both the ground and the cone within one sphere, so only a per-point
    height test can separate them). Points the plane test wrongly discards at
    the cone base are recovered afterwards by ``reclaim_cone_base``.

    Known limitation: if the sphere contains only cone points (no ground hits
    at all), the plane is fitted to the cone's own lowest points and the
    bottom ~z_offset of the cone is discarded. Harmless for the later xy arc
    fit.

    Parameters
    ----------
    points : np.ndarray
        ``(N, 5)`` array of ``(x, y, z, intensity, ring)``.
    ground_percentile : float
        Fraction of lowest-z points used to fit the ground plane.
    z_offset : float
        Height above the plane a point must exceed to count as cone
        (default 0.03 m — the tilt-compensated plane makes a tighter
        threshold safe, preserving more of the cone base).

    Returns
    -------
    (np.ndarray, np.ndarray, tuple | None)
        ``(above, ground, plane)`` — the ABOVE_GROUND subset (input to
        clustering), the discarded AT_GROUND subset (kept for visualisation),
        and the fitted plane ``(a, b, c)``. Both arrays are ``(M, 5)`` and may
        be empty; an empty input yields two empty arrays and ``plane = None``.
    """
    points = np.asarray(points, dtype=float)
    if points.size == 0:
        empty = points.reshape(0, 5)
        return empty, empty.copy(), None
    plane = fit_ground_plane(points, ground_percentile)
    a, b, c = plane
    height = points[:, Z] - (a * points[:, X] + b * points[:, Y] + c)
    above_mask = height > z_offset
    return points[above_mask], points[~above_mask], plane


def reclaim_cone_base(above: np.ndarray, ground: np.ndarray,
                      base_radius: float = 0.0625,
                      cone_height: float = 0.31, plane=None,
                      range_margin: float = 0.05,
                      bearing_margin: float = 0.05):
    """Recover cone-base points the height filter discarded (A5 second pass).

    Physical rationale: the LiDAR cannot see the ground inside the cone's
    footprint — the cone occludes it — so a return at ground height within
    the footprint is almost certainly cone base, not ground. The footprint is
    tested in polar (bearing/range) space rather than as an xy disc: a ground
    ring sweeping just in front of the cone cuts a chord through any xy disc
    and gets wrongly reclaimed (dragging the centroid toward the sensor,
    since misclassified ground only ever sits in FRONT of the cone), but its
    side arms lie outside the bearing window a cone of known size can occupy
    and its front strip falls outside the range window.

    The anchor is the cone axis estimated from the survivors: each survivor's
    height above ``plane`` gives its expected surface radius r(h), so the
    axis range is ``mean(range + r(h))``. The acceptance window then hugs the
    cone's own depth — ranges in ``[axis - base_radius - range_margin,
    axis + range_margin]`` (asymmetric: the cone's visible surface all lies
    in front of the axis), bearings within ``atan((base_radius +
    bearing_margin) / axis_range)`` of the axis bearing. With no survivors
    there is no anchor and the reclaim is skipped — by policy such a
    detection is dropped entirely rather than falling back to the camera
    position.

    Parameters
    ----------
    above, ground : np.ndarray
        The ``(M, 5)`` ABOVE_GROUND / AT_GROUND splits from ``split_ground``.
    base_radius, cone_height : float
        Cone geometry for the seed's cone type.
    plane : tuple | None
        Fitted ground plane, for survivor heights. With ``None`` the surface
        radius falls back to ``base_radius / 2`` for the axis estimate.
    range_margin : float
        Range slack beyond the cone's own depth (default 0.05 m — point
        jitter plus axis-estimate error; the field-tuning knob for how much
        floor directly in front of the base can sneak in).
    bearing_margin : float
        Cross-range slack added to the cone's angular half-width (default
        0.05 m).

    Returns
    -------
    (np.ndarray, np.ndarray)
        ``(above, ground)`` with reclaimed points moved from ``ground`` into
        ``above``. Unchanged if either input is empty.
    """
    if above.shape[0] == 0 or ground.shape[0] == 0:
        return above, ground

    ranges = np.hypot(above[:, X], above[:, Y])
    if plane is not None:
        a, b, c = plane
        h = above[:, Z] - (a * above[:, X] + b * above[:, Y] + c)
        radii = base_radius * np.clip(1.0 - h / cone_height, 0.0, 1.0)
    else:
        radii = np.full(above.shape[0], base_radius / 2.0)
    axis_range = float((ranges + radii).mean())
    bearings = np.arctan2(above[:, Y], above[:, X])
    axis_bearing = float(np.angle(np.exp(1j * bearings).mean()))

    g_range = np.hypot(ground[:, X], ground[:, Y])
    g_bearing = np.arctan2(ground[:, Y], ground[:, X])
    d_bearing = np.abs(np.angle(np.exp(1j * (g_bearing - axis_bearing))))
    half_width = math.atan2(base_radius + bearing_margin, axis_range)

    reclaim_mask = (
        (g_range >= axis_range - base_radius - range_margin)
        & (g_range <= axis_range + range_margin)
        & (d_bearing <= half_width))
    if not reclaim_mask.any():
        return above, ground
    return np.vstack([above, ground[reclaim_mask]]), ground[~reclaim_mask]


def rescue_ground_dip(ground: np.ndarray, base_radius: float,
                      dip_threshold: float = 0.30, min_points: int = 2):
    """Rescue cone points hiding at ground height via a within-ring range dip.

    Last-resort recovery for the far-cone failure mode: beyond ~6 m usually a
    single ring hits the cone, and when it hits low (inside the z_offset
    band) the height filter discards every cone point — zero survivors, an
    ALL_POINTS_AT_GROUND drop. z cannot separate those points from ground,
    but range along the ring can: a beam that hits the cone stops short of
    where the rest of its ring lands, so the cone appears as a compact run of
    consecutive-azimuth points whose range dips well below the ring's ground
    level. Callers invoke this only when refinement would otherwise drop the
    cone (no height-filter survivors, or too few to cluster), so any cone the
    normal pipeline refines is unaffected.

    Per ring: points are sorted by wrap-safe azimuth, the ring's ground range
    is taken as the 75th percentile of ranges (robust even when cone points
    are a large minority of the subset), and contiguous runs at least
    ``dip_threshold`` closer than that are candidate cones. A run qualifies
    with >= ``min_points`` points and an azimuth extent consistent with a
    cone of ``base_radius`` at that range (2.5x noise margin). The largest
    qualifying run wins.

    Parameters
    ----------
    ground : np.ndarray
        ``(N, 5)`` AT_GROUND points from ``split_ground``.
    base_radius : float
        Cone base radius for the azimuth-width consistency check.
    dip_threshold : float
        Minimum range dip below the ring's ground level (default 0.30 m —
        comfortably above range noise, far below the multi-metre dip a real
        cone interception produces).
    min_points : int
        Minimum run length (default 2).

    Returns
    -------
    (np.ndarray, np.ndarray)
        ``(rescued, ground)`` — the rescued cone-candidate points and the
        remaining ground points. ``rescued`` is empty when no dip qualifies.
    """
    ground = np.asarray(ground, dtype=float)
    if ground.shape[0] < min_points + 3:
        return ground[:0], ground

    ranges = np.hypot(ground[:, X], ground[:, Y])
    azimuths = np.arctan2(ground[:, Y], ground[:, X])

    best = None
    for ring_id in np.unique(ground[:, RING]):
        sel = np.flatnonzero(ground[:, RING] == ring_id)
        if sel.size < min_points + 3:
            continue  # too few neighbours to establish the ground range
        ring_az = azimuths[sel]
        centre = np.angle(np.exp(1j * ring_az).mean())
        rel_az = np.angle(np.exp(1j * (ring_az - centre)))
        order = np.argsort(rel_az)
        ground_range = np.percentile(ranges[sel], 75)
        dipped = ranges[sel][order] < ground_range - dip_threshold

        runs = []
        start = None
        for i, d in enumerate([*dipped, False]):  # sentinel closes final run
            if d and start is None:
                start = i
            elif not d and start is not None:
                runs.append((start, i))
                start = None
        for s, e in runs:
            run = sel[order[s:e]]
            if run.size < min_points:
                continue
            half_width = math.atan2(base_radius, float(ranges[run].mean()))
            extent = float(rel_az[order[e - 1]] - rel_az[order[s]])
            if extent > 2.5 * 2.0 * half_width:
                continue  # wider than any cone at this range
            if best is None or run.size > best.size:
                best = run

    if best is None:
        return ground[:0], ground
    keep = np.ones(ground.shape[0], dtype=bool)
    keep[best] = False
    return ground[best], ground[keep]


# Reason codes for a failed refinement. The first two are produced by the
# caller before clustering is reached; the rest by verify_and_locate. Policy:
# a failed refinement drops the camera detection entirely — no camera-position
# fallback at any range.
NO_POINTS_IN_SPHERE = 'NO_POINTS_IN_SPHERE'
ALL_POINTS_AT_GROUND = 'ALL_POINTS_AT_GROUND'
NO_CLUSTER = 'NO_CLUSTER'
TOO_MANY_POINTS = 'TOO_MANY_POINTS'
CLUSTER_TOO_WIDE = 'CLUSTER_TOO_WIDE'
CLUSTER_TOO_TALL = 'CLUSTER_TOO_TALL'


@dataclass
class RefinedCone:
    """LiDAR-refined cone location (xy only — z is never estimated)."""

    x: float
    y: float
    point_count: int
    ring_count: int
    mean_intensity: float
    confidence: float


def largest_xy_cluster(points: np.ndarray, eps: float) -> np.ndarray:
    """Return the largest xy-connected component of ``points`` (step A6).

    Single-linkage connected components: two points are connected when their
    xy distance is <= ``eps``. At the scale this runs at (a few dozen points
    inside one sphere) this is behaviourally equivalent to DBSCAN with a small
    min_samples, with far less machinery. The O(N^2) distance matrix is
    trivial for N < ~100; callers should not pass whole clouds.

    Points from different LiDAR rings on the same cone stack vertically, so
    they share xy locations and merge into one cluster here — a multi-ring
    cone always yields a single combined cluster (and thus a single centroid).

    Parameters
    ----------
    points : np.ndarray
        ``(N, 5)`` array of ``(x, y, z, intensity, ring)``.
    eps : float
        Connection radius in xy, metres.

    Returns
    -------
    np.ndarray
        ``(M, 5)`` subset forming the largest component (empty for empty
        input; ties broken arbitrarily).
    """
    points = np.asarray(points, dtype=float)
    n = points.shape[0]
    if n == 0:
        return points.reshape(0, 5)
    diff = points[:, None, :2] - points[None, :, :2]
    adjacency = np.einsum('ijk,ijk->ij', diff, diff) <= eps * eps

    labels = np.full(n, -1, dtype=int)
    n_labels = 0
    for i in range(n):
        if labels[i] >= 0:
            continue
        member = np.zeros(n, dtype=bool)
        member[i] = True
        frontier = member.copy()
        while frontier.any():
            reachable = adjacency[frontier].any(axis=0) & ~member
            member |= reachable
            frontier = reachable
        labels[member] = n_labels
        n_labels += 1

    return points[labels == np.argmax(np.bincount(labels))]


def _axis_projection_xy(cluster: np.ndarray, plane, base_radius: float,
                        cone_height: float, r_fallback: float) -> np.ndarray:
    """Project every cluster point onto the cone axis and average (step A7).

    Each LiDAR return sits on the cone's front surface; the beam direction
    (sensor origin -> point, in xy) points approximately through the cone
    axis. A point's height above the fitted ground plane gives the cone
    radius at that height, ``r(h) = base_radius * (1 - h / cone_height)``
    (clamped to [0, base_radius] so noise above the tip or below the plane
    cannot produce a bogus radius). Pushing the point along its beam by
    ``r(h)`` yields an independent xy estimate of the axis; the mean over all
    points — across every ring on the cone — is the centroid. Per-point noise
    averages out here rather than being amplified as a short-arc circle fit
    would.

    With ``plane=None`` (no ground fit available) all points are pushed by
    the constant ``r_fallback`` instead.
    """
    xy = cluster[:, :2]
    if plane is not None:
        a, b, c = plane
        h = cluster[:, Z] - (a * cluster[:, X] + b * cluster[:, Y] + c)
        radii = base_radius * np.clip(1.0 - h / cone_height, 0.0, 1.0)
    else:
        radii = np.full(cluster.shape[0], r_fallback)
    norms = np.maximum(np.linalg.norm(xy, axis=1), 1e-9)
    beam_dirs = xy / norms[:, None]
    return (xy + radii[:, None] * beam_dirs).mean(axis=0)


def verify_and_locate(above: np.ndarray, plane, *, cluster_eps: float = 0.12,
                      min_points: int = 3, min_points_far: int = 2,
                      far_range_threshold: float = 6.0,
                      max_points: int = 250,
                      max_width: float = 0.30, max_height: float = 0.35,
                      base_radius: float = 0.0625, cone_height: float = 0.31,
                      r_fallback: float = 0.05):
    """Verify the cone cluster and compute its xy centroid (steps A6 + A7).

    Clusters the ground-filtered points in xy, gates the largest cluster on
    point count and physical extent (a 1 m-wide "cluster" is a wall or a
    person, not a cone), then locates the cone axis via per-point axis
    projection. ``max_height`` gates the cluster's z *extent* as a sanity
    check only — the returned position is xy, no z is estimated.

    The point-count minimum is range-aware: ``min_points`` applies within
    ``far_range_threshold`` of the sensor (a close cone yielding 2 points is
    a probable camera mis-seed and is dropped), ``min_points_far`` beyond it
    (a far cone physically returns only 2-3 points, and the camera seed
    already corroborates the location).

    Parameters
    ----------
    above : np.ndarray
        ``(N, 5)`` ground-filtered (and base-reclaimed/rescued) points.
    plane : tuple | None
        Fitted ground plane ``(a, b, c)`` from ``split_ground``.
    cluster_eps, min_points, min_points_far, far_range_threshold,
    max_points, max_width, max_height : ...
        A6 clustering radius and verification gates.
    base_radius, cone_height : float
        Cone geometry for the seed's cone type.
    r_fallback : float
        Constant projection radius used when ``plane`` is None.

    Returns
    -------
    (RefinedCone | None, str)
        The refined cone and ``''``, or ``None`` and a reason code.
    """
    cluster = largest_xy_cluster(above, cluster_eps)
    n = cluster.shape[0]
    min_required = min_points
    if n:
        centroid_range = float(np.hypot(*cluster[:, :2].mean(axis=0)))
        if centroid_range > far_range_threshold:
            min_required = min_points_far
    if n < min_required:
        return None, NO_CLUSTER
    if n > max_points:
        return None, TOO_MANY_POINTS
    if max(np.ptp(cluster[:, X]), np.ptp(cluster[:, Y])) > max_width:
        return None, CLUSTER_TOO_WIDE
    if np.ptp(cluster[:, Z]) > max_height:
        return None, CLUSTER_TOO_TALL

    cx, cy = _axis_projection_xy(
        cluster, plane, base_radius, cone_height, r_fallback)
    ring_count = int(np.unique(cluster[:, RING]).size)
    # Heuristic quality score: saturates at 10 points / 3 rings. More rings
    # mean better height diversity for the projection, so they weigh equally
    # with raw point count.
    confidence = (0.5 * min(1.0, n / 10.0)
                  + 0.5 * min(1.0, ring_count / 3.0))
    return RefinedCone(
        x=float(cx), y=float(cy), point_count=int(n), ring_count=ring_count,
        mean_intensity=float(cluster[:, INTENSITY].mean()),
        confidence=confidence), ''

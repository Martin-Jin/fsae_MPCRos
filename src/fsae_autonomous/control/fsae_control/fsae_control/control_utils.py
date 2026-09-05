import math

import numpy as np

# FSDS: max steering angle 25 degrees per ros-bridge.md
MAX_STEER_RAD = math.radians(25.0)

# Planning-level braking capability (m/s^2, positive magnitude) used by
# curvature_speed()'s braking-distance propagation. Deliberately below the
# vehicle's true limit (~9 m/s^2): the tyres also need lateral force for the
# corner being braked into (friction circle), plus margin for model error and
# actuation lag. Mirrors a_brake_max in fsae_MPCTest/sim/speed_profile.py.
A_BRAKE_PLAN = 5.0


def _heading_error(car_pos, car_yaw, target_global) -> float:
    """Return heading error in radians: positive when target is left of car."""
    dx = target_global[0] - car_pos[0]
    dy = target_global[1] - car_pos[1]
    cos_y, sin_y = math.cos(car_yaw), math.sin(car_yaw)
    x_car =  dx * cos_y + dy * sin_y
    y_car = -dx * sin_y + dy * cos_y
    return math.atan2(y_car, x_car)


def compute_steering(car_pos, car_yaw, target_global) -> float:
    """Pure-proportional steering (legacy helper, kept for reference)."""
    return float(np.clip(-_heading_error(car_pos, car_yaw, target_global)
                         / MAX_STEER_RAD, -1.0, 1.0))


class StanleyController:
    """
    Stanley path-tracking steering controller (Thrun et al., DARPA 2005).

    δ = θ_e + arctan(k_cte · e / (v + k_soft))

    θ_e — heading error: path tangent angle minus car yaw (rad).
          Positive when path turns left relative to the car.
    e   — cross-track error: signed lateral distance from the front axle
          to the nearest path point (m), positive when the axle is to
          the RIGHT of the path.
    v   — car speed (m/s); k_soft prevents division by zero at standstill.

    Sign convention (FSDS ENU: x forward, y left):
      output > 0  → steer right
      output < 0  → steer left
      output ∈ [-1, 1]

    Tuning:
      k_cte     — cross-track gain.  Higher values correct lateral error faster
                  but cause oscillation on a high-speed straight.
      k_soft    — speed softening (m/s).  Set to ~walking speed so the CTE
                  term doesn't saturate the steering at low speeds.
      k_d       — yaw-rate damper gain.  Subtracts k_d·ω from the Stanley
                  angle before normalising, opposing rapid heading changes.
                  This is the primary fix for left-right sway: the CTE term
                  alone has no memory of how fast the heading is already
                  changing, so it overshoots; k_d·ω counters each swing.
      wheelbase — distance from rear to front axle (m).  Used to project
                  the control point to the front axle, which is where Stanley
                  measures cross-track error.
    """

    def __init__(
        self,
        k_cte: float = 1.0,
        k_soft: float = 1.0,
        k_d: float = 0.1,
        wheelbase: float = 1.5,
    ):
        self.k_cte     = k_cte
        self.k_soft    = k_soft
        self.k_d       = k_d
        self.wheelbase = wheelbase
        # Last tick's tracking error, in the SAME sign convention as
        # mpc_core.py's last_telemetry (+ve = left/CCW) so both controllers'
        # e_y/e_psi are directly comparable in telemetry_logger.py's CSV —
        # see compute()'s sign flip on `e` below. Exposed for ControlLogger;
        # not used internally by compute() itself.
        self.last_e_y: float = 0.0
        self.last_e_psi: float = 0.0

    def compute(
        self,
        path: np.ndarray,
        car_pos: np.ndarray,
        car_yaw: float,
        car_speed: float,
        car_yaw_rate: float = 0.0,
    ) -> float:
        """
        Return a steering command in [-1, 1].

        path         — (N, 2) array of waypoints in map frame (must have N ≥ 2)
        car_pos      — (2,) car position in map frame
        car_yaw      — car heading in radians
        car_speed    — car speed in m/s
        car_yaw_rate — yaw rate in rad/s (positive = left / CCW); used by the
                       damper term to oppose rapid heading changes

        Also updates self.last_e_y / self.last_e_psi (see their docstring).
        """
        if len(path) < 2:
            return 0.0

        # Project control point to front axle
        fa = car_pos + self.wheelbase * np.array([math.cos(car_yaw), math.sin(car_yaw)])

        # Nearest waypoint index to front axle
        idx = int(np.argmin(np.linalg.norm(path - fa, axis=1)))

        # Unit tangent in direction of travel at that waypoint
        if idx < len(path) - 1:
            seg = path[idx + 1] - path[idx]
        else:
            seg = path[idx] - path[idx - 1]
        seg_len = float(np.linalg.norm(seg))
        if seg_len < 1e-6:
            return 0.0
        t = seg / seg_len

        # Heading error: path_yaw - car_yaw, normalised to (-π, π)
        path_yaw = math.atan2(t[1], t[0])
        theta_e = math.atan2(
            math.sin(path_yaw - car_yaw),
            math.cos(path_yaw - car_yaw),
        )

        # Cross-track error: right-normal of path, positive = axle right of path
        right_n = np.array([t[1], -t[0]])   # 90° CW rotation of tangent
        e = float(np.dot(fa - path[idx], right_n))

        # Expose this tick's error in mpc_core.py's sign convention (+ve =
        # left/CCW) — e above is +ve RIGHT, the opposite — so a Stanley log
        # and an MPC log can be plotted on the same axis without a manual
        # sign flip. theta_e already matches (+ve = path turns left of car).
        self.last_e_y = -e
        self.last_e_psi = theta_e

        # Stanley angle — positive = left turn (standard convention).  Damper
        # subtracts k_d·ω: when the car is already swinging left (ω > 0), this
        # reduces δ so the next tick steers less left, preventing overshoot.
        delta = (theta_e
                 + math.atan2(self.k_cte * e, car_speed + self.k_soft)
                 - self.k_d * car_yaw_rate)

        # Return the steering ANGLE in radians (positive = left), clamped to the
        # physical limit.  FSDS normalisation (+1 = right) is done by fsds_bridge.
        return float(np.clip(delta, -MAX_STEER_RAD, MAX_STEER_RAD))


def tracking_error_speed_gate(e_y, e_psi,
                              ey_lo=0.5, ey_hi=2.0,
                              epsi_lo=math.radians(20.0), epsi_hi=math.radians(60.0),
                              floor=0.3):
    """
    Multiplier in [floor, 1] that scales the speed target down when the car is
    failing to track the path.

    curvature_speed() only looks at the shape of the path ahead, not where the
    car actually is relative to it, so it will happily command full speed down
    a straight while the car is badly off-line. This gate ramps the target
    down (linearly) once |e_y| or |e_psi| exceeds its _lo threshold, taking
    the worse of the two, and saturates at `floor` rather than 0 above _hi —
    the car still needs some speed to steer itself back to the path.

    The five default thresholds are reasonable-default judgement calls, not
    independently measured/tuned: _lo is set well past normal tracking noise
    so the gate doesn't fire during ordinary driving, _hi is set at a clearly
    "badly off" error, and floor stops short of zero so the car never loses
    all steering authority. Retune via tuning.md if live data suggests either
    threshold fires too early/late.

    Parameters
    ----------
    e_y : float     Lateral tracking error (m).   Sign ignored.
    e_psi : float   Heading tracking error (rad). Sign ignored.
    ey_lo/ey_hi, epsi_lo/epsi_hi : float
        Ramp start/end. At/below _lo -> 1.0; at/above _hi -> floor.
    floor : float   Minimum multiplier.

    Returns
    -------
    float in [floor, 1.0]
    """
    if ey_hi <= ey_lo or epsi_hi <= epsi_lo:
        return 1.0
    gy = 1.0 - (abs(float(e_y)) - ey_lo) / (ey_hi - ey_lo)
    gp = 1.0 - (abs(float(e_psi)) - epsi_lo) / (epsi_hi - epsi_lo)
    return float(np.clip(min(gy, gp), floor, 1.0))


def curvature_speed(waypoints, v_max=15.0, v_min=1.5, a_lat_max=4.75,
                    scan_start=0.0, scan_end=24.0, step=2.0, safety=1.0):
    """
    Curvature-limited target speed over the next scan_end metres of the path.

    Ported from the planner's speed logic so the controller can set cmd_vel.speed
    without a cross-package import. v_target = safety·√(a_lat_max / κ_peak) for
    each corner in the scan window, propagated for braking distance (see below)
    and reduced to the most restrictive value. A short-path cap (scales v_max
    down when the visible path is shorter than scan_end) applies only when
    there isn't enough path to measure curvature at all — once curvature has
    been measured, the short-path cap is not reapplied on top of v_target.
    waypoints[0] is assumed to be the car's current position.

    scan_end=24 m is sized so a tight hairpin (~2 m radius, v_target ~2.7 m/s)
    approached at v_max is visible far enough out to brake for at a realistic
    deceleration; a shorter scan sees the corner too late, saturating steering
    at corner entry. Kept in sync with the planner's own lookahead.

    Braking-distance propagation: each corner in the scan window is converted
    to the fastest speed from which that corner is still reachable at
    A_BRAKE_PLAN, and the most restrictive wins — otherwise a corner 24 m
    ahead and the same corner 2 m ahead give the same target, which can demand
    a deceleration the car cannot produce.

    scan_start=0.0: curvature measurement starts at the car's own position
    rather than ahead of it, so a short, tight corner isn't skipped by a dead
    zone (see the apex-blind-spot comment below).
    """
    n = len(waypoints)
    if n < 3:
        return float(v_max)

    segs  = np.linalg.norm(np.diff(waypoints, axis=0), axis=1)
    arc   = np.concatenate([[0.0], np.cumsum(segs)])
    total = arc[-1]

    v_max_eff = max(v_min, v_max * min(1.0, total / scan_end))
    if total < scan_start + step:
        return float(v_max_eff)

    hi = min(scan_end, total)
    # The planner re-fits the centreline every frame, so the published path
    # carries a few cm of per-point lateral wiggle even on a straight. Taking
    # the raw MAX Menger curvature over ~2 m triples turns that noise into a
    # spurious kappa and makes v_target oscillate frame-to-frame. Fix: densely
    # resample the scan window and moving-average denoise it before measuring
    # curvature — a real corner is a sustained bend that survives smoothing,
    # only the cm-scale wiggle is removed.
    #
    # pts_s0 is the arc distance ahead of the car of pts[0]. A width-w 'valid'
    # moving average places its first output at the centre of the first
    # window, (w-1)/2 * dense_step further along than scan_start, so this is
    # tracked explicitly to keep the braking propagation below honest.
    #
    # A short, tight corner's curvature can be sustained over only ~2-3 m of
    # arc, so scan_start=0.0, a fine dense_step (0.5) and a narrow smoothing
    # window (w<=3, no decimation) keep the effective measurement start close
    # to the car and leave enough samples inside a short apex zone to see it.
    pts = None
    pts_s0 = scan_start
    dense_step = 0.5
    dense = np.arange(scan_start, hi, dense_step)
    if len(dense) >= 7:                       # room to smooth and still leave >=3 triples
        dx = np.interp(dense, arc, waypoints[:, 0])
        dy = np.interp(dense, arc, waypoints[:, 1])
        w  = min(3, len(dense) - 4)           # 'valid' conv keeps len-w+1 >= 3 points
        ker = np.ones(w) / w
        sx = np.convolve(dx, ker, mode='valid')
        sy = np.convolve(dy, ker, mode='valid')
        pts = np.column_stack([sx, sy])       # no decimation -- keep every smoothed sample
        pts_s0 = scan_start + (w - 1) / 2.0 * dense_step
    if pts is None or len(pts) < 3:
        # Short scan window: no headroom to denoise — fall back to coarse sampling.
        sample_arcs = np.arange(scan_start, hi, step)
        if len(sample_arcs) < 3:
            return float(v_max_eff)
        sx  = np.interp(sample_arcs, arc, waypoints[:, 0])
        sy  = np.interp(sample_arcs, arc, waypoints[:, 1])
        pts = np.column_stack([sx, sy])
        pts_s0 = scan_start

    # Collect every triple's Menger curvature, then reduce below rather than
    # taking the raw max, which would let a single bad triple (a frame-to-frame
    # centreline-fit artifact, not a real corner) set the speed for the whole
    # window. kappa_at[j] records which pts index kappas[j] is centred on —
    # needed because a degenerate triple is skipped, so the index can't be
    # assumed from position alone.
    kappas = []
    kappa_at = []
    for i in range(1, len(pts) - 1):
        p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1]
        d12 = float(np.linalg.norm(p2 - p1))
        d23 = float(np.linalg.norm(p3 - p2))
        d31 = float(np.linalg.norm(p1 - p3))
        denom = d12 * d23 * d31
        if denom < 1e-9:
            continue
        v1    = p2 - p1
        v2    = p3 - p1
        cross = abs(float(v1[0] * v2[1] - v1[1] * v2[0]))
        kappas.append(2.0 * cross / denom)
        kappa_at.append(i)

    if not kappas:
        return float(v_max_eff)

    k = np.asarray(kappas, dtype=float)
    k_at = np.asarray(kappa_at, dtype=int)
    # A genuine corner spans several consecutive triples, so a short running
    # mean survives it while an isolated fit artifact gets averaged down.
    # Reduce with a max over the smoothed series rather than a percentile of
    # the raw one — the scan window only yields ~7 triples, so a p75/p90 is
    # both noisy and biased toward speeds faster than the raw max would give.
    # The 'valid' 3-point mean drops one entry at each end, so the surviving
    # centres are k_at[1:-1]; tracked alongside k rather than assumed fixed.
    if len(k) >= 3:
        k = np.convolve(k, np.ones(3) / 3.0, mode='valid')
        k_at = k_at[1:len(k) + 1]

    # ── Braking-distance propagation ──────────────────────────────────────
    # A single max over the window ignores WHERE the corner is: a hairpin
    # 24 m ahead and the same hairpin 2 m ahead would produce an identical
    # target, demanding a deceleration the car cannot physically produce as
    # it gets closer. Instead, for each sampled corner at distance d ahead
    # with its own corner-speed limit v_corner, the fastest we may travel now
    # and still brake to it is
    #     v_allowed = sqrt(v_corner^2 + 2 * a_brake * d)
    # (from v_f^2 = v_i^2 - 2*a*d). Take the most restrictive over the window;
    # a corner far enough away imposes no limit since v_allowed then exceeds
    # v_max_eff.
    #
    # Distances: each surviving entry k[j] is centred on pts[k_at[j]], whose
    # distance ahead of the car is pts_s0 (where pts[0] actually sits,
    # including the moving-average centre shift) plus the arc length along
    # pts to there.
    #
    # entry_margin: a curvature sample describes the middle of a bend, but the
    # car must already be at corner speed by the bend's entry, which is
    # earlier — braking to the sample's own distance would be too late. Sized
    # at one triple half-width (the arc a single curvature sample spans) so
    # it scales with the sampling density.
    k_safe = np.maximum(k, 1e-9)
    v_corner = safety * np.sqrt(a_lat_max / k_safe)
    if len(pts) > 1:
        pts_arc = np.concatenate(
            [[0.0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
        )
        entry_margin = float(np.median(np.diff(pts_arc))) if len(pts_arc) > 1 else 0.0
        d_ahead = (pts_s0
                   + pts_arc[np.clip(k_at, 0, len(pts_arc) - 1)]
                   - entry_margin)
        d_ahead = np.maximum(d_ahead, 0.0)
    else:
        d_ahead = np.full(len(k), pts_s0)

    v_allowed = np.sqrt(v_corner ** 2 + 2.0 * A_BRAKE_PLAN * d_ahead)
    v_target = float(np.min(v_allowed))

    # v_max_eff (the short-path-scaled ceiling) is not reapplied here — it
    # only applies to the early-return "not enough path to measure curvature"
    # cases above. v_max itself is still re-clamped: on a straight approach,
    # before a corner enters the scan window, kappa is measured near zero, so
    # v_target can be arbitrarily large otherwise.
    return float(np.clip(v_target, v_min, v_max))


def dynamic_speed_cap(waypoints, v_max=15.0, v_min=1.5,
                      a_lat_max=3.2, safety=0.9):
    """
    Real-time curvature-lookahead speed cap, meant to be layered UNDER a
    precomputed/oracle speed profile rather than replacing it.

    precomputed_speed_at() is a static, position-indexed lookup: it assumes
    the car is already travelling at the oracle profile's own planned speed,
    so it has no notion of "car is currently going faster than the profile
    allows and the corner is close enough that it can no longer brake down
    to the profile's target in time." That mismatch is exactly what shows up
    as late, hard braking and steering saturation at corner entry — see
    fsae_MPCTest/`docs/reference/README.md`'s speed-governor section.

    This is a thin wrapper over curvature_speed() using its own (separate,
    typically tighter) a_lat_max/safety defaults — the oracle profile was
    optimised for the whole lap and is trusted as the primary target, so
    this cap is only meant to catch the case where live tracking has drifted
    from that plan, not to re-litigate the racing line. Callers take
    min(oracle_v_target, dynamic_speed_cap(...)) — see
    controller.enable_dynamic_speed_cap.

    Parameters
    ----------
    waypoints : (n,2) array-like   Live path ahead, waypoints[0] = car position.
    v_max, v_min : float   Same meaning as curvature_speed().
    a_lat_max : float   Lateral-accel budget used only by THIS cap (m/s^2).
    safety : float      Safety margin used only by THIS cap.

    Returns
    -------
    float : speed cap (m/s), meant to be min()'d against another target.
    """
    return curvature_speed(waypoints, v_max=v_max, v_min=v_min,
                           a_lat_max=a_lat_max, safety=safety)


def _load_profile_csv(csv_path: str):
    """
    Shared reader for fsae_MPCTest's tuner/export_speed_profile.py /
    tuner/tools/raceline_optimizer.py CSVs. Accepts two header shapes:
      "x,y,psi,v_target"              (4 columns, speed_profile.csv and
                                        older raceline.csv exports)
      "x,y,psi,psi_target,v_target"   (5 columns, raceline_optimizer.py
                                        exports since the shaped
                                        heading-lead reference was added —
                                        see late_turn_in_investigation.md
                                        Part 8/9)
    Comment lines starting with '#' are skipped. Column count is detected
    per-file from the first data row, not the header text, so a caller
    doesn't need to know in advance which shape a given CSV has.

    Deliberately a plain reader with no scipy/centreline-reconstruction
    dependency — that runs once, offline, when the CSV is exported.

    Returns
    -------
    (path_X, path_Y, path_Psi, path_PsiTarget, path_V) : tuple of
        np.ndarray, shape (n,). path_PsiTarget equals path_Psi
        (the geometric tangent) for a 4-column file — i.e. an old/
        speed-profile CSV with no shaped-heading column behaves exactly
        as if psi_target had been exported equal to psi, a genuine no-op
        for every caller that doesn't ask for it explicitly.

    Raises
    ------
    FileNotFoundError, ValueError : bad csv_path or malformed contents.
    """
    xs, ys, psis, psi_targets, vs = [], [], [], [], []
    with open(csv_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('x,y'):
                continue
            fields = line.split(',')
            x_s, y_s, psi_s = fields[0], fields[1], fields[2]
            if len(fields) >= 5:
                psi_target_s, v_s = fields[3], fields[4]
            else:
                psi_target_s, v_s = psi_s, fields[3]
            xs.append(float(x_s))
            ys.append(float(y_s))
            psis.append(float(psi_s))
            psi_targets.append(float(psi_target_s))
            vs.append(float(v_s))
    if len(xs) < 2:
        raise ValueError(f"{csv_path}: fewer than 2 valid rows")
    return (np.asarray(xs), np.asarray(ys), np.asarray(psis),
            np.asarray(psi_targets), np.asarray(vs))


def load_speed_profile_csv(csv_path: str):
    """
    Load a pre-computed (x, y, v_target) speed profile exported by
    fsae_MPCTest's tuner/export_speed_profile.py.

    For a track that's already been mapped, this replaces curvature_speed()'s
    per-tick re-derivation with a lookup against an oracle profile computed
    once, offline, from the whole recorded map — the live-built centreline is
    frequently shorter than curvature_speed()'s own scan_end (perception FOV
    clips laterally on a corner before its forward window does), so this
    bypasses that shortfall for a track that's already known.

    Parameters
    ----------
    csv_path : str   Path to a CSV with header "x,y,psi,v_target" (comment
                      lines starting with '#' are skipped).

    Returns
    -------
    (path_X, path_Y, path_V) : tuple of np.ndarray, shape (n,)

    Raises
    ------
    FileNotFoundError, ValueError : bad csv_path or malformed contents.
    """
    path_X, path_Y, _path_Psi, _path_PsiTarget, path_V = _load_profile_csv(csv_path)
    return path_X, path_Y, path_V


def load_path_profile_csv(csv_path: str):
    """
    Load a pre-computed (x, y) path exported by fsae_MPCTest's
    tuner/export_speed_profile.py, for use as a drop-in replacement of the
    live planner's /fsae/planning/selected_trajectory centreline.

    For a track that's already been mapped, this removes the live planner
    (centerline_planner.py / boundary.py / cone_map.py) from the control loop
    entirely, isolating controller/plant tracking error from planner-induced
    path error.

    psi is exported but not returned here: MPCController._error_state()
    already derives path heading from consecutive waypoints (atan2 of the
    segment direction, the same convention centerline_planner.py's published
    PoseArray uses), so the (n,2) array below is a direct substitute for the
    live topic's path with no interface change to mpc_core.py.

    Parameters
    ----------
    csv_path : str   Path to a CSV with header "x,y,psi,v_target" (comment
                      lines starting with '#' are skipped).

    Returns
    -------
    path : np.ndarray, shape (n, 2)   [x, y] waypoints, global frame.

    Raises
    ------
    FileNotFoundError, ValueError : bad csv_path or malformed contents.
    """
    path_X, path_Y, _path_Psi, _path_PsiTarget, _path_V = _load_profile_csv(csv_path)
    return np.column_stack([path_X, path_Y])


def load_path_heading_profile_csv(csv_path: str):
    """
    Load the SHAPED heading-lead reference profile (psi_target) exported by
    fsae_MPCTest's tuner/tools/raceline_optimizer.py — see
    late_turn_in_investigation.md Part 8/9 for the mechanism and
    MPCController.set_heading_profile() for how it's consumed.

    Separate from load_path_profile_csv (which returns only (x,y), an
    (n,2) array used directly as `path` everywhere in mpc_core.py,
    including CornerMap's curvature segmentation) so that call site's
    return shape never changes — this is an additive, opt-in lookup, not a
    replacement for the geometric path array.

    Row-aligned with load_path_profile_csv's own (x,y) output when given
    the SAME csv_path (both read the same file, same row order) — the
    caller is responsible for loading both from one file, not mixing
    sources.

    For a 4-column CSV (no psi_target column), degrades to the plain
    geometric heading — see _load_profile_csv's docstring for why that's a
    genuine no-op, not repeated here.

    Parameters
    ----------
    csv_path : str

    Returns
    -------
    psi_target : np.ndarray, shape (n,)

    Raises
    ------
    FileNotFoundError, ValueError : bad csv_path or malformed contents.
    """
    _path_X, _path_Y, _path_Psi, path_PsiTarget, _path_V = _load_profile_csv(csv_path)
    return path_PsiTarget


def precomputed_speed_at(car_pos, path_X, path_Y, path_V) -> float:
    """
    Nearest-point lookup into a pre-computed speed profile (see
    load_speed_profile_csv()).

    Deliberately a plain nearest-point search, not a Frenet/arc-length
    projection: the profile is dense (see export script, default 1000 pts
    over a lap), so nearest-point error is small and this avoids needing the
    heading/tangent bookkeeping a proper Frenet projection would add for a
    speed lookup that only needs to be "close enough," unlike e_y/e_psi
    tracking error, which does need that precision.

    Parameters
    ----------
    car_pos : array-like, shape (2,)   Car's current [x, y] (global frame).
    path_X, path_Y, path_V : np.ndarray, shape (n,)   From load_speed_profile_csv().

    Returns
    -------
    float : v_target at the nearest profile point to car_pos.
    """
    d2 = (path_X - car_pos[0]) ** 2 + (path_Y - car_pos[1]) ** 2
    return float(path_V[int(np.argmin(d2))])

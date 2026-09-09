# Title: nmpc_core.py

"""
nmpc_core.py — NONLINEAR model-predictive path-tracking controller
(Frenet-frame / curvilinear coordinates, Gauss-Newton SQP, condensed dense QP
subproblem solved by OSQP).

This is a SECOND, independently selectable controller. It does not modify,
subclass or import behaviour from mpc_core.MPCController's solve path: that
LTV-QP controller remains the default and is completely untouched. Selection
happens at node construction time via NMPCParams.use_nmpc (default False) —
see mpc_controller.py.

WHY IT EXISTS: MPCController's prediction model has no term for the path
itself bending (`e_psi_dot = r`, missing `- kappa(s)*s_dot`), so with the car
dead on-line approaching a corner the QP predicts staying on-line forever and
no cost weighting can produce turn-in before real error exists — measured at
exactly 0.000 deg commanded across 8 synthetic states. Here `kappa(s)` is
looked up against arc length `s`, which is itself a STATE driven by the car's
predicted motion, not indexed by horizon step — so unlike three earlier
attempts to inject curvature as exogenous horizon data (all producing a
wrong-direction transient, see below), the obligation isn't schedulable.
Full derivation, the model equations, the cost construction, and the
real-time SQP structure (roll-forward feasibility, condensing, warm-start,
solve-time budget): `docs/reference/README.md`'s "Nonlinear MPC (use_nmpc)"
section and `late_turn_in_investigation.md` Part 16 (§16.1 gap, §16.3 model,
§16.5 correctness checks, §16.7 solve time/horizon-iteration sweep).

State/input vectors: x = [s, e_y, e_psi, v_x, v_y, r, delta_act, a_act],
u = [delta_cmd, a_cmd]. Every vehicle constant (lf, lr, m, Iz, Cf, Cr,
tau_delta, tau_a, MAX_STEER_RAD, MAX_ACCEL, MAX_BRAKE, du_max) is taken from
MPCController unchanged, including its kinematic/dynamic blend breakpoints —
no new physical constant is introduced. Error measurement (front-axle
projection, e_psi wrap, e_y_dot) is identical to `MPCController._error_state`
so an NMPC log means exactly what an LTV-QP log means. Cost weights come from
the SAME MPCParams the LTV-QP uses — see nmpc_params.py for the per-NMPC
override fields and the one weight whose meaning changes (q_r -> heading-error
rate, not absolute yaw rate).

WHAT THIS CONTROLLER DELIBERATELY DOES NOT DO
---------------------------------------------
* No adaptive gain schedule (mpc_core's corner-factor/heading-error-asymmetry
  stack) — that exists to synthesise anticipation a curvature-blind model
  can't produce; layering it on a curvature-aware model would double-count an
  effect that's now structural. Left untouched on the LTV-QP path. The one
  exception is steer_rate_anti_hunt (see EXPERIMENTAL ADDITIONS below) — it
  only ever makes steering-RATE more expensive when already
  centred/aligned/uncurving, the opposite direction from anticipation, so it
  is offered as a separate, independently-defaulted-False opt-in rather than
  assumed exempt from this section's reasoning.
* No shaped heading-lead profile. set_heading_profile() is accepted (so the
  nodes need no branch) and IGNORED with a one-time log line — that profile is
  a workaround for the same missing curvature term this controller closes
  structurally.
* No speed profile over the horizon BY DEFAULT. v_ref is the caller's
  single, already low-passed desired_speed held constant across the
  horizon, same as the LTV-QP gets — deliberately not addressing the
  (separate) braking-lag problem here, so a live A/B isolates the
  lateral-model change alone. NMPCParams.nmpc_horizon_speed_profile_enabled
  (default False, EXPERIMENTAL) can opt into a per-stage lookup instead —
  see PathReference.v_ref_at.

EXPERIMENTAL ADDITIONS (all additive, all default to preserve the above
exactly)
---------------------------------------------------------------------------
* PathReference.__init__ now fits an analytic CubicSpline to the raw
  waypoints by default (NMPCParams.nmpc_spline_reference_enabled, default
  True) instead of the old dense-resample + moving-average +
  finite-difference pipeline — see PathReference's own docstring. The old
  path is kept (not deleted) and selectable via the flag for A/B comparison.
* nmpc_horizon_speed_profile_enabled (default False): see PathReference.v_ref_at.
* nmpc_friction_circle_enabled (default False): an ADDITIONAL hard
  |F_yf|/|F_yr| <= F_max QP constraint on top of (not instead of) the
  existing soft alat-ceiling saturation below — see NH_FRICTION and
  _build_qp/_solve_step.
* nmpc_steer_rate_anti_hunt_enabled (MPCParams field, default False):
  reuses mpc_core._steer_rate_anti_hunt verbatim (imported, not
  reimplemented, so it is byte-identical by construction) to scale
  R_rate[0,0] up to nmpc_anti_hunt_boost_max (inherits anti_hunt_boost_max)
  when the CURRENT state is centred/aligned/uncurving. Computed once per
  compute() call from the measured state (not per SQP iteration, not a
  function of horizon step), so it is fresh every tick with no cross-tick
  memory — unlike a temporal low-pass filter on the output, this adds no
  lag. See "WHAT THIS CONTROLLER DELIBERATELY DOES NOT DO" above for why
  this is scoped separately from the rest of the gain-schedule family.
* nmpc_corner_rrate_blend_enabled (MPCParams field, default False): a
  narrower, ALTERNATIVE port of mpc_core's corner_factor family — blends
  R_rate[0,0] between nmpc_rrate_steer_straight/_corner by CURRENT curvature
  alone (mpc_core._corner_factor/_blend, imported verbatim). Unlike the rest
  of that family (Q[e_y]/Q[e_psi]/Q[r]/R[steer], deliberately excluded
  above), only R_rate[steer] is touched here, to limit how much of the
  "no adaptive gain schedule" reasoning this overrides. NOT composed with
  nmpc_steer_rate_anti_hunt_enabled — takes priority over it when both are
  set; the two are meant to be used one at a time.
"""

import math
import time
from dataclasses import dataclass

import numpy as np
import scipy.sparse as sp
from scipy.interpolate import CubicSpline

try:
    import osqp
except ImportError as _exc:      # pragma: no cover - see package.xml
    osqp = None
    _OSQP_IMPORT_ERROR = _exc

# PORT NOTE (fsae_autonomous): sourced from fsae_control.mpc.mpc_core (the
# LTV-QP module) on the sim side. This repo does not carry mpc_core.py (it
# needs cvxpy/clarabel, which this repo does not depend on), so these 7
# symbols are lifted into control_limits.py instead -- see that file's
# docstring. Keep control_limits.py byte-identical to mpc_core.py's copies.
from fsae_control.mpc.control_limits import (
    MAX_ACCEL, MAX_BRAKE, MAX_STEER_RAD, _steer_rate_anti_hunt,
    _corner_factor, _blend, _reversal_penalty_boost,
)
from fsae_control.mpc.mpc_params import DEFAULT_MPC_PARAMS, MPCParams
from fsae_control.mpc.nmpc_params import DEFAULT_NMPC_PARAMS, NMPCParams

# ── State/input/output layout ────────────────────────────────────────────
IDX_S     = 0   # arc length along the reference path (m)
IDX_EY    = 1   # lateral deviation, + = front axle LEFT of the path (m)
IDX_EPSI  = 2   # heading error, car_yaw - path_yaw, wrapped (rad)
IDX_VX    = 3   # body-frame forward speed (m/s)
IDX_VY    = 4   # body-frame lateral speed (m/s)
IDX_R     = 5   # yaw rate (rad/s)
IDX_DELTA = 6   # actuator-lagged steering angle (rad)
IDX_A     = 7   # actuator-lagged acceleration (m/s^2)
NX = 8
NU = 2
NH = 5          # h() rows: e_y, e_y_dot, e_psi, e_psi_dot, e_v
# Extra _outputs()/_output_jacobians() rows appended ONLY when
# NMPCController.friction_circle_enabled (NMPCParams.nmpc_friction_circle_enabled)
# is True: F_yf, F_yr (front/rear axle lateral tyre force, N). Rides along
# through the SAME finite-difference Jacobian pass that produces C for the
# cost rows above, at zero extra rollout cost -- see _outputs()'s docstring.
# NEVER weighted into the cost (w_out has NH=5 entries, not NH+NH_FRICTION);
# used only to build the friction-circle QP constraint rows in _solve_step.
NH_FRICTION = 2

# Finite-difference perturbations, one per state then per input. Sized per
# variable so every column of the Jacobian has a comparable truncation/roundoff
# balance: eps_j ~ 1e-6 * (typical magnitude of that variable). Verified
# against central differences in Part 16 §16.5.
_FD_EPS_X = np.array([1e-6, 1e-6, 1e-7, 1e-6, 1e-6, 1e-7, 1e-7, 1e-6])
_FD_EPS_U = np.array([1e-7, 1e-6])

# Guard on the Frenet denominator (1 - kappa*e_y). It is singular at
# e_y = 1/kappa; on this car that is 4.8 m at the tightest logged corner
# (kappa 0.21) against a 3.5 m track half-width, so this floor is inert in
# normal operation and only prevents a sign flip if the car is somehow far
# off-track on a very tight bend. Not a tunable.
_DENOM_FLOOR = 0.25


def _wrap(a):
    """Wrap an angle (or array of angles) to [-pi, pi]."""
    return np.arctan2(np.sin(a), np.cos(a))


class PathReference:
    """
    Arc-length parameterisation of a waypoint path, plus the curvature
    profile kappa(s) the NMPC's prediction needs.

    Built once per DISTINCT path: for a precomputed/static path that is once
    per run (see NMPCController.set_static_path / the per-tick signature cache
    in compute()); in live-planner mode the path changes every tick and this is
    rebuilt each time (measured cost in Part 16 §16.7).

    kappa(s)/psi_ref(s) construction (NMPCParams.nmpc_spline_reference_enabled,
    default True): x(s) and y(s) are each fit as an independent
    `scipy.interpolate.CubicSpline` over the raw (not resampled) arc-length
    knots, and kappa/psi_ref are the spline's own analytic first/second
    derivatives (psi_ref = atan2(y', x'), kappa = (x'y'' - y'x'')/(x'^2+y'^2)^1.5),
    evaluated on a dense `dense_step` grid. This replaces the previous
    dense-resample + moving-average + finite-difference pipeline — the SAME
    denoise precedent control_utils.curvature_speed() uses (dense_step 0.5 m,
    w 3) — which is still present and used verbatim when the flag is False,
    kept for A/B comparison against the known "centreline curvature spikes"
    defect this addresses (see CLAUDE.md). Either way this matters more here
    than for a speed cap, because kappa enters the PREDICTION and would be
    steered for.
    """

    def __init__(self, path, dense_step=0.5, smooth_w=3, kappa_clip=0.5,
                 spline_reference_enabled=True, path_v_xy=None, path_v=None):
        path = np.asarray(path, dtype=float)
        self.path = path
        seg = np.diff(path, axis=0)
        seg_len = np.hypot(seg[:, 0], seg[:, 1])
        self.arc = np.concatenate([[0.0], np.cumsum(seg_len)])
        self.total = float(self.arc[-1]) if len(self.arc) else 0.0

        s_k = np.array([0.0, max(self.total, 1e-3)])
        kappa = np.zeros(2)
        psi_ref = None
        if self.total > 4.0 * max(dense_step, 1e-6):
            if spline_reference_enabled:
                s_k, kappa, psi_ref = self._spline_kappa_psi(
                    path, self.arc, dense_step, kappa_clip)
            else:
                # Dense resample + smooth + heading difference -> kappa(s).
                dense = np.arange(0.0, self.total, dense_step)
                dx = np.interp(dense, self.arc, path[:, 0])
                dy = np.interp(dense, self.arc, path[:, 1])
                w = int(max(1, min(smooth_w, max(1, len(dense) - 4))))
                if w > 1:
                    ker = np.ones(w) / w
                    sx = np.convolve(dx, ker, mode='valid')
                    sy = np.convolve(dy, ker, mode='valid')
                    s0 = (w - 1) / 2.0 * dense_step
                else:
                    sx, sy, s0 = dx, dy, 0.0
                if len(sx) >= 3:
                    d_x = np.diff(sx)
                    d_y = np.diff(sy)
                    ds = np.hypot(d_x, d_y)
                    psi = np.arctan2(d_y, d_x)
                    dpsi = _wrap(np.diff(psi))
                    ds_mid = 0.5 * (ds[:-1] + ds[1:])
                    good = ds_mid > 1e-6
                    k = np.zeros_like(ds_mid)
                    k[good] = dpsi[good] / ds_mid[good]
                    # kappa[i] is centred on the smoothed sample i+1.
                    s_k = s0 + dense_step * (np.arange(len(k)) + 1.0)
                    kappa = np.clip(k, -kappa_clip, kappa_clip)
                    # Reference HEADING on the same grid and from the same
                    # smoothed samples the curvature came from, unwrapped so
                    # interpolation across the +-pi seam is well defined.
                    #
                    # This matters as much as the curvature itself: the reference
                    # heading and the reference curvature must describe ONE
                    # reference, or the measured e_psi and the model's own
                    # e_psi_dot = r - kappa*s_dot disagree. Measuring e_psi off the
                    # RAW segment tangent (as the LTV-QP does) quantises it in
                    # steps of ds/R — 5.7 deg per 0.5 m waypoint on a 5 m-radius
                    # hairpin — and the NMPC reads each of those steps as a real
                    # state error to be corrected within a tick or two. Offline
                    # that produced a hard period-2 steering limit cycle
                    # (+25 deg / -25 deg alternating) through the tight corners on
                    # comp_test_map_3; see late_turn_in_investigation.md Part 16
                    # §16.6. The LTV-QP does not show it because its own
                    # anti-hunt/R_rate machinery damps exactly this, and because it
                    # never predicts heading forward at all.
                    psi_mid = np.unwrap(psi)
                    psi_ref = 0.5 * (psi_mid[:-1] + psi_mid[1:])

        self.s_kappa = s_k
        self.kappa = kappa
        # Scalar-lookup fast path for the sequential rollout (see
        # kappa_scalar): s_kappa is a uniform grid by construction, so the
        # index is arithmetic and a Python list beats numpy indexing at this
        # size. _k_uniform is False only for the degenerate short-path
        # fallback above (all-zero curvature), where kappa_scalar falls back
        # to np.interp.
        self._k_list = [float(v) for v in np.atleast_1d(kappa)]
        self._k_n = len(self._k_list)
        self._k_s0 = float(s_k[0])
        self._k_ds = float(dense_step)
        self._k_uniform = self._k_n >= 3

        # Reference heading psi_ref(s) on the SAME grid as kappa (see above).
        # When the path was too short to smooth, fall back to the raw
        # per-waypoint tangent so this is always populated.
        if psi_ref is None:
            d = np.diff(path, axis=0)
            raw = np.unwrap(np.arctan2(d[:, 1], d[:, 0]))
            self.s_psi = 0.5 * (self.arc[:-1] + self.arc[1:])
            self.psi_ref = raw
        else:
            self.s_psi = s_k
            self.psi_ref = psi_ref

        # Speed-profile lookup (NMPCParams.nmpc_horizon_speed_profile_enabled).
        # None (default) means "not available" -- v_ref_at falls back to the
        # caller's scalar. Built from the speed profile's OWN (path_v_xy)
        # points, NOT self.arc: the speed-profile array is a separate object
        # from the path array handed to this constructor (confirmed at the
        # mpc_controller.py call site -- self._static_path and
        # self._speed_profile are loaded from two different CSVs), so its own
        # cumulative arc length must be computed independently.
        self.s_v = None
        self.v_target = None
        if path_v_xy is not None and path_v is not None:
            pv_xy = np.asarray(path_v_xy, dtype=float)
            pv = np.asarray(path_v, dtype=float)
            if len(pv_xy) >= 2 and len(pv) == len(pv_xy):
                seg_v = np.diff(pv_xy, axis=0)
                seg_v_len = np.hypot(seg_v[:, 0], seg_v[:, 1])
                self.s_v = np.concatenate([[0.0], np.cumsum(seg_v_len)])
                self.v_target = pv

        # Signature used to decide whether a cached PathReference still
        # describes the array compute() was handed this tick. Cheap (no
        # full-array compare) and sufficient: the planner republishes a new
        # array object with different endpoints/length when the path changes.
        self.signature = (
            len(path),
            float(path[0, 0]), float(path[0, 1]),
            float(path[-1, 0]), float(path[-1, 1]),
            round(self.total, 6),
        )

    @staticmethod
    def _spline_kappa_psi(path, arc, dense_step, kappa_clip):
        """
        Analytic kappa(s)/psi_ref(s) from independent CubicSpline fits of
        x(s), y(s) over the RAW arc-length knots `arc` (not a dense-
        resampled grid — the spline itself is the smoothing step, so no
        separate resample/moving-average is needed). Not-a-knot boundary
        conditions (scipy's default): these are open racing lines, not
        closed loops (self.total/self.arc are treated as a plain open
        interval everywhere else in this class), so no periodic wraparound
        is added.
        """
        cs_x = CubicSpline(arc, path[:, 0])
        cs_y = CubicSpline(arc, path[:, 1])
        dx1, dy1 = cs_x.derivative(1), cs_y.derivative(1)
        dx2, dy2 = cs_x.derivative(2), cs_y.derivative(2)

        s_k = np.arange(0.0, arc[-1], dense_step)
        if len(s_k) < 3 or s_k[-1] < arc[-1]:
            s_k = np.append(s_k, arc[-1])

        xp, yp = dx1(s_k), dy1(s_k)
        xpp, ypp = dx2(s_k), dy2(s_k)
        denom = np.maximum(xp ** 2 + yp ** 2, 1e-9) ** 1.5
        kappa = (xp * ypp - yp * xpp) / denom
        kappa = np.clip(kappa, -kappa_clip, kappa_clip)
        psi_ref = np.unwrap(np.arctan2(yp, xp))
        return s_k, kappa, psi_ref

    def kappa_at(self, s):
        """
        Signed curvature (1/m) at arc length(s) `s`, clamped to the path's own
        extent at both ends (np.interp's default edge behaviour) rather than
        returning 0 past the end: holding the last known curvature is the
        conservative choice for a horizon that runs off the end of a partial
        planner path, where dropping to 0 would predict the corner simply
        stopping.
        """
        return np.interp(s, self.s_kappa, self.kappa)

    def v_ref_at(self, s):
        """
        Speed target v(s) from the precomputed per-lap speed profile, at
        arc length(s) `s` (end-clamped, same convention as kappa_at). Only
        meaningful when this PathReference was built with a speed-profile
        array (see __init__'s path_v_xy/path_v) -- callers must check
        `self.v_target is not None` before relying on this rather than the
        scalar v_ref, exactly like nmpc_horizon_speed_profile_enabled's own
        gating in NMPCController.
        """
        return np.interp(s, self.s_v, self.v_target)

    def kappa_scalar(self, s):
        """
        Single-point kappa(s), O(1) on the uniform curvature grid. Same values
        (and same end-clamping) as kappa_at, without np.interp's per-call
        overhead — this is called ~1100 times per rollout, so that overhead is
        the difference between a 1 ms and a 5 ms rollout.
        """
        if not self._k_uniform:
            return float(np.interp(s, self.s_kappa, self.kappa))
        t = (s - self._k_s0) / self._k_ds
        if t <= 0.0:
            return self._k_list[0]
        i = int(t)
        if i >= self._k_n - 1:
            return self._k_list[-1]
        k0 = self._k_list[i]
        return k0 + (t - i) * (self._k_list[i + 1] - k0)

    def psi_ref_at(self, s):
        """
        Reference heading (rad, unwrapped and hence continuous) at arc
        length(s) `s`, from the same smoothed samples kappa comes from. Used
        for BOTH the e_y projection direction and e_psi, so the measured
        Frenet state and the predicted one describe one identical reference.
        """
        return np.interp(s, self.s_psi, self.psi_ref)

    def project(self, front_axle, car_yaw):
        """
        Frenet projection of a front-axle position onto the path.

        Returns (s0, e_y, e_psi, base_idx, path_yaw). Deliberately identical
        arithmetic to MPCController._error_state (nearest waypoint, segment
        tangent, perpendicular projection, wrapped heading error) so e_y/e_psi
        are directly comparable between the two controllers' logs.
        """
        path = self.path
        base_idx = int(np.argmin(np.linalg.norm(path - front_axle, axis=1)))
        s_base = float(self.arc[base_idx])
        # Reference direction from the SMOOTHED profile, not the raw segment
        # tangent — see psi_ref_at / the psi_ref construction comment.
        path_yaw = float(self.psi_ref_at(s_base))
        dx = front_axle[0] - path[base_idx][0]
        dy = front_axle[1] - path[base_idx][1]
        cos_y, sin_y = math.cos(path_yaw), math.sin(path_yaw)
        e_y = dy * cos_y - dx * sin_y
        along = dx * cos_y + dy * sin_y
        s0 = s_base + along
        # Re-evaluate the heading at the refined station: on a tight corner the
        # along-track correction can be a metre or more, over which the
        # reference heading genuinely changes.
        path_yaw = float(self.psi_ref_at(s0))
        e_psi = float(_wrap(car_yaw - path_yaw))
        return s0, float(e_y), e_psi, base_idx, path_yaw

    def xy_at(self, s, e_y=0.0):
        """
        Inverse of project(): Frenet (s, e_y) -> Cartesian (x, y) in
        self.path's own frame. Exactly inverts project()'s
        e_y = dy*cos(psi) - dx*sin(psi) arithmetic (same raw self.arc/
        self.path anchors, not a freshly-fit spline), so a round trip
        (xy_at(*project(pt, yaw)[:2])) recovers pt. Vectorised over
        array-like s/e_y like kappa_at, so a whole horizon converts in one
        call.
        """
        x0 = np.interp(s, self.arc, self.path[:, 0])
        y0 = np.interp(s, self.arc, self.path[:, 1])
        psi = self.psi_ref_at(s)
        x = x0 - e_y * np.sin(psi)
        y = y0 + e_y * np.cos(psi)
        return x, y


@dataclass
class _Plant:
    """
    Vehicle constants for the prediction model.

    Every value defaults to MPCController.__init__'s own hardcoded value, kept
    here so this module is self-contained but MUST be kept in sync with that
    constructor (and, per CLAUDE.md, with vehicle_physics.VehicleParams) if the
    plant is ever re-identified. These are NOT independent tunables.
    """
    lf: float = 0.70
    lr: float = 0.85
    m: float = 255.0
    Iz: float = 150.0
    Cf: float = 29155.47766921484
    Cr: float = 19512.3421655211
    tau_delta: float = 0.08
    tau_a: float = 0.02
    # Kinematic->dynamic blend breakpoints, identical to _discrete_model's
    # alpha = clip((v_x - 1.0)/(2.5 - 1.0), 0, 1).
    v_blend_lo: float = 1.0
    v_blend_hi: float = 2.5
    # FSDS's measured sustained lateral-acceleration ceiling law, from
    # MPCParams.alat_ceiling_flat/_slope/_intercept (the SAME law
    # mpc_core._alat_ceiling_at and model/vehicle_physics.alat_ceiling_at
    # already use — measured by open-loop system-ID, see CLAUDE.md's
    # "MECHANISM: a dynamically-enforced lateral-acceleration ceiling").
    # NMPCController.__init__ overwrites these from its MPCParams instance.
    #
    # Why the PREDICTION needs it: linear tyres produce unbounded lateral
    # force, so without this the model believes it can hold any corner at any
    # speed. The plant cannot (FSDS clamps sustained a_lat at ~7.5-9 m/s^2),
    # so the NMPC would command a yaw rate that never arrives, see the error
    # persist, and command more — which offline showed up as a large-amplitude
    # steering oscillation through the tight corners, and eventually a spin
    # (late_turn_in_investigation.md Part 16 §16.6). The LTV-QP has the same
    # optimistic tyre model but is shielded from it by heavy steering-effort /
    # steering-rate damping and by never predicting the corner at all.
    alat_ceiling_enabled: bool = True
    alat_ceiling_flat: float = 7.5
    alat_ceiling_slope: float = 0.47
    alat_ceiling_intercept: float = 2.46


def _tyre_forces(X, p):
    """
    Front/rear axle lateral tyre force (N), vectorised over stages, AFTER
    the existing soft alat-ceiling tanh saturation (if p.alat_ceiling_enabled)
    -- i.e. the SAME F_yf/F_yr that actually enter _f's dynamics, not the
    raw linear-tyre value. A function of STATE only (v_y, r, delta are all
    states; steering/accel COMMAND only affects delta's rate, not the
    instantaneous force at this stage), which is what lets these ride along
    as extra _outputs() rows with no extra rollout cost -- see NH_FRICTION's
    comment. Kept a line-by-line mirror of _f's own force computation; if
    that changes, update this too.
    """
    v_x = X[:, IDX_VX]
    v_y = X[:, IDX_VY]
    r   = X[:, IDX_R]
    d   = X[:, IDX_DELTA]

    v_safe = np.maximum(np.abs(v_x), p.v_blend_hi)
    alpha_f = np.arctan((v_y + p.lf * r) / v_safe) - d
    alpha_r = np.arctan((v_y - p.lr * r) / v_safe)
    F_yf = -2.0 * p.Cf * alpha_f
    F_yr = -2.0 * p.Cr * alpha_r

    if p.alat_ceiling_enabled:
        cos_d = np.cos(d)
        a_y = (F_yf * cos_d + F_yr) / p.m
        ceil = np.maximum(p.alat_ceiling_flat,
                          p.alat_ceiling_slope * np.abs(v_x) + p.alat_ceiling_intercept)
        ratio = np.abs(a_y) / ceil
        sat = np.where(ratio > 1e-6, np.tanh(ratio) / np.maximum(ratio, 1e-6), 1.0)
        F_yf = F_yf * sat
        F_yr = F_yr * sat
    return F_yf, F_yr


def _f(X, U, ref, p):
    """
    Continuous-time dynamics, vectorised over horizon stages.

    X: (M, NX), U: (M, NU) -> (M, NX) state derivatives. `ref` supplies
    kappa(s); `p` is a _Plant. See the module docstring for the equations.
    """
    s     = X[:, IDX_S]
    e_y   = X[:, IDX_EY]
    e_psi = X[:, IDX_EPSI]
    v_x   = X[:, IDX_VX]
    v_y   = X[:, IDX_VY]
    r     = X[:, IDX_R]
    d     = X[:, IDX_DELTA]
    a     = X[:, IDX_A]

    kap = ref.kappa_at(s)

    denom = 1.0 - kap * e_y
    # Keep the denominator away from zero WITHOUT flipping its sign (see
    # _DENOM_FLOOR): a sign flip would reverse the predicted direction of
    # travel along the path.
    denom = np.where(denom >= 0.0,
                     np.maximum(denom, _DENOM_FLOOR),
                     np.minimum(denom, -_DENOM_FLOOR))

    cos_ep = np.cos(e_psi)
    sin_ep = np.sin(e_psi)
    s_dot   = (v_x * cos_ep - v_y * sin_ep) / denom
    e_y_dot = v_x * sin_ep + v_y * cos_ep
    e_psi_dot = r - kap * s_dot

    # Tyre slip angles: floor the denominator at the top of the
    # kinematic/dynamic blend band so the linear-tyre expressions stay finite
    # as v_x -> 0 (the blend below is what actually handles low speed).
    v_safe = np.maximum(np.abs(v_x), p.v_blend_hi)
    alpha_f = np.arctan((v_y + p.lf * r) / v_safe) - d
    alpha_r = np.arctan((v_y - p.lr * r) / v_safe)
    F_yf = -2.0 * p.Cf * alpha_f
    F_yr = -2.0 * p.Cr * alpha_r
    cos_d = np.cos(d)

    if p.alat_ceiling_enabled:
        # Smooth saturation of the lateral forces so the predicted lateral
        # acceleration cannot exceed the measured FSDS ceiling at this speed.
        # tanh(x)/x is 1 to second order at x=0, so small-signal handling (and
        # therefore the linear-region cornering stiffness the weights were
        # tuned against) is unchanged; only the demanded-beyond-possible region
        # is bent over. Both axle forces are scaled by the same factor, which
        # preserves the yaw-moment balance and hence the model's understeer
        # character while limiting its magnitude.
        a_y = (F_yf * cos_d + F_yr) / p.m
        ceil = np.maximum(p.alat_ceiling_flat,
                          p.alat_ceiling_slope * np.abs(v_x) + p.alat_ceiling_intercept)
        ratio = np.abs(a_y) / ceil
        sat = np.where(ratio > 1e-6, np.tanh(ratio) / np.maximum(ratio, 1e-6), 1.0)
        F_yf = F_yf * sat
        F_yr = F_yr * sat

    blend = np.clip((v_x - p.v_blend_lo) / (p.v_blend_hi - p.v_blend_lo), 0.0, 1.0)

    # Fade tyre forces out at low speed, same `blend` the kinematic/dynamic
    # mix already uses. WITHOUT this, alpha_f/alpha_r's speed-floored
    # denominator (v_safe, needed to avoid a divide-by-zero as v_x -> 0) makes
    # a stationary tyre's slip angle track the STEERING COMMAND directly
    # (alpha_f ~= -d when v_y, r are small), so the model predicts a large
    # cornering force from steering alone at v_x = 0 -- backwards from a real
    # tyre, which generates ~zero force with no rolling contact velocity.
    # Uncommanded, this manufactured force propagates through v_y_dot_dyn/
    # r_dot_dyn into a large, entirely fictitious predicted e_y/e_psi
    # excursion over the horizon while the car has not physically moved,
    # which is what caused the NMPC's steering command to snap to the full
    # +-25 deg mechanical lock in the first ~0.5-0.7s of every run from a
    # standing start (measured 2026-08-13: nmpc_pred_ey_end reached -1.9 m
    # while v_actual was still ~0). The dynamic branch's own OUTPUT
    # (v_y_dot_dyn/r_dot_dyn) is already blended out by `blend` below, but
    # that happens too late to stop the force itself from existing --
    # F_yf/F_yr must be scaled here, at the source, not just downstream.
    F_yf = F_yf * blend
    F_yr = F_yr * blend

    v_x_dot = a + blend * r * v_y

    v_y_dot_dyn = (F_yf * cos_d + F_yr) / p.m - r * v_x
    r_dot_dyn   = (p.lf * F_yf * cos_d - p.lr * F_yr) / p.Iz

    # Kinematic branch, differentiated: r_kin = v_x*tan(d)/L, v_y_kin = lr*r_kin,
    # with d_dot from the steering actuator lag and v_x_dot = a (the r*v_y term
    # is itself blended out at low speed).
    L = p.lf + p.lr
    d_dot = (U[:, 0] - d) / p.tau_delta
    tan_d = np.tan(d)
    sec2_d = 1.0 / np.maximum(cos_d * cos_d, 1e-3)
    r_dot_kin = (a * tan_d + v_x * sec2_d * d_dot) / L
    v_y_dot_kin = p.lr * r_dot_kin

    v_y_dot = (1.0 - blend) * v_y_dot_kin + blend * v_y_dot_dyn
    r_dot   = (1.0 - blend) * r_dot_kin   + blend * r_dot_dyn

    out = np.empty_like(X)
    out[:, IDX_S]     = s_dot
    out[:, IDX_EY]    = e_y_dot
    out[:, IDX_EPSI]  = e_psi_dot
    out[:, IDX_VX]    = v_x_dot
    out[:, IDX_VY]    = v_y_dot
    out[:, IDX_R]     = r_dot
    out[:, IDX_DELTA] = d_dot
    out[:, IDX_A]     = (U[:, 1] - a) / p.tau_a
    return out


def _f_scalar(x, u, kap, p):
    """
    Scalar (single-state) form of _f, returning a tuple of 8 derivatives.

    EXISTS ONLY FOR SPEED, and is a line-by-line mirror of _f above — keep the
    two identical. The horizon rollout is inherently sequential (35 steps x 4
    RK stages x n_sub substeps), and at that size numpy's per-call overhead
    dominates completely: the vectorised _f costs ~75 us on a 1x8 array, making
    one rollout 17 ms, versus ~1 ms for this form. The Jacobian pass, which
    batches all stages into one array, still uses the vectorised _f.

    `kap` is passed in (already looked up) rather than read from `ref` so the
    caller can use PathReference.kappa_scalar's O(1) uniform-grid lookup
    instead of np.interp's ~4 us call overhead.

    test_nmpc_core.py::test_scalar_matches_vectorised asserts the two forms
    agree to 1e-12 on randomised states — a divergence between them is a
    silent-wrong-prediction bug, so that test is not optional.
    """
    s, e_y, e_psi, v_x, v_y, r, d, a = x

    denom = 1.0 - kap * e_y
    if denom >= 0.0:
        denom = denom if denom > _DENOM_FLOOR else _DENOM_FLOOR
    else:
        denom = denom if denom < -_DENOM_FLOOR else -_DENOM_FLOOR

    cos_ep = math.cos(e_psi)
    sin_ep = math.sin(e_psi)
    s_dot = (v_x * cos_ep - v_y * sin_ep) / denom
    e_y_dot = v_x * sin_ep + v_y * cos_ep
    e_psi_dot = r - kap * s_dot

    v_safe = abs(v_x)
    if v_safe < p.v_blend_hi:
        v_safe = p.v_blend_hi
    alpha_f = math.atan((v_y + p.lf * r) / v_safe) - d
    alpha_r = math.atan((v_y - p.lr * r) / v_safe)
    F_yf = -2.0 * p.Cf * alpha_f
    F_yr = -2.0 * p.Cr * alpha_r
    cos_d = math.cos(d)

    if p.alat_ceiling_enabled:
        # Mirror of _f's lateral-acceleration ceiling saturation.
        a_y = (F_yf * cos_d + F_yr) / p.m
        ceil = p.alat_ceiling_slope * abs(v_x) + p.alat_ceiling_intercept
        if ceil < p.alat_ceiling_flat:
            ceil = p.alat_ceiling_flat
        ratio = abs(a_y) / ceil
        if ratio > 1e-6:
            sat = math.tanh(ratio) / ratio
            F_yf *= sat
            F_yr *= sat

    blend = (v_x - p.v_blend_lo) / (p.v_blend_hi - p.v_blend_lo)
    blend = 0.0 if blend < 0.0 else (1.0 if blend > 1.0 else blend)

    # Mirror of _f's low-speed tyre-force fade -- see that copy's comment for
    # why this must scale F_yf/F_yr at the source, not just blend v_y_dot_dyn/
    # r_dot_dyn downstream.
    F_yf *= blend
    F_yr *= blend

    v_x_dot = a + blend * r * v_y
    v_y_dot_dyn = (F_yf * cos_d + F_yr) / p.m - r * v_x
    r_dot_dyn = (p.lf * F_yf * cos_d - p.lr * F_yr) / p.Iz

    L = p.lf + p.lr
    d_dot = (u[0] - d) / p.tau_delta
    sec2_d = cos_d * cos_d
    sec2_d = 1.0 / (sec2_d if sec2_d > 1e-3 else 1e-3)
    r_dot_kin = (a * math.tan(d) + v_x * sec2_d * d_dot) / L
    v_y_dot_kin = p.lr * r_dot_kin

    return (
        s_dot,
        e_y_dot,
        e_psi_dot,
        v_x_dot,
        (1.0 - blend) * v_y_dot_kin + blend * v_y_dot_dyn,
        (1.0 - blend) * r_dot_kin + blend * r_dot_dyn,
        d_dot,
        (u[1] - a) / p.tau_a,
    )


def _step_scalar(x, u, ref, p, dt, n_sub):
    """
    Scalar form of _step (one dt, RK4 with n_sub substeps, exact ZOH overwrite
    of the two actuator states, v_x floored at 0). Mirror of _step — see
    _f_scalar's docstring.
    """
    h = dt / n_sub
    xk = tuple(float(v) for v in x)
    d0, a0 = xk[IDX_DELTA], xk[IDX_A]
    for _ in range(n_sub):
        k1 = _f_scalar(xk, u, ref.kappa_scalar(xk[IDX_S]), p)
        x2 = tuple(xk[i] + 0.5 * h * k1[i] for i in range(NX))
        k2 = _f_scalar(x2, u, ref.kappa_scalar(x2[IDX_S]), p)
        x3 = tuple(xk[i] + 0.5 * h * k2[i] for i in range(NX))
        k3 = _f_scalar(x3, u, ref.kappa_scalar(x3[IDX_S]), p)
        x4 = tuple(xk[i] + h * k3[i] for i in range(NX))
        k4 = _f_scalar(x4, u, ref.kappa_scalar(x4[IDX_S]), p)
        xk = tuple(
            xk[i] + (h / 6.0) * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i])
            for i in range(NX)
        )
    out = list(xk)
    exp_d = math.exp(-dt / p.tau_delta)
    exp_a = math.exp(-dt / p.tau_a)
    out[IDX_DELTA] = d0 * exp_d + u[0] * (1.0 - exp_d)
    out[IDX_A] = a0 * exp_a + u[1] * (1.0 - exp_a)
    if out[IDX_VX] < 0.0:
        out[IDX_VX] = 0.0
    return out


def _step(X, U, ref, p, dt, n_sub):
    """
    One dt of the discretised model, vectorised over stages: RK4 with n_sub
    substeps, then the two actuator states overwritten with their EXACT
    zero-order-hold values.

    The overwrite matters: tau_a = 0.02 s against dt = 0.05 s puts lambda*dt at
    -2.5, close to RK4's real-axis stability edge, so RK4 alone leaves a_act
    visibly short of its true value at the end of a step. The lag states are
    linear, decoupled and driven by a constant input over the step, so their
    exact solution is available — and it is the same expression compute() uses
    to integrate the real actuator state.
    """
    h = dt / n_sub
    Xk = X
    for _ in range(n_sub):
        k1 = _f(Xk, U, ref, p)
        k2 = _f(Xk + (0.5 * h) * k1, U, ref, p)
        k3 = _f(Xk + (0.5 * h) * k2, U, ref, p)
        k4 = _f(Xk + h * k3, U, ref, p)
        Xk = Xk + (h / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
    Xk = Xk.copy()
    exp_d = math.exp(-dt / p.tau_delta)
    exp_a = math.exp(-dt / p.tau_a)
    Xk[:, IDX_DELTA] = X[:, IDX_DELTA] * exp_d + U[:, 0] * (1.0 - exp_d)
    Xk[:, IDX_A]     = X[:, IDX_A]     * exp_a + U[:, 1] * (1.0 - exp_a)
    # The car cannot be predicted into reverse; a negative v_x would also flip
    # the sign of every slip angle and make the prediction meaningless.
    np.maximum(Xk[:, IDX_VX], 0.0, out=Xk[:, IDX_VX])
    return Xk


def _outputs(X, ref, p, v_ref, horizon_speed_profile_enabled=False,
             friction_circle_enabled=False):
    """
    Stage output h(x) = [e_y, e_y_dot, e_psi, e_psi_dot, v_x - v_ref],
    vectorised over stages. e_psi_dot = r - kappa(s)*s_dot is the
    heading-error RATE — see nmpc_params.py on why q_r weights this rather
    than absolute yaw rate.

    v_ref is normally the caller's single scalar, broadcast to every stage
    (unchanged default behaviour). When `horizon_speed_profile_enabled` is
    True AND `ref` actually carries a speed-profile array (ref.v_target is
    not None -- NMPCParams.nmpc_horizon_speed_profile_enabled), the target is
    instead looked up per-stage at that stage's own PREDICTED arc length
    ref.v_ref_at(X[:, IDX_S]) -- a state-keyed lookup, exactly like
    kappa_at(s), NOT a value scheduled by horizon index. See
    PathReference.v_ref_at's docstring.

    When `friction_circle_enabled` is True, TWO EXTRA rows (F_yf, F_yr, see
    NH_FRICTION) are appended, returning shape (M, NH + NH_FRICTION) instead
    of (M, NH). These ride along through the exact same finite-difference
    Jacobian pass _output_jacobians already runs for the cost rows, but are
    NEVER part of the cost themselves (see NMPCController._solve_step's
    w_out slicing) -- only used to build the friction-circle QP constraint.
    Shape is IDENTICAL to before this feature existed when the flag is
    False (not just "the extra rows are empty").
    """
    e_y   = X[:, IDX_EY]
    e_psi = X[:, IDX_EPSI]
    v_x   = X[:, IDX_VX]
    v_y   = X[:, IDX_VY]
    r     = X[:, IDX_R]
    kap = ref.kappa_at(X[:, IDX_S])
    denom = 1.0 - kap * e_y
    denom = np.where(denom >= 0.0,
                     np.maximum(denom, _DENOM_FLOOR),
                     np.minimum(denom, -_DENOM_FLOOR))
    cos_ep = np.cos(e_psi)
    sin_ep = np.sin(e_psi)
    s_dot = (v_x * cos_ep - v_y * sin_ep) / denom
    if horizon_speed_profile_enabled and ref.v_target is not None:
        v_ref_stage = ref.v_ref_at(X[:, IDX_S])
    else:
        v_ref_stage = v_ref
    n_cols = NH + NH_FRICTION if friction_circle_enabled else NH
    H = np.empty((X.shape[0], n_cols))
    H[:, 0] = e_y
    H[:, 1] = v_x * sin_ep + v_y * cos_ep
    H[:, 2] = e_psi
    H[:, 3] = r - kap * s_dot
    H[:, 4] = v_x - v_ref_stage
    if friction_circle_enabled:
        F_yf, F_yr = _tyre_forces(X, p)
        H[:, NH] = F_yf
        H[:, NH + 1] = F_yr
    return H


def _rrate_zone_scale(kappa_now, kappa_ahead, k, boost_straight, ease_approach,
                      floor_corner):
    """
    Continuous three-zone multiplier on the steering-rate cost, driven by
    CURRENT curvature and the peak curvature the HORIZON predicts ahead:

        straight  (nothing now, nothing ahead)  -> boost_straight  (>= 1)
        approach  (nothing now, corner ahead)   -> ease_approach
        corner    (turning now)                 -> floor_corner    (<= 1)

    Both inputs go through the same saturating `_corner_factor` curve, so
    this is a smooth surface with no thresholds or hysteresis -- it degrades
    gracefully on a continuously-winding road (where `now` and `ahead` are
    both high, giving the corner value throughout) and on a lone kink
    (where `ahead` leads `now` by a tick or two, giving a brief approach
    ease).

    Blend order matters: the approach ease is applied FIRST against the
    straight boost, then the corner floor takes over as `now` rises. That
    ordering means a corner entered from a straight passes
    boost -> ease -> floor in that sequence, which is the intended
    "release the brake before you need to turn" behaviour.

    CAUTION on `k`: the ease/floor endpoints are only REACHED as
    `_corner_factor` approaches 1, so this schedule is only as strong as `k`
    lets it saturate over the TRACK's curvature range. At the LTV-QP's
    inherited k=8.0 a track whose tightest corner is |kappa|~0.2 tops
    `_corner_factor` out near 0.63, which silently degrades this from a
    three-zone schedule into a mild global rate boost -- the multiplier never
    leaves the boost band. Check a run's `m_Rrate_zone` column against
    `floor_corner` before concluding the endpoints did anything; if it never
    approaches the floor, raise `k` rather than lowering the endpoints
    (k ~= target/((1 - target) * kappa_max)).
    CAUTION on `kappa_ahead`: this is the peak |kappa| the horizon predicts,
    which leads current curvature by roughly the horizon length. Against a
    static raceline that is a clean signal. Against a LIVE planner path it
    inherits the open centreline curvature-spike defect, and unlike a speed
    target there is no rate limiter downstream to absorb a spurious spike --
    re-validate before trusting this with use_planner=True.
    """
    now = _corner_factor(abs(kappa_now), k)
    ahead = _corner_factor(abs(kappa_ahead), k)
    # Lead-only component: how much more corner is COMING than is here now.
    lead = max(0.0, ahead - now)
    s = boost_straight + (ease_approach - boost_straight) * lead
    return s + (floor_corner - s) * now


def _rrate_stage_ramp(N, near):
    """
    Per-stage multiplier on the steering-rate cost: `near` at horizon stage 0,
    rising linearly to 1.0 at the last stage. Returns shape (N,).

    WHY: the plain rate cost is uniform across the horizon
    (`np.tile(self.r_rate, N)`), so it charges the same price for a steering
    change whether that change is the FIRST move into a corner or the tenth
    tick of an oscillation. One weight cannot be both stiff enough to kill
    tick-to-tick hunting and compliant enough for a gentle corner's small
    early input, which is why a high flat weight makes the solver defer
    turn-in until it must catch up at the actuator slew limit.

    Ramping by STAGE is keyed on horizon POSITION, not measured state -- a
    measured-state schedule (curvature/error) was live-tested and failed
    because ~27% of jerk events show no curvature or heading-error signal at
    all one second beforehand, while the horizon already predicts the corner.

    CAUTION: offline-rejected as a fix for that jerk -- it moved
    slew-limited ticks the WRONG way (8.4% -> 12-15%) because a cheaper
    near-stage rate simply spends more of the slew budget every tick. It IS
    the only change found so far that clears the offline nmpc_offline_check
    DNF, which is why it is kept. See
    fsae_MPCTest/docs/steering_turn_in_upgrade_options.md (Option 1).

    `near` = 1.0 is an exact no-op, so the flag-off path is byte-identical.
    """
    if N <= 1:
        return np.ones(max(N, 1))
    return np.linspace(float(near), 1.0, N)


def _csc_pattern(mask):
    """
    Build a CSC matrix with an explicit, fixed sparsity pattern from a boolean
    mask, plus the (row, col) index arrays that write into its .data in CSC
    order.

    OSQP requires every update() to keep the pattern it was set up with, so the
    pattern is fixed once and only the data array is refilled per solve. Going
    through a mask (rather than converting a dense value array) is what
    guarantees a structural zero stays structurally present instead of being
    dropped by scipy.
    """
    m = sp.csc_matrix(mask.astype(np.float64))
    rows = m.indices.copy()
    cols = np.zeros_like(rows)
    for j in range(m.shape[1]):
        cols[m.indptr[j]:m.indptr[j + 1]] = j
    return m, rows, cols


class NMPCController:
    """
    Frenet-frame nonlinear MPC, drop-in compatible with
    mpc_core.MPCController's node-facing surface: compute(), reset(),
    set_static_path(), set_heading_profile(), last_telemetry, a_max,
    a_max_brake.
    """

    def __init__(
        self,
        dt: float = 0.05,
        N: int | None = None,
        params: MPCParams | None = None,
        nmpc: NMPCParams | None = None,
        logger=None,
    ) -> None:
        """
        dt must equal the calling node's control period (0.05 s), as for
        MPCController. N defaults to NMPCParams.nmpc_horizon (35, matching
        MPCController's own horizon so horizon length is never a confound when
        comparing the two); an explicit N overrides it. `logger` is an optional
        rclpy logger for the one-time informational messages; print() is used
        when it is None so this module stays importable/testable outside ROS.
        """
        if osqp is None:      # pragma: no cover - dependency guard
            raise ImportError(
                'nmpc_core requires osqp (already a documented dependency of '
                f'mpc_core via cvxpy — see package.xml): {_OSQP_IMPORT_ERROR!r}'
            )

        self.dt = float(dt)
        self.params = params if params is not None else DEFAULT_MPC_PARAMS
        self.nmpc = nmpc if nmpc is not None else DEFAULT_NMPC_PARAMS
        self._logger = logger
        self.N = int(self.nmpc.nmpc_horizon if N is None else N)
        if self.N < 2:
            raise ValueError(f'NMPC horizon must be >= 2 (got {self.N})')

        self.nx, self.nu = NX, NU
        nm0 = nmpc if nmpc is not None else DEFAULT_NMPC_PARAMS
        # alat_ceiling_flat/_slope/_intercept are FSDS's measured plant
        # constant (the sustained lateral-accel ceiling law), not a tuning
        # weight -- MPCParams no longer carries them (removed along with the
        # whole corner_demand/lookahead-gain-scheduling family they used to
        # parameterise), so _Plant's own hardcoded defaults (7.5/0.47/2.46,
        # the same measured values) are used directly here, the same
        # precedent this class already follows for lf/lr/m/Iz/Cf/Cr. Only
        # nmpc_alat_ceiling_enabled (a genuine NMPC-only on/off switch, not a
        # shared plant constant) still comes from NMPCParams.
        self.plant = _Plant(alat_ceiling_enabled=bool(nm0.nmpc_alat_ceiling_enabled))
        # Convenience aliases so telemetry/geometry code reads like mpc_core's.
        self.lf, self.lr = self.plant.lf, self.plant.lr

        # ── Experimental feature flags (see nmpc_params.py's comments) ───
        self.spline_reference_enabled = bool(nm0.nmpc_spline_reference_enabled)
        self.horizon_speed_profile_enabled = bool(nm0.nmpc_horizon_speed_profile_enabled)
        self.friction_circle_enabled = bool(nm0.nmpc_friction_circle_enabled)
        if self.friction_circle_enabled:
            # F_max = m * ceiling(v_x) / 2 per axle: the measured ceiling law
            # bounds TOTAL lateral force (F_yf*cos(d) + F_yr) / m, split
            # evenly across the two axles as a simple, symmetric per-axle
            # cap (the soft mechanism in _f/_f_scalar scales both axles by
            # the SAME factor too, so this keeps the same even-split
            # convention rather than inventing a front/rear bias). This is a
            # HARD, ADDITIONAL bound alongside (not instead of) that
            # existing soft tanh saturation.
            self._fmax_flat = 0.5 * self.plant.m * self.plant.alat_ceiling_flat
            self._fmax_slope = 0.5 * self.plant.m * self.plant.alat_ceiling_slope
            self._fmax_intercept = 0.5 * self.plant.m * self.plant.alat_ceiling_intercept
        self.speed_limit_enabled = bool(nm0.nmpc_speed_limit_enabled)
        self.speed_limit_margin = float(nm0.nmpc_speed_limit_margin)
        self.speed_limit_slack_weight = float(nm0.nmpc_speed_limit_slack_weight)

        # ── Limits: identical to MPCController's ────────────────────────
        self.a_max = MAX_ACCEL
        self.a_max_brake = MAX_BRAKE
        self.u_min = np.array([-MAX_STEER_RAD, -self.a_max_brake])
        self.u_max = np.array([MAX_STEER_RAD, self.a_max])
        # 180 deg/s * dt, matching MPCController's du_max exactly (see that
        # constructor's long note on why it is 180 and not 190).
        self.du_max = np.array([math.radians(180.0) * self.dt, 0.6])

        # ── Weights: MPCParams, with per-NMPC overrides ─────────────────
        # The override fields (nmpc_q_e_y, ...) live in MPCParams itself
        # (see mpc_params.py's "NMPC weight overrides" section), alongside the base
        # fields they inherit from when left at -1.0. NMPCParams (self.nmpc)
        # no longer carries any weight field at all — only structural/
        # solver settings.
        def _pick(override, inherited):
            return float(inherited if override is None or override < 0.0 else override)

        pm = self.params
        self.w_out = np.array([
            _pick(pm.nmpc_q_e_y,      pm.q_e_y),
            _pick(pm.nmpc_q_e_yd,     pm.q_e_yd),
            _pick(pm.nmpc_q_e_psi,    pm.q_e_psi),
            _pick(pm.nmpc_q_epsi_dot, pm.q_r),
            _pick(pm.nmpc_q_e_v,      pm.q_e_v),
        ])
        self.r_delta = _pick(pm.nmpc_r_delta, pm.r_delta)
        self.r_a_accel = _pick(pm.nmpc_r_a_accel, pm.r_a_accel)
        self.r_a_brake = _pick(pm.nmpc_r_a_brake, pm.r_a_brake)
        self.r_rate = np.array([
            _pick(pm.nmpc_r_rate_delta, pm.r_rate_delta),
            _pick(pm.nmpc_r_rate_a, pm.r_rate_a),
        ])
        self.terminal_scale = _pick(pm.nmpc_terminal_scale, pm.terminal_q_scale)

        # Independent of steer_rate_anti_hunt_enabled (the LTV-QP's own
        # flag) — see nmpc_params.py/mpc_params.py's field comments and the
        # module docstring's "WHAT THIS CONTROLLER DELIBERATELY DOES NOT DO"
        # for why this is opt-in and separately defaulted False.
        self.steer_rate_anti_hunt_enabled = bool(pm.nmpc_steer_rate_anti_hunt_enabled)
        self.anti_hunt_boost_max = _pick(pm.nmpc_anti_hunt_boost_max, pm.anti_hunt_boost_max)

        # Composes with EITHER of the two flags above (not an alternative to
        # either) -- see mpc_params.py's nmpc_reversal_penalty_enabled field
        # comment for why this one's signal (last tick's actual steering)
        # doesn't double-count with curvature/e_y/e_psi-keyed mechanisms.
        self.reversal_penalty_enabled = bool(pm.nmpc_reversal_penalty_enabled)
        self.reversal_penalty_boost_max = _pick(
            pm.nmpc_reversal_penalty_boost_max, pm.reversal_penalty_boost_max)
        self.reversal_penalty_k = _pick(pm.nmpc_reversal_penalty_k, pm.reversal_penalty_k)

        # EXPERIMENTAL, default off. Discounts the steering-rate cost at the
        # NEAR horizon stages -- see _rrate_stage_ramp's docstring, including
        # why it is NOT a fix for the shallow-corner jerk. Composes with the
        # flags above: they set the rate weight's MAGNITUDE, this shapes it
        # across STAGES.
        self.rrate_stage_ramp_enabled = bool(pm.nmpc_rrate_stage_ramp_enabled)
        self.rrate_stage_near = float(pm.nmpc_rrate_stage_near)

        # EXPERIMENTAL, default off. Continuous three-zone schedule on the
        # steering-rate cost: boost on a true straight, ease on the approach
        # to a corner the HORIZON can see, floor through the corner itself.
        # See _rrate_zone_scale. MULTIPLIES r_rate_delta (unlike the corner
        # blend, which overwrites it).
        self.rrate_zone_enabled = bool(pm.nmpc_rrate_zone_enabled)
        self.rrate_zone_boost_straight = float(pm.nmpc_rrate_zone_boost_straight)
        self.rrate_zone_ease_approach = float(pm.nmpc_rrate_zone_ease_approach)
        self.rrate_zone_floor_corner = float(pm.nmpc_rrate_zone_floor_corner)
        # Steering/accel JERK weights (second difference of the input). 0.0
        # (default) disables the term entirely -- see _build_qp's _E2 comment.
        self.rjerk_delta = float(pm.nmpc_rjerk_delta)
        self.rjerk_a = float(pm.nmpc_rjerk_a)

        # Alternative to the above, not a composition with it -- see
        # mpc_params.py's nmpc_corner_rrate_blend_enabled field comment.
        self.corner_rrate_blend_enabled = bool(pm.nmpc_corner_rrate_blend_enabled)
        self.corner_factor_k = _pick(pm.nmpc_corner_factor_k, pm.corner_factor_k)
        self.rrate_steer_straight = _pick(pm.nmpc_rrate_steer_straight, pm.rrate_steer_straight)
        self.rrate_steer_corner = _pick(pm.nmpc_rrate_steer_corner, pm.rrate_steer_corner)

        # ── Continuity memory (mirrors MPCController's) ─────────────────
        self._delta_act = 0.0
        self._a_act = 0.0
        self._u_prev = np.zeros(NU)
        self._u_prev2 = np.zeros(NU)  # command two ticks ago, for the jerk anchor
        self._v_des_filtered: float | None = None
        self._U = np.zeros((self.N, NU))     # warm-start input trajectory
        self._have_warm_start = False
        self._u_history: list[np.ndarray] = []
        self._pose_age_filtered: float | None = None
        self._n_delay = 0

        self._ref: PathReference | None = None
        self._ref_signature = None
        self._static_ref: PathReference | None = None
        self._heading_profile_warned = False

        self.last_telemetry: dict = {}
        # (N+1, 2) Cartesian predicted trajectory, only populated when
        # nmpc_publish_prediction_enabled is set (RViz visualisation) --
        # see compute()'s own gated assignment near its return.
        self.last_prediction_xy: np.ndarray | None = None
        self._qp = None
        self._build_qp()

    # ------------------------------------------------------------------
    # Node-facing hooks (same names/semantics as MPCController's)
    # ------------------------------------------------------------------
    def _log(self, msg: str) -> None:
        if self._logger is not None:      # pragma: no cover - ROS path
            self._logger.info(msg)
        else:
            print(f'[nmpc_core] {msg}')

    def set_static_path(self, path, path_v_xy=None, path_v=None) -> None:
        """
        Precompute the arc-length/curvature reference for a fixed path, once,
        at load time. Called by the owning node exactly where it calls
        MPCController.set_static_path(); compute() never builds this itself for
        a static path (it looks the cached one up by signature).

        path=None clears it (live-planner mode), in which case compute() builds
        a reference per tick from whatever path it is handed.

        `path_v_xy`/`path_v` (optional, NMPCParams.nmpc_horizon_speed_profile_enabled):
        the precomputed per-lap speed profile's own (x, y) points and target
        speeds — a SEPARATE array from `path` (the node's self._static_path
        and self._speed_profile are loaded from two different CSVs; see
        PathReference.v_ref_at's docstring) — passed straight through.
        """
        if path is None or len(np.asarray(path)) < 3:
            self._static_ref = None
            return
        try:
            self._static_ref = PathReference(
                path,
                dense_step=self.nmpc.nmpc_curvature_dense_step,
                smooth_w=self.nmpc.nmpc_curvature_smooth_w,
                kappa_clip=self.nmpc.nmpc_kappa_clip,
                spline_reference_enabled=self.spline_reference_enabled,
                path_v_xy=path_v_xy, path_v=path_v,
            )
            k = self._static_ref.kappa
            self._log(
                f'NMPC path reference built: {self._static_ref.total:.1f} m, '
                f'{len(k)} curvature samples, |kappa| max {np.abs(k).max():.4f} 1/m.'
            )
        except (ValueError, IndexError) as exc:   # pragma: no cover - defensive
            self._log(f'PathReference build failed ({exc}); will rebuild per tick.')
            self._static_ref = None

    def set_heading_profile(self, psi_target) -> None:
        """
        Accepted and IGNORED — see the module docstring. The shaped
        heading-lead profile (Part 8/9) is a workaround for the missing
        curvature term this controller models directly, so applying both would
        double-count the anticipation. Logged once so a launch config that
        enables use_precomputed_heading_profile alongside use_nmpc does not
        silently do nothing.
        """
        if psi_target is not None and not self._heading_profile_warned:
            self._heading_profile_warned = True
            self._log(
                'use_precomputed_heading_profile is IGNORED by the NMPC: its '
                'Frenet model already carries the path curvature the shaped '
                'heading lead exists to approximate.'
            )

    def reset(self) -> None:
        """Clear continuity state, as MPCController.reset() does."""
        self._delta_act = 0.0
        self._a_act = 0.0
        self._u_prev = np.zeros(NU)
        self._u_prev2 = np.zeros(NU)  # command two ticks ago, for the jerk anchor
        self._v_des_filtered = None
        self._U = np.zeros((self.N, NU))
        self._have_warm_start = False
        self._u_history.clear()
        self._pose_age_filtered = None
        self._n_delay = 0

    # ------------------------------------------------------------------
    # QP subproblem (condensed, dense, fixed sparsity)
    # ------------------------------------------------------------------
    def _build_qp(self) -> None:
        """
        Allocate the condensed QP once: variables
        z = [dU (nu*N); slack (N); slack_v (N)], with the constraint rows

            (1) box/trust region on dU                       nu*N rows
            (2) input slew rate |u_k - u_{k-1}| <= du_max     nu*N rows
            (3) e_y_k - slack_k <= +halfwidth                 N rows
            (4) e_y_k + slack_k >= -halfwidth                 N rows
            (5) slack >= 0                                    N rows
            (6) v_x_k - slack_v_k <= v_max_k                  N rows
            (7) slack_v >= 0                                  N rows

        Rows (3)-(5) and the slack variables are omitted entirely when
        nmpc_track_halfwidth <= 0. The pattern never changes after this, so
        each solve only rewrites P.data / A.data / q / l / u.

        Friction-circle rows (self.friction_circle_enabled, see
        NMPCParams.nmpc_friction_circle_enabled): one two-sided
        (-F_max <= ... <= F_max) row per axle per stage = 2 axles * N
        stages, dense in dU (same reasoning as the soft-track rows above —
        stage k's tyre force depends on every earlier input through S).
        Read ONCE here, at construction time, like _use_slack — NOT
        per-tick — since it changes the QP's fixed sparsity pattern. When
        False, n_rows/nz and every array below are IDENTICAL to before this
        feature existed.

        Speed-limit rows (6)-(7) (self.speed_limit_enabled, see
        NMPCParams.nmpc_speed_limit_enabled): a SEPARATE one-sided soft bound
        with its OWN slack_v (not sharing the track bound's slack, so the two
        constraints can't offset each other's cost), one row per stage plus
        one non-negativity row per stage. v_max_k is filled in per-tick from
        PathReference.v_ref_at(s_k) + nmpc_speed_limit_margin in _solve_step;
        when no speed-profile array is available at solve time the rows are
        left inert (l=-inf, u=inf) rather than omitted, since (like the
        friction-circle rows) the sparsity pattern is fixed once here, not
        per-tick. Read ONCE here, at construction time, like _use_slack.
        """
        N = self.N
        n_du = NU * N
        self._use_slack = self.nmpc.nmpc_track_halfwidth > 0.0
        n_slack = N if self._use_slack else 0
        self._use_vslack = self.speed_limit_enabled
        n_vslack = N if self._use_vslack else 0
        nz = n_du + n_slack + n_vslack
        n_fric = 2 * N if self.friction_circle_enabled else 0

        # First-difference operator E: diff_k = u_k - u_{k-1} (u_{-1} = u_prev).
        E = np.zeros((n_du, n_du))
        for k in range(N):
            E[k * NU:(k + 1) * NU, k * NU:(k + 1) * NU] = np.eye(NU)
            if k > 0:
                E[k * NU:(k + 1) * NU, (k - 1) * NU:k * NU] = -np.eye(NU)
        self._E = E
        self._Rr_flat = np.tile(self.r_rate, N)
        self._ErE = E.T @ (self._Rr_flat[:, None] * E)
        # Second-difference operator for the steering-JERK penalty
        # (rjerk_delta > 0). E2 = E @ E: applying the first-difference
        # operator twice gives du_k - du_{k-1}, i.e. steering ACCELERATION.
        # The plain rate cost charges by |du|, identical for a sustained ramp
        # into a corner and for one leg of an oscillation, so it cannot damp
        # hunting without also resisting turn-in. Measured live, reversals
        # carry ~4.3x the |d2| of same-direction ramps vs only ~1.9x the
        # |d1|. A steady ramp is therefore nearly free here; a wiggle is not.
        # No OSQP sparsity change: p_mask[:n_du,:n_du] is already a dense
        # upper triangle, so this adds no new nonzeros to the pattern.
        self._E2 = E @ E
        rj = np.tile(np.array([self.rjerk_delta, self.rjerk_a]), N)
        self._E2rE2 = (self._E2.T @ (rj[:, None] * self._E2)
                       if (self.rjerk_delta or self.rjerk_a) else None)

        # P pattern: dense upper triangle over dU, plus the slack diagonals.
        p_mask = np.zeros((nz, nz), dtype=bool)
        p_mask[:n_du, :n_du] = np.triu(np.ones((n_du, n_du), dtype=bool))
        if n_slack:
            idx = np.arange(n_du, n_du + n_slack)
            p_mask[idx, idx] = True
        if n_vslack:
            idx = np.arange(n_du + n_slack, nz)
            p_mask[idx, idx] = True
        P, p_rows, p_cols = _csc_pattern(p_mask)

        # A pattern.
        n_rows = (2 * n_du + (3 * N if self._use_slack else 0)
                  + n_fric + (2 * N if self._use_vslack else 0))
        a_mask = np.zeros((n_rows, nz), dtype=bool)
        a_mask[:n_du, :n_du] = np.eye(n_du, dtype=bool)
        a_mask[n_du:2 * n_du, :n_du] = E != 0.0
        if self._use_slack:
            r0 = 2 * n_du
            # Track rows are structurally dense in dU: stage k's e_y depends on
            # every earlier input, and marking the (structurally zero) later
            # columns present too keeps this pattern trivially fixed.
            a_mask[r0:r0 + 2 * N, :n_du] = True
            for k in range(N):
                a_mask[r0 + k, n_du + k] = True                 # -slack_k
                a_mask[r0 + N + k, n_du + k] = True              # +slack_k
                a_mask[r0 + 2 * N + k, n_du + k] = True          # slack_k >= 0
        if n_fric:
            rf0 = 2 * n_du + (3 * N if self._use_slack else 0)
            a_mask[rf0:rf0 + n_fric, :n_du] = True
        if n_vslack:
            rv0 = 2 * n_du + (3 * N if self._use_slack else 0) + n_fric
            # Speed rows are dense in dU for the same reason the track rows
            # are: stage k's v_x depends on every earlier input through S.
            a_mask[rv0:rv0 + N, :n_du] = True
            for k in range(N):
                a_mask[rv0 + k, n_du + n_slack + k] = True           # -slack_v_k
                a_mask[rv0 + N + k, n_du + n_slack + k] = True       # slack_v_k >= 0
        A, a_rows, a_cols = _csc_pattern(a_mask)

        q = np.zeros(nz)
        l = np.full(n_rows, -np.inf)
        u = np.full(n_rows, np.inf)

        prob = osqp.OSQP()
        settings = dict(
            verbose=False,
            eps_abs=self.nmpc.nmpc_osqp_eps,
            eps_rel=self.nmpc.nmpc_osqp_eps,
            max_iter=int(self.nmpc.nmpc_osqp_max_iter),
        )
        try:
            prob.setup(P, q, A, l, u, warm_starting=True, polishing=False,
                       **settings)
        except TypeError:      # pragma: no cover - osqp < 1.0 naming
            prob.setup(P, q, A, l, u, warm_start=True, polish=False, **settings)

        self._qp = dict(
            prob=prob, P=P, A=A,
            p_rows=p_rows, p_cols=p_cols,
            a_rows=a_rows, a_cols=a_cols,
            n_du=n_du, n_slack=n_slack, n_vslack=n_vslack, n_fric=n_fric,
            nz=nz, n_rows=n_rows,
        )

    # ------------------------------------------------------------------
    # Prediction / linearisation
    # ------------------------------------------------------------------
    def _rollout(self, x0, U, ref):
        """
        Nonlinear forward simulation of the whole horizon from x0 under U.
        Returns X with shape (N+1, NX). Sequential by construction (each stage
        depends on the previous one), so this is the one part of a Gauss-Newton
        iteration that cannot be vectorised across stages — hence the scalar
        _step_scalar fast path (see its docstring: 1 ms here versus 17 ms
        through the vectorised form).
        """
        N = self.N
        X = np.empty((N + 1, NX))
        X[0] = x0
        xk = [float(v) for v in x0]
        p, dt, n_sub = self.plant, self.dt, self.nmpc.nmpc_rk_substeps
        for k in range(N):
            xk = _step_scalar(xk, U[k], ref, p, dt, n_sub)
            X[k + 1] = xk
        return X

    def _project_feasible(self, U):
        """
        Project an input trajectory onto the set the QP's own constraints
        describe: input bounds, and the per-step slew limit measured from
        self._u_prev forward.

        This is what makes the subproblem UNCONDITIONALLY FEASIBLE, and that
        matters more than it looks. The QP's slew rows are
        `-du_max - e <= E dU <= du_max - e` with `e` the current iterate's own
        differences, so dU = 0 is feasible if and only if the iterate already
        respects the slew limit. A warm start that does not (shifting the
        previous solution and clipping it to the input bounds can produce one)
        can make the whole subproblem primal-infeasible — after which OSQP
        returns a finite but meaningless x. Projecting first removes that
        failure mode by construction rather than trying to detect it.
        """
        Up = np.clip(np.asarray(U, dtype=float), self.u_min, self.u_max)
        prev = self._u_prev
        for k in range(Up.shape[0]):
            Up[k] = np.clip(Up[k], prev - self.du_max, prev + self.du_max)
            prev = Up[k]
        return Up

    def _jacobians(self, X, U, ref):
        """
        One-step Jacobians A_k = d x_{k+1}/d x_k and B_k = d x_{k+1}/d u_k for
        every stage, by forward finite differences — vectorised over stages, so
        each perturbation direction costs ONE batched one-step integration of
        all N stages rather than N scalar ones (10 batched steps total).

        These use nmpc_jac_substeps, which now matches the rollout's
        nmpc_rk_substeps (both 4). It used to be deliberately coarser (1 vs 2)
        to halve the cost of the dominant term in a Gauss-Newton iteration,
        on the argument that A_k/B_k only supply the QP's STEP DIRECTION and
        never the predicted trajectory, so a coarser sensitivity costs at most
        a slightly worse step that the next iteration and the trust region
        absorb.

        That argument is sound about ACCURACY and wrong about STABILITY, which
        is what actually bit. The (v_y, r) sub-dynamics stiffen as 1/v_x, so
        below roughly 3.5 m/s too few substeps make this integration
        divergent rather than inaccurate. A divergent A_k does not degrade
        gracefully: it compounds through the condensing loop and leaves a
        Hessian whose only representable solution is exactly zero. Keep both
        counts at 4 and do not re-introduce the asymmetry as a cost saving.
        """
        N = self.N
        Xs = X[:N]
        p, dt = self.plant, self.dt
        n_sub = max(1, int(self.nmpc.nmpc_jac_substeps))
        F0 = _step(Xs, U, ref, p, dt, n_sub)
        A = np.empty((N, NX, NX))
        B = np.empty((N, NX, NU))
        for j in range(NX):
            Xp = Xs.copy()
            Xp[:, j] += _FD_EPS_X[j]
            A[:, :, j] = (_step(Xp, U, ref, p, dt, n_sub) - F0) / _FD_EPS_X[j]
        for j in range(NU):
            Up = U.copy()
            Up[:, j] += _FD_EPS_U[j]
            B[:, :, j] = (_step(Xs, Up, ref, p, dt, n_sub) - F0) / _FD_EPS_U[j]
        return A, B

    def _output_jacobians(self, X, ref, v_ref):
        """
        Output Jacobians C_k = d h/d x at every stage (including the terminal
        one), same vectorised forward-difference scheme as _jacobians.

        When self.friction_circle_enabled, H0/C carry NH_FRICTION extra rows
        (F_yf, F_yr — see _outputs' docstring), riding along through this
        SAME finite-difference pass at no extra rollout cost. Shape is
        (stages, NH, NX) when the flag is False, IDENTICAL to before this
        feature existed.
        """
        H0 = _outputs(X, ref, self.plant, v_ref,
                      horizon_speed_profile_enabled=self.horizon_speed_profile_enabled,
                      friction_circle_enabled=self.friction_circle_enabled)
        n_rows = H0.shape[1]
        C = np.empty((X.shape[0], n_rows, NX))
        for j in range(NX):
            Xp = X.copy()
            Xp[:, j] += _FD_EPS_X[j]
            Hp = _outputs(Xp, ref, self.plant, v_ref,
                         horizon_speed_profile_enabled=self.horizon_speed_profile_enabled,
                         friction_circle_enabled=self.friction_circle_enabled)
            C[:, :, j] = (Hp - H0) / _FD_EPS_X[j]
        return H0, C

    def _cost(self, X, U, H, ref=None):
        """
        True (nonlinear) cost of a candidate trajectory — used only by the
        backtracking test, so it must match the QP's objective term for term:
        weighted output residuals with the terminal scale, input effort with
        the accel/brake split, input rate against u_prev, the soft-track
        slack penalty at its optimal value for this trajectory (max(0, |e_y| -
        halfwidth), which is what the QP's slack would be), and (when
        speed_limit_enabled) the analogous soft speed-limit slack penalty
        (max(0, v_x - v_max(s)), the slack_v the QP would choose).

        H may carry NH_FRICTION extra (unweighted) columns when
        friction_circle_enabled -- sliced down to the original NH cost rows
        here so w (len NH) always broadcasts correctly and the objective
        itself never includes the friction rows, per the feature's spec.

        ref is only required when self._use_vslack; omitted (None) is fine
        for callers that never enable that flag, matching every other
        experimental feature's opt-in-only signature footprint.
        """
        w = self.w_out
        H = H[:, :NH]
        stage = float(np.sum(w * H[:-1] ** 2)) + float(
            self.terminal_scale * np.sum(w * H[-1] ** 2))
        a = U[:, 1]
        eff = float(self.r_delta * np.sum(U[:, 0] ** 2)
                    + self.r_a_accel * np.sum(np.maximum(a, 0.0) ** 2)
                    + self.r_a_brake * np.sum(np.minimum(a, 0.0) ** 2))
        du = np.vstack([U[0] - self._u_prev, np.diff(U, axis=0)])
        # Score the rate term with self._Rr_flat -- the SAME per-stage weight
        # vector the QP's Hessian (_ErE) is built from -- not the flat
        # self.r_rate. Any mechanism that reshapes the rate weight (corner
        # blend, anti-hunt, reversal penalty, stage ramp) writes _Rr_flat; if
        # this used self.r_rate the backtracking line search would score a
        # DIFFERENT objective from the one the QP minimised and could reject
        # genuinely improving steps. Falls back to the flat tile if absent.
        _rr = getattr(self, '_Rr_flat', None)
        if _rr is None or _rr.shape[0] != du.size:
            rate = float(np.sum(self.r_rate * du ** 2))
        else:
            rate = float(np.sum(_rr * du.reshape(-1) ** 2))
        jerk = 0.0
        if self._E2rE2 is not None:
            # Same objective the QP minimises (see _solve_step's jerk block).
            d2 = np.vstack([du[0] - (self._u_prev - self._u_prev2),
                            np.diff(du, axis=0)])
            jerk = float(np.sum(np.array([self.rjerk_delta, self.rjerk_a]) * d2 ** 2))
        slack = 0.0
        if self._use_slack:
            over = np.maximum(np.abs(X[1:, IDX_EY]) - self.nmpc.nmpc_track_halfwidth,
                              0.0)
            slack = float(self.nmpc.nmpc_slack_weight * np.sum(over ** 2))
        vslack = 0.0
        if self._use_vslack and ref is not None and ref.v_target is not None:
            v_max = ref.v_ref_at(X[1:, IDX_S]) + self.speed_limit_margin
            over_v = np.maximum(X[1:, IDX_VX] - v_max, 0.0)
            vslack = float(self.speed_limit_slack_weight * np.sum(over_v ** 2))
        return stage + eff + rate + jerk + slack + vslack

    def _solve_step(self, X, U, ref, v_ref):
        """
        One Gauss-Newton SQP iteration: condense, solve the QP, return the
        input-deviation trajectory dU (N, NU) and the OSQP status string.

        Because X was produced by rolling the nonlinear model forward from the
        measured state under U, the linearised dynamics have ZERO defect, so
        the condensed sensitivities alone describe the subproblem exactly:
        dx_k = sum_{j<k} Phi_{k,j} du_j.

        When self.friction_circle_enabled, H/C carry NH_FRICTION extra
        (unweighted) rows (see _outputs) -- G/g below are built from ONLY
        the first NH rows (the cost), and the friction rows are sliced out
        separately further down to build the hard QP constraint.
        """
        N = self.N
        qp = self._qp
        n_du, n_slack, n_vslack, nz, n_rows = (
            qp['n_du'], qp['n_slack'], qp['n_vslack'], qp['nz'], qp['n_rows'])

        A_k, B_k = self._jacobians(X, U, ref)
        H, C = self._output_jacobians(X, ref, v_ref)
        Hc, Cc = H[:, :NH], C[:, :NH, :]

        # Condensing: S[k] = d x_k / d U_flat, (NX, n_du).
        S = np.zeros((N + 1, NX, n_du))
        for k in range(N):
            S[k + 1] = A_k[k] @ S[k]
            S[k + 1][:, k * NU:(k + 1) * NU] += B_k[k]

        # Weighted output sensitivities: G = sqrt(W) C S, stacked over stages,
        # with the terminal stage scaled by sqrt(terminal_scale).
        sw = np.sqrt(self.w_out)
        scale = np.ones(N + 1)
        scale[N] = math.sqrt(max(self.terminal_scale, 0.0))
        WC = (sw[None, :, None] * Cc) * scale[:, None, None]
        G = np.einsum('kij,kjl->kil', WC, S).reshape((N + 1) * NH, n_du)
        g = ((sw[None, :] * Hc) * scale[:, None]).reshape(-1)

        # Input effort: accel/brake weight chosen per stage by the sign of the
        # current iterate's a_cmd (the linearisation point) — the SQP analogue
        # of _build_qp's cp.pos/cp.neg split, which needs no extra variables
        # because the sign is known at linearisation time.
        ru = np.empty((N, NU))
        ru[:, 0] = self.r_delta
        ru[:, 1] = np.where(U[:, 1] >= 0.0, self.r_a_accel, self.r_a_brake)
        ru_flat = ru.reshape(-1)
        u_flat = U.reshape(-1)

        # Input rate: diff = E dU + e, e = E u_flat - [u_prev, 0, ...].
        e_rate = self._E @ u_flat
        e_rate[:NU] -= self._u_prev

        Hess = G.T @ G + np.diag(ru_flat) + self._ErE
        grad = G.T @ g + ru_flat * u_flat + self._E.T @ (self._Rr_flat * e_rate)
        if self._E2rE2 is not None:
            # ||E2 u - d2_anchor||^2_Rj: contributes E2'RjE2 to the Hessian.
            # The anchor carries the last TWO commands into step 0's second
            # difference (as _u_prev does for the first difference) -- without
            # it the term is blind to a reversal spanning the tick boundary,
            # exactly what it exists to catch.
            e_jerk = self._E2 @ u_flat
            e_jerk[:NU] -= (2.0 * self._u_prev - self._u_prev2)
            e_jerk[NU:2 * NU] += self._u_prev
            rj = np.tile(np.array([self.rjerk_delta, self.rjerk_a]), N)
            Hess = Hess + self._E2rE2
            grad = grad + self._E2.T @ (rj * e_jerk)

        P_dense = np.zeros((nz, nz))
        P_dense[:n_du, :n_du] = 2.0 * Hess
        q = np.zeros(nz)
        q[:n_du] = 2.0 * grad
        if n_slack:
            idx = np.arange(n_du, n_du + n_slack)
            P_dense[idx, idx] = 2.0 * self.nmpc.nmpc_slack_weight
        if n_vslack:
            idx = np.arange(n_du + n_slack, nz)
            P_dense[idx, idx] = 2.0 * self.speed_limit_slack_weight

        A_dense = np.zeros((n_rows, nz))
        l = np.empty(n_rows)
        u = np.empty(n_rows)

        # (1) box + trust region on dU.
        A_dense[:n_du, :n_du] = np.eye(n_du)
        tr = np.tile(np.array([self.nmpc.nmpc_trust_delta_rad,
                               self.nmpc.nmpc_trust_a]), N)
        lo = np.maximum(np.tile(self.u_min, N) - u_flat, -tr)
        hi = np.minimum(np.tile(self.u_max, N) - u_flat, tr)
        # A trust region tighter than the distance to a violated bound would
        # make the box infeasible; keep lo <= hi in that (transient) case.
        lo = np.minimum(lo, hi)
        l[:n_du], u[:n_du] = lo, hi

        # (2) slew rate.
        A_dense[n_du:2 * n_du, :n_du] = self._E
        du_flat = np.tile(self.du_max, N)
        l[n_du:2 * n_du] = -du_flat - e_rate
        u[n_du:2 * n_du] = du_flat - e_rate

        # (3)-(5) soft track bound with slack.
        if n_slack:
            r0 = 2 * n_du
            hw = self.nmpc.nmpc_track_halfwidth
            S_ey = S[1:, IDX_EY, :]              # (N, n_du)
            ey = X[1:, IDX_EY]
            A_dense[r0:r0 + N, :n_du] = S_ey
            A_dense[r0:r0 + N, n_du:n_du + n_slack] = -np.eye(N)
            l[r0:r0 + N] = -np.inf
            u[r0:r0 + N] = hw - ey
            A_dense[r0 + N:r0 + 2 * N, :n_du] = S_ey
            A_dense[r0 + N:r0 + 2 * N, n_du:n_du + n_slack] = np.eye(N)
            l[r0 + N:r0 + 2 * N] = -hw - ey
            u[r0 + N:r0 + 2 * N] = np.inf
            A_dense[r0 + 2 * N:r0 + 3 * N, n_du:n_du + n_slack] = np.eye(N)
            l[r0 + 2 * N:r0 + 3 * N] = 0.0
            u[r0 + 2 * N:r0 + 3 * N] = np.inf

        n_fric = qp['n_fric']
        if n_fric:
            # Hard |F_yf|, |F_yr| <= F_max bound, ADDITIONAL to the existing
            # soft alat-ceiling saturation inside _f/_f_scalar (untouched).
            # F_axle(x0) + dF/dU_flat @ dU, linearised at the current
            # iterate exactly like the soft-track rows above -- dF/dU_flat
            # is C's two extra rows (dF/dx, "for free" from
            # _output_jacobians) composed with the SAME S = dx/dU_flat the
            # cost rows already use. A symmetric two-sided bound needs only
            # ONE row per axle per stage (both l and u set), hence n_fric =
            # 2 (axles) * N (stages).
            rf0 = 2 * n_du + (3 * N if n_slack else 0)
            F0 = H[1:, NH:NH + 2]                    # (N, 2): F_yf, F_yr at x0
            dF_dU = np.einsum('kij,kjl->kil', C[1:, NH:NH + 2, :], S[1:])  # (N,2,n_du)
            v_x_pred = X[1:, IDX_VX]
            F_max = np.maximum(self._fmax_flat,
                               self._fmax_slope * np.abs(v_x_pred) + self._fmax_intercept)
            # Rows rf0 .. rf0+N-1: front axle.
            A_dense[rf0:rf0 + N, :n_du] = dF_dU[:, 0, :]
            l[rf0:rf0 + N] = -F_max - F0[:, 0]
            u[rf0:rf0 + N] = F_max - F0[:, 0]
            # Rows rf0+N .. rf0+2N-1: rear axle.
            A_dense[rf0 + N:rf0 + 2 * N, :n_du] = dF_dU[:, 1, :]
            l[rf0 + N:rf0 + 2 * N] = -F_max - F0[:, 1]
            u[rf0 + N:rf0 + 2 * N] = F_max - F0[:, 1]

        if n_vslack:
            rv0 = 2 * n_du + (3 * N if n_slack else 0) + n_fric
            S_vx = S[1:, IDX_VX, :]              # (N, n_du)
            vx = X[1:, IDX_VX]
            if ref.v_target is not None:
                v_max = ref.v_ref_at(X[1:, IDX_S]) + self.speed_limit_margin
            else:
                # No profile supplied this tick (e.g. live-planner mode with
                # no precomputed speed CSV) -- leave the rows inert rather
                # than tightening around whatever v_max happened to be last,
                # same "no-op when data is absent" contract as
                # horizon_speed_profile_enabled's own ref.v_target gate.
                v_max = np.full(N, np.inf)
            # (6) v_x_k - slack_v_k <= v_max_k.
            A_dense[rv0:rv0 + N, :n_du] = S_vx
            A_dense[rv0:rv0 + N, n_du + n_slack:nz] = -np.eye(N)
            l[rv0:rv0 + N] = -np.inf
            u[rv0:rv0 + N] = v_max - vx
            # (7) slack_v >= 0.
            A_dense[rv0 + N:rv0 + 2 * N, n_du + n_slack:nz] = np.eye(N)
            l[rv0 + N:rv0 + 2 * N] = 0.0
            u[rv0 + N:rv0 + 2 * N] = np.inf

        qp['prob'].update(
            Px=P_dense[qp['p_rows'], qp['p_cols']],
            Ax=A_dense[qp['a_rows'], qp['a_cols']],
            q=q, l=l, u=u,
        )
        res = qp['prob'].solve()
        status = str(res.info.status).lower()
        # Status MUST be checked, not just finiteness: on a primal-infeasible
        # or otherwise failed subproblem OSQP returns a finite but MEANINGLESS
        # x, and taking it as a step direction is exactly how this controller
        # first diverged in offline testing (a wrong-way full-lock ramp built
        # up over ~20 ticks, each moving the full slew limit in the garbage
        # direction — see late_turn_in_investigation.md Part 16 §16.6).
        # 'solved inaccurate' / 'maximum iterations reached' ARE accepted:
        # they are still descent directions in practice, and the caller
        # validates every step against the true nonlinear cost before keeping
        # it, so a poor direction costs one wasted iteration, never a bad
        # command.
        ok = ('solved' in status) or ('maximum iterations' in status)
        if not ok or res.x is None or not np.all(np.isfinite(res.x[:n_du])):
            return None, status
        return res.x[:n_du].reshape(N, NU), status

    # ------------------------------------------------------------------
    # Delay compensation
    # ------------------------------------------------------------------
    def _update_n_delay(self, pose_age_s: float) -> int:
        """
        Filtered, hysteresis-gated rollforward depth from a measured pose age.

        Deliberate duplicate of MPCController._update_n_delay (same MPCParams
        fields, same arithmetic): that method is bound to the LTV-QP
        controller's own state, and refactoring it out would mean editing
        mpc_core.py's live solve path, which this feature is specifically
        designed not to touch. Keep the two in sync if either changes.
        """
        age = max(0.0, float(pose_age_s))
        cap = self.params.max_delay_compensation_steps
        if self._pose_age_filtered is None:
            self._pose_age_filtered = age
            self._n_delay = int(np.clip(round(age / self.dt), 0, cap))
            return self._n_delay
        self._pose_age_filtered += (
            self.params.pose_age_lp_alpha * (age - self._pose_age_filtered))
        steps_f = self._pose_age_filtered / self.dt
        if abs(steps_f - self._n_delay) > 0.5 + self.params.n_delay_hysteresis:
            self._n_delay = int(np.clip(round(steps_f), 0, cap))
        return self._n_delay

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------
    def compute(
        self,
        path: np.ndarray,
        car_pos: np.ndarray,
        car_yaw: float,
        car_speed: float,
        desired_speed: float,
        car_yaw_rate: float = 0.0,
        pose_age_s: float = 0.0,
        car_vy: float = 0.0,
    ) -> tuple[float, float, float]:
        """
        Run one NMPC control step. Signature, units, return convention
        ((steering in [-1,1], throttle in [0,1], brake in [0,1])) and the
        short-path guard are all identical to MPCController.compute(), so the
        calling nodes need no branch beyond which object they construct.
        """
        if path is None or len(path) < 3:
            return 0.0, 0.0, 0.5

        t0 = time.perf_counter()

        # Same first-order target-speed filter as MPCController.compute().
        alpha = 0.08
        if self._v_des_filtered is None:
            self._v_des_filtered = desired_speed
        self._v_des_filtered += alpha * (desired_speed - self._v_des_filtered)
        v_ref = float(self._v_des_filtered)

        ref = self._path_reference(path)
        if ref is None or ref.total < 1e-3:
            return 0.0, 0.0, 0.5

        # ── Measured Frenet state ──────────────────────────────────────
        fa = np.asarray(car_pos, dtype=float) + self.lf * np.array(
            [math.cos(car_yaw), math.sin(car_yaw)])
        s0, e_y, e_psi, base_idx, path_yaw = ref.project(fa, car_yaw)
        x0 = np.array([
            s0, e_y, e_psi,
            max(float(car_speed), 0.0), float(car_vy), float(car_yaw_rate),
            self._delta_act, self._a_act,
        ])

        # ── Corner-blend / anti-hunt (EXPERIMENTAL, default off — see module
        # docstring) — ALTERNATIVES, not composed: the corner-factor blend
        # takes priority when both are enabled (skips anti-hunt entirely in
        # that case). Same signals/functions as the LTV-QP path (imported
        # verbatim from mpc_core, not reimplemented). Computed once per
        # compute() call (this tick's measured state), and applied UNIFORMLY
        # across the whole horizon for this tick's solve — not a function of
        # horizon step, so neither schedules a future obligation the way the
        # deleted lookahead family did. self._Rr_flat/self._ErE are
        # ordinarily fixed at _build_qp() time; when both flags are off
        # (default), neither is touched here, so behaviour is byte-identical
        # to before either feature existed.
        kappa_now = float(ref.kappa_at(np.array([s0]))[0])
        m_rrate_antihunt = 1.0
        # Always computed (not gated behind corner_rrate_blend_enabled) --
        # this is a general current-curvature signal other mechanisms also
        # key off via last_telemetry, independent of whether the R_rate
        # weight-blend feature itself is active.
        corner_frac = _corner_factor(kappa_now, self.corner_factor_k)
        rrate_steer_corner_blend = float(self.r_rate[0])
        # Tracks R_rate[0,0]'s running value through the if/elif AND the
        # reversal-penalty composition below, so the reversal penalty (which
        # applies regardless of which branch ran) boosts whatever value is
        # actually current rather than always the pre-if/elif base -- the
        # same silent-discard bug already found and fixed twice tonight in
        # mpc_core.py's own corner-blend/anti-hunt composition.
        rrate_steer_current = rrate_steer_corner_blend
        if self.corner_rrate_blend_enabled:
            rrate_steer_corner_blend = _blend(
                self.rrate_steer_straight, self.rrate_steer_corner, corner_frac)
            rrate_steer_current = rrate_steer_corner_blend
        elif self.steer_rate_anti_hunt_enabled:
            R2 = _steer_rate_anti_hunt(
                kappa_now, e_y, np.diag(self.r_rate), True,
                e_psi=e_psi, boost_max=self.anti_hunt_boost_max,
            )
            m_rrate_antihunt = float(R2[0, 0] / self.r_rate[0]) if self.r_rate[0] else 1.0
            rrate_steer_current = float(R2[0, 0])

        m_rrate_reversal = 1.0
        if self.reversal_penalty_enabled:
            R3 = _reversal_penalty_boost(
                float(self._u_prev[0]), np.diag([rrate_steer_current, self.r_rate[1]]),
                True, boost_max=self.reversal_penalty_boost_max, k=self.reversal_penalty_k,
            )
            m_rrate_reversal = (
                float(R3[0, 0] / rrate_steer_current) if rrate_steer_current else 1.0)
            rrate_steer_current = float(R3[0, 0])

        if (self.corner_rrate_blend_enabled or self.steer_rate_anti_hunt_enabled
                or self.reversal_penalty_enabled or self.rrate_stage_ramp_enabled
                or self.rrate_zone_enabled):
            r_rate_tick = np.array([rrate_steer_current, self.r_rate[1]])
            Rr_flat = np.tile(r_rate_tick, self.N)
            if self.rrate_stage_ramp_enabled:
                Rr_flat = (Rr_flat.reshape(self.N, NU)
                           * _rrate_stage_ramp(self.N, self.rrate_stage_near)[:, None]
                           ).reshape(-1)
            self._Rr_flat = Rr_flat
            self._ErE = self._E.T @ (Rr_flat[:, None] * self._E)

        # ── Delay compensation (nonlinear rollforward) ──────────────────
        # Same trigger/depth logic as the LTV-QP path, but rolled forward
        # through the NONLINEAR model instead of predict_ahead()'s linear
        # Ad/Bd — the model is right here, so there is no reason to use a
        # linearisation for it.
        if self.params.delay_compensation_enabled:
            n_delay = self._update_n_delay(pose_age_s)
            if n_delay > 0 and self._u_history:
                xk = [float(v) for v in x0]
                for u_hist in self._u_history[-n_delay:]:
                    xk = _step_scalar(xk, u_hist, ref, self.plant, self.dt,
                                      self.nmpc.nmpc_rk_substeps)
                x0 = np.array(xk)
        else:
            n_delay = 0

        # ── Warm start: shift the previous solution one step ────────────
        if self._have_warm_start:
            U = np.vstack([self._U[1:], self._U[-1:]])
        else:
            U = np.tile(self._u_prev, (self.N, 1))
        U = self._project_feasible(U)

        # ── Gauss-Newton SQP ───────────────────────────────────────────
        budget_s = self.nmpc.nmpc_solve_budget_ms * 1e-3
        X = self._rollout(x0, U, ref)

        # Three-zone rate schedule (rrate_zone_enabled). Applied HERE, not in
        # the block above, because it needs kappa across the PREDICTED horizon,
        # which only exists once X has been rolled out.
        m_rrate_zone = 1.0
        if self.rrate_zone_enabled:
            kap_h = ref.kappa_at(X[:, IDX_S])
            m_rrate_zone = _rrate_zone_scale(
                kappa_now, float(np.abs(kap_h).max()), self.corner_factor_k,
                self.rrate_zone_boost_straight, self.rrate_zone_ease_approach,
                self.rrate_zone_floor_corner)
            self._Rr_flat = self._Rr_flat * np.tile(
                np.array([m_rrate_zone, 1.0]), self.N)
            self._ErE = self._E.T @ (self._Rr_flat[:, None] * self._E)
        H = _outputs(X, ref, self.plant, v_ref,
                     horizon_speed_profile_enabled=self.horizon_speed_profile_enabled,
                     friction_circle_enabled=self.friction_circle_enabled)
        cost = self._cost(X, U, H, ref)
        iters = 0
        status = 'warm-start-only'
        for _ in range(max(1, int(self.nmpc.nmpc_sqp_iters))):
            if time.perf_counter() - t0 > budget_s:
                status = 'budget'
                break
            dU, status = self._solve_step(X, U, ref, v_ref)
            if dU is None:
                break
            step = 1.0
            accepted = False
            for _bt in range(max(0, int(self.nmpc.nmpc_backtrack_max)) + 1):
                U_try = np.clip(U + step * dU, self.u_min, self.u_max)
                X_try = self._rollout(x0, U_try, ref)
                H_try = _outputs(X_try, ref, self.plant, v_ref,
                                 horizon_speed_profile_enabled=self.horizon_speed_profile_enabled,
                                 friction_circle_enabled=self.friction_circle_enabled)
                cost_try = self._cost(X_try, U_try, H_try, ref)
                # ONLY a genuine improvement is accepted. Accepting the
                # smallest trial regardless (an earlier version of this loop
                # did, "so a tick always makes progress") means a bad search
                # direction is written into the warm start and carried into the
                # next tick — which is how a single failed subproblem grew into
                # a divergent wrong-way full-lock ramp in offline testing.
                # Rejecting leaves U at the previous tick's shifted solution,
                # which is always feasible and always sane.
                if cost_try <= cost:
                    U, X, H, cost = U_try, X_try, H_try, cost_try
                    accepted = True
                    break
                step *= 0.5
            iters += 1
            if not accepted:
                status = 'rejected'
                break
            # U + Delta is slew-feasible by construction (Delta = 0 is feasible
            # and the QP's rate rows are linear, so any fraction of an accepted
            # step is too), and the clip above cannot break that when both
            # endpoints already respect the input bounds.

        self._U = U
        self._have_warm_start = True

        # ── Ship u[0], hard-limited exactly as the LTV-QP path is ──────
        u_opt = np.clip(U[0], self.u_min, self.u_max)
        u_opt = np.clip(u_opt, self._u_prev - self.du_max, self._u_prev + self.du_max)
        self._u_history.append(u_opt.copy())
        if len(self._u_history) > self.params.max_delay_compensation_steps:
            del self._u_history[:-self.params.max_delay_compensation_steps]

        exp_delta = math.exp(-self.dt / self.plant.tau_delta)
        exp_a = math.exp(-self.dt / self.plant.tau_a)
        self._delta_act = self._delta_act * exp_delta + u_opt[0] * (1.0 - exp_delta)
        self._a_act = self._a_act * exp_a + u_opt[1] * (1.0 - exp_a)
        self._u_prev2 = self._u_prev.copy()
        self._u_prev = u_opt.copy()

        delta_cmd = float(np.clip(u_opt[0], -MAX_STEER_RAD, MAX_STEER_RAD))
        a_cmd = float(u_opt[1])
        steering = float(np.clip(-delta_cmd / MAX_STEER_RAD, -1.0, 1.0))
        if a_cmd >= 0.0:
            throttle = float(np.clip(a_cmd / self.a_max, 0.0, 1.0))
            brake = 0.0
        else:
            throttle = 0.0
            brake = float(np.clip(-a_cmd / self.a_max_brake, 0.0, 1.0))

        solve_ms = (time.perf_counter() - t0) * 1e3

        # Telemetry: the keys mpc_core publishes keep their exact meaning (so
        # every existing offline analysis script and telemetry_logger column
        # still works), plus nmpc_* diagnostics. kappa/kappa_max_abs are
        # recomputed here from the SAME kappa(s) reference the prediction used
        # — kappa at the car, and peak |kappa| over the horizon's own predicted
        # arc length, which is the NMPC's natural analogue of the LTV-QP's
        # speed-scaled lookahead window.
        kap_horizon = ref.kappa_at(X[:, IDX_S])
        self.last_telemetry = {
            'e_y': float(e_y),
            'e_psi': float(e_psi),
            'e_v': float(car_speed - v_ref),
            'kappa': kappa_now,
            'base_idx': int(base_idx),
            'kappa_max_abs': float(np.abs(kap_horizon).max()),
            'm_Rrate_antihunt': m_rrate_antihunt,
            'm_Rrate_reversal': m_rrate_reversal,
            'm_Rrate_zone': m_rrate_zone,
            'corner_frac': corner_frac,
            # The FINAL, fully-composed R_rate[0,0] actually used this tick
            # -- same semantic as mpc_core.py's own Rrate_steer_corner_blend
            # column (post corner-blend AND anti-hunt AND reversal-penalty),
            # not just the corner-blend stage in isolation.
            'Rrate_steer_corner_blend': rrate_steer_current,
            'pose_age_s': float(pose_age_s),
            'n_delay': int(n_delay),
            'solve_ms': float(solve_ms),
            'car_speed': float(car_speed),
            'desired_speed': float(v_ref),
            'steering': steering,
            'throttle': throttle,
            'brake': brake,
            'delta_cmd': delta_cmd,
            'a_cmd': a_cmd,
            'delta_act': float(self._delta_act),
            'a_act': float(self._a_act),
            # NMPC-specific: see telemetry_logger.NMPC_COLUMNS.
            'nmpc_iters': int(iters),
            'nmpc_cost': float(cost),
            'nmpc_status': 1.0 if status.lower().startswith('solved') else 0.0,
            'nmpc_s0': float(s0),
            'nmpc_kappa_horizon_end': float(kap_horizon[-1]),
            'nmpc_pred_ey_end': float(X[-1, IDX_EY]),
            'nmpc_pred_epsi_end': float(X[-1, IDX_EPSI]),
            'nmpc_pred_ey_max_abs': float(np.abs(X[:, IDX_EY]).max()),
        }
        if self.friction_circle_enabled:
            # H's two extra (unweighted) rows -- realized per-axle force at
            # the FINAL accepted trajectory, see _outputs' docstring.
            self.last_telemetry['nmpc_fyf_max_abs'] = float(np.abs(H[:, NH]).max())
            self.last_telemetry['nmpc_fyr_max_abs'] = float(np.abs(H[:, NH + 1]).max())
        if self.speed_limit_enabled and ref.v_target is not None:
            # Worst predicted overspeed vs the profile at the FINAL accepted
            # trajectory -- 0 means the soft bound was never active this
            # tick, a positive value shows how much slack the QP actually
            # needed (same diagnostic role as nmpc_pred_ey_max_abs above).
            v_max_final = ref.v_ref_at(X[1:, IDX_S]) + self.speed_limit_margin
            self.last_telemetry['nmpc_speed_limit_over_max'] = float(
                np.maximum(X[1:, IDX_VX] - v_max_final, 0.0).max())

        # RViz visualisation only, default off (see NMPCParams field docstring)
        # so there is zero added cost -- not even the np.interp calls below --
        # unless a caller has explicitly opted in.
        if self.nmpc.nmpc_publish_prediction_enabled:
            xs, ys = ref.xy_at(X[:, IDX_S], X[:, IDX_EY])
            self.last_prediction_xy = np.column_stack([xs, ys])
        else:
            self.last_prediction_xy = None
        return steering, throttle, brake

    def _path_reference(self, path) -> PathReference | None:
        """
        Return the PathReference for this tick's path: the one built at load
        time by set_static_path() when its signature still matches (the static
        case — zero per-tick cost), otherwise a cached per-tick rebuild that is
        only redone when the path actually changes (live-planner mode).
        """
        path = np.asarray(path, dtype=float)
        sig = (
            len(path),
            float(path[0, 0]), float(path[0, 1]),
            float(path[-1, 0]), float(path[-1, 1]),
        )
        if self._static_ref is not None and self._static_ref.signature[:5] == sig:
            return self._static_ref
        if self._ref is not None and self._ref_signature == sig:
            return self._ref
        try:
            self._ref = PathReference(
                path,
                dense_step=self.nmpc.nmpc_curvature_dense_step,
                smooth_w=self.nmpc.nmpc_curvature_smooth_w,
                kappa_clip=self.nmpc.nmpc_kappa_clip,
                spline_reference_enabled=self.spline_reference_enabled,
            )
        except (ValueError, IndexError):    # pragma: no cover - defensive
            return None
        self._ref_signature = sig
        return self._ref

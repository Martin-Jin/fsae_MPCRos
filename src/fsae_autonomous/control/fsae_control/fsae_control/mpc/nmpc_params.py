# Title: nmpc_params.py

"""
nmpc_params.py — STRUCTURAL/SOLVER tunables for the NONLINEAR MPC
path-tracking controller (nmpc_core.NMPCController). See
late_turn_in_investigation.md Part 16 for the research/decision record
behind the formulation.

WHAT LIVES HERE VS. IN mpc_params.py
--------------------------------------------------------
NMPC weight overrides live in mpc_params.py's MPCParams; this file holds
only structural/solver fields with no LTV-QP analogue. Do not re-add
weight fields here — see mpc_params.py instead.

What remains here are fields that have NO LTV-QP analogue to inherit
from — horizon length, SQP iteration count, trust-region size, solver
tolerances, curvature-smoothing parameters. These are genuinely NMPC-only
mechanics, not "MPC weights" in the sense the rest of MPCParams's fields
are.

PARITY, NOW THAT AN OFFLINE NMPC EXISTS
-----------------------------------------
Before fsae_MPCTest's offline NMPC port (controller/nmpc_optimiser.py),
these structural fields had no offline counterpart, so CLAUDE.md's
numeric-parity rule didn't apply to them. It does now: every field below
has a matching settings.py NMPC_* constant (see that file's "Nonlinear MPC
(NMPC)" section), kept numerically identical by hand — the same
discipline as Q_diag/R_diag/R_rate_diag always have been. Extend both
sides together if either changes.

ONE WEIGHT (now in mpc_params.py) DOES NOT TRANSFER WITH IDENTICAL
MEANING: q_r / nmpc_q_epsi_dot. In the LTV-QP it weights absolute yaw rate
`r`; in the Frenet NMPC it weights the heading-error RATE
`r - kappa*s_dot` (see nmpc_core._outputs). Penalising absolute `r` in a
curvature-aware model would penalise the yaw rate the car MUST hold to
follow a corner (r = kappa*v), i.e. it would fight cornering — which is
the exact failure this controller exists to remove. Same number,
different regressor: expect to re-sweep it. See Part 16 §16.3 choice (1),
and mpc_params.py's own docstring for the field itself.

PROVENANCE OF EVERY DEFAULT BELOW
---------------------------------
No default here is a fresh guess. Each is either (a) copied from an existing
validated value in mpc_core.py / control_utils.py (noted per field), or
(b) a solver/structural setting measured in Part 16 §16.7, or (c) an explicit
guard whose value is chosen to be inert on this car's real operating range
(also noted). Anything that is genuinely unvalidated says so in its `desc`.
"""

from dataclasses import dataclass, field, fields
import math


@dataclass
class NMPCParams:
    # ── Master switch ───────────────────────────────────────────────────
    # Default False: the LTV-QP MPCController stays the shipped controller.
    # Same rollout posture as use_precomputed_corner_map /
    # use_precomputed_heading_profile (land off, prove live, then consider
    # flipping) — and unlike those two, flipping this one swaps the whole
    # optimiser, so it is the most conservative default available.
    use_nmpc: bool = field(default=False, metadata={
        "unit": "bool",
        "desc": "true -> use nmpc_core.NMPCController (Frenet-frame nonlinear MPC) "
                "instead of mpc_core.MPCController (LTV-QP). Default false.",
        "controller": "nmpc_only",
    })

    # ── Horizon / real-time budget ──────────────────────────────────────
    # MEASURED, not assumed — see Part 16 §16.7 for the horizon-choice sweep.
    #
    # 20 (= 1.0 s) is chosen over 35 deliberately, even though 35 matches
    # MPCController's horizon: a LONGER horizon measured WORSE on tracking
    # here, because the prediction model is optimistic (linear tyres, no
    # suspension/relaxation) and that mismatch compounds over 1.75 s. 1.0 s at
    # this track's speeds is 12-17 m of anticipation, comparable to the LTV-QP's
    # own speed-scaled lookahead window. Raise it back toward 35 only with a
    # measurement, not on the assumption that more horizon is better.
    nmpc_horizon: int = field(default=20, metadata={
        "unit": "steps",
        "desc": "prediction horizon in steps (20 * dt=0.05 = 1.0 s). "
                "See Part 16 §16.7 for the horizon choice.",
        "controller": "nmpc_only",
    })
    # 1, not 2 — see §16.7. A single Gauss-Newton iteration per tick is the
    # standard real-time-iteration scheme — the warm start carries
    # convergence across ticks, and a converged-per-tick solution exploits
    # the optimistic model harder.
    nmpc_sqp_iters: int = field(default=1, metadata={
        "unit": "iterations",
        "desc": "max Gauss-Newton SQP iterations per control tick (real-time-"
                "iteration style: the previous tick's shifted solution is the "
                "warm start, so one iteration per tick still converges across "
                "ticks). See Part 16 §16.7 for the iteration-count choice.",
        "controller": "nmpc_only",
    })
    nmpc_solve_budget_ms: float = field(default=25.0, metadata={
        "unit": "ms",
        "desc": "wall-clock budget per tick; SQP stops early (shipping the best "
                "feasible iterate) once exceeded. Half of the 50 ms control "
                "period, leaving the rest of the tick for the node",
        "controller": "nmpc_only",
    })
    nmpc_rk_substeps: int = field(default=2, metadata={
        "unit": "substeps",
        "desc": "RK4 substeps per dt in the prediction rollout. 2 is needed "
                "because tau_a=0.02 s is stiff against dt=0.05 s (lambda*dt = "
                "-2.5, near RK4's real-axis stability edge)",
        "controller": "nmpc_only",
    })

    nmpc_jac_substeps: int = field(default=1, metadata={
        "unit": "substeps",
        "desc": "RK4 substeps used when finite-differencing the QP's A_k/B_k "
                "sensitivities. Deliberately coarser than nmpc_rk_substeps: "
                "these only set the SQP STEP DIRECTION, never the predicted "
                "trajectory, and this is the dominant cost per iteration "
                "(see nmpc_core._jacobians)",
        "controller": "nmpc_only",
    })

    # ── SQP step control ────────────────────────────────────────────────
    nmpc_trust_delta_rad: float = field(default=math.radians(9.0), metadata={
        "unit": "rad",
        "desc": "per-iteration trust region on each stage's steering deviation. "
                "9 deg = MPCController's own du_max steering slew per tick "
                "(180 deg/s * 0.05 s) — reused, not invented",
        "controller": "nmpc_only",
    })
    nmpc_trust_a: float = field(default=0.6, metadata={
        "unit": "m/s^2",
        "desc": "per-iteration trust region on each stage's accel deviation. "
                "0.6 = MPCController's du_max[1] — reused, not invented",
        "controller": "nmpc_only",
    })
    nmpc_backtrack_max: int = field(default=2, metadata={
        "unit": "halvings",
        "desc": "max step halvings if a full SQP step increases the true "
                "nonlinear cost (divergence guard). 0 disables backtracking",
        "controller": "nmpc_only",
    })

    # ── Soft track constraint (mirrors MPCController's own) ─────────────
    nmpc_track_halfwidth: float = field(default=3.5, metadata={
        "unit": "m",
        "desc": "soft |e_y| bound with slack, copied from _build_qp's existing "
                "+-3.5 m literal. <=0 removes the constraint (and its slack "
                "variables) entirely",
        "controller": "nmpc_only",
    })
    nmpc_slack_weight: float = field(default=10000.0, metadata={
        "unit": "1/m^2",
        "desc": "penalty on the track-bound slack, copied from _build_qp's "
                "existing W_slack = 10000.0",
        "controller": "nmpc_only",
    })

    # ── Curvature reference construction ────────────────────────────────
    # Both defaults are control_utils.curvature_speed()'s existing denoise
    # precedent (dense_step = 0.5 m, moving-average width 3), not new
    # smoothing constants. This matters more here than for the QP: with
    # kappa inside the PREDICTION, a spurious centreline spike (the known
    # open planner defect, CLAUDE.md) would be predicted as a real bend.
    nmpc_curvature_dense_step: float = field(default=0.5, metadata={
        "unit": "m",
        "desc": "arc-length resampling step for the kappa(s) reference "
                "(= curvature_speed()'s dense_step)",
        "controller": "nmpc_only",
    })
    nmpc_curvature_smooth_w: int = field(default=3, metadata={
        "unit": "samples",
        "desc": "moving-average width applied before differencing headings "
                "(= curvature_speed()'s w). 1 disables smoothing",
        "controller": "nmpc_only",
    })
    nmpc_kappa_clip: float = field(default=0.5, metadata={
        "unit": "1/m",
        "desc": "hard clamp on |kappa(s)|. GUARD, not a tuning knob: 0.5 = a "
                "2 m radius, the tightest corner curvature_speed()'s own "
                "docstring contemplates, so it is inert on any real track "
                "line and only catches a degenerate/spiking path",
        "controller": "nmpc_only",
    })

    nmpc_alat_ceiling_enabled: bool = field(default=True, metadata={
        "unit": "bool",
        "desc": "include FSDS's measured sustained lateral-acceleration ceiling "
                "(MPCParams.alat_ceiling_flat/_slope/_intercept, the same law "
                "mpc_core._alat_ceiling_at uses) as a smooth saturation of the "
                "prediction's tyre forces. True is correct for FSDS; set False "
                "for real-vehicle work, mirroring "
                "model/vehicle_physics.VehicleParams.alat_ceiling_enabled",
        "controller": "nmpc_only",
    })

    # ── Path reference construction ─────────────────────────────────────
    nmpc_spline_reference_enabled: bool = field(default=True, metadata={
        "unit": "bool",
        "desc": "true (default) -> PathReference builds kappa(s)/psi_ref(s) "
                "from an analytic CubicSpline fit to the raw waypoints "
                "(x(s), y(s) each independently splined over cumulative arc "
                "length) instead of the dense-resample + moving-average + "
                "finite-difference pipeline. A strict numerical-quality fix "
                "to the documented centreline-curvature-spikes defect with no "
                "new solver coupling, so it defaults on -- unlike every other "
                "flag in this file. False restores the old moving-average "
                "path exactly (kept, not deleted), for A/B comparison",
        "controller": "nmpc_only",
    })

    # ── Horizon speed profile (EXPERIMENTAL, default off) ────────────────
    nmpc_horizon_speed_profile_enabled: bool = field(default=False, metadata={
        "unit": "bool",
        "desc": "true -> sample a precomputed per-lap speed profile v(s) at "
                "each horizon stage's own PREDICTED arc length s_k "
                "(PathReference.v_ref_at) instead of holding v_ref constant "
                "across the horizon. Mirrors kappa(s)'s own state-keyed, "
                "non-schedulable lookup so it inherits the same property "
                "(see nmpc_core.py's module docstring on why curvature-as-"
                "exogenous-horizon-data produced wrong-direction transients). "
                "Only takes effect when a speed-profile array is actually "
                "supplied at PathReference construction time -- otherwise "
                "this flag is a no-op and v_ref stays the frozen scalar. "
                "Default False: genuine experiment, not yet validated",
        "controller": "nmpc_only",
    })

    # ── Friction-circle hard constraint (EXPERIMENTAL, default off) ──────
    nmpc_friction_circle_enabled: bool = field(default=False, metadata={
        "unit": "bool",
        "desc": "true -> add a HARD |F_yf|/|F_yr| <= F_max bound to the "
                "condensed QP, ADDITIONAL to (not a replacement for) the "
                "existing SOFT alat-ceiling tanh saturation inside _f/"
                "_f_scalar -- see CLAUDE.md's warning against touching that "
                "mechanism, which this does not. F_max is derived from the "
                "SAME measured ceiling law "
                "(alat_ceiling_flat/_slope/_intercept) via "
                "F_max = m * ceiling(v_x) / 2 per axle. Changes the QP's "
                "fixed sparsity pattern, so it is read once at construction "
                "time, not per-tick. When False, _build_qp/_outputs/"
                "_output_jacobians/_solve_step produce IDENTICAL output "
                "(including array shapes) to before this feature existed. "
                "Default False: genuine experiment, not yet validated",
        "controller": "nmpc_only",
    })

    # ── Soft per-stage speed limit (EXPERIMENTAL, default off) ───────────
    nmpc_speed_limit_enabled: bool = field(default=False, metadata={
        "unit": "bool",
        "desc": "true -> add a SOFT (slack-backed) v_x_k <= v_ref_at(s_k) + "
                "nmpc_speed_limit_margin + slack_v_k row per stage, same "
                "PathReference.v_ref_at(s_k) state-keyed lookup as "
                "nmpc_horizon_speed_profile_enabled, same slack-with-weight "
                "pattern as the existing soft track-bound rows (never a hard "
                "bound like nmpc_friction_circle_enabled -- that one's zero-"
                "slack hard bound went infeasible under ordinary cornering "
                "and stalled the car; see `docs/reference/`). Added "
                "2026-08-19 because nmpc_horizon_speed_profile_enabled's cost "
                "term alone was live-tested and rejected: the QP just SUMS "
                "(v_x-v_ref)^2 across stages with no ordering, so the solver "
                "can trade a bad early (in-corner) residual against a good "
                "late (post-corner) one in the SAME solve, producing v_actual "
                "~16.7 m/s against v_ref ~3-5 m/s approaching a corner. A "
                "per-stage INEQUALITY can't be traded away that way -- it "
                "must hold at every stage individually. Only takes effect "
                "when a speed-profile array is supplied (ref.v_target is not "
                "None), exactly like nmpc_horizon_speed_profile_enabled's own "
                "gating; can be enabled independently of that flag. Default "
                "False: genuine experiment, not yet validated",
        "controller": "nmpc_only",
    })
    nmpc_speed_limit_margin: float = field(default=0.5, metadata={
        "unit": "m/s",
        "desc": "added on top of v_ref_at(s_k) before the hard-but-soft bound "
                "applies, so ordinary tracking noise around the profile "
                "doesn't constantly engage slack. 0 = bound exactly at the "
                "profile's own value",
        "controller": "nmpc_only",
    })
    nmpc_speed_limit_slack_weight: float = field(default=200.0, metadata={
        "unit": "1/(m/s)^2",
        "desc": "penalty on the speed-limit slack, same role as "
                "nmpc_slack_weight for the track bound but a separate, much "
                "smaller constant: a speed overshoot of a few m/s for a tick "
                "or two while braking is expected and should cost noticeably "
                "less than actually leaving the track (nmpc_slack_weight = "
                "10000), not be pinned to zero as aggressively",
        "controller": "nmpc_only",
    })

    # ── Solver tolerance ────────────────────────────────────────────────
    nmpc_osqp_max_iter: int = field(default=500, metadata={
        "unit": "iterations",
        "desc": "OSQP iteration cap for the SQP subproblem. Bounded well below "
                "MPCController's 8000 on purpose: this is a step DIRECTION that "
                "the true-cost backtracking test validates before it is kept, "
                "so a hard subproblem should cost bounded time and be retried "
                "next tick rather than blow the 50 ms control period (an "
                "uncapped version spent up to 90 ms in single ticks — Part 16 "
                "§16.7)",
        "controller": "nmpc_only",
    })
    nmpc_osqp_eps: float = field(default=1e-4, metadata={
        "unit": "unitless",
        "desc": "OSQP eps_abs/eps_rel for the SQP subproblem. Looser than "
                "MPCController's 1e-5 on purpose: an SQP subproblem is a STEP "
                "direction that the next iteration corrects, not the final "
                "answer, so sub-1e-4 accuracy buys nothing and costs iterations",
        "controller": "nmpc_only",
    })


DEFAULT_NMPC_PARAMS = NMPCParams()

# (name, default, metadata) tuples in declaration order — the single source
# both the ROS2 declare_parameters() calls and control.launch.py's launch-arg
# generation build from, mirroring mpc_params.MPC_PARAM_FIELDS exactly.
NMPC_PARAM_FIELDS = tuple(
    (f.name, getattr(DEFAULT_NMPC_PARAMS, f.name), f.metadata)
    for f in fields(NMPCParams)
)


def declare_nmpc_params(node) -> None:
    """
    declare_parameters() every NMPCParams field on `node`, defaulting to
    DEFAULT_NMPC_PARAMS. Mirrors mpc_params.declare_mpc_params().
    """
    node.declare_parameters(
        namespace='',
        parameters=[(name, default) for name, default, _meta in NMPC_PARAM_FIELDS],
    )


def nmpc_params_from_node(node) -> NMPCParams:
    """
    Read back every NMPCParams field from `node`'s already-declared ROS2
    parameters into a fresh NMPCParams. Mirrors
    mpc_params.mpc_params_from_node() (bool/int fields use their ROS2-typed
    accessor; everything else is a plain float).
    """
    kwargs = {}
    for f in fields(NMPCParams):
        value = node.get_parameter(f.name).get_parameter_value()
        if f.type is bool:
            kwargs[f.name] = value.bool_value
        elif f.type is int:
            kwargs[f.name] = value.integer_value
        else:
            kwargs[f.name] = value.double_value
    return NMPCParams(**kwargs)

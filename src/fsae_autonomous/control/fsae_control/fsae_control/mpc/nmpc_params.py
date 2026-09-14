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
                "period, leaving the rest of the tick for the node. Checked in "
                "two places in compute(): before starting an SQP iteration, and "
                "before starting each backtracking line-search trial. The first "
                "check alone is a no-op at the shipped nmpc_sqp_iters=1 (that "
                "loop body always runs its one iteration to completion, so the "
                "check can only ever refuse to start it); the per-backtrack "
                "check is what actually bounds tick time in that configuration, "
                "since each trial re-rolls out the full horizon and dominates "
                "solve variance. Fixed 2026-09-14, see "
                "fsae_MPCTest/docs/logs/nmpc_low_speed_accel_stall_investigation.md.",
        "controller": "nmpc_only",
    })
    nmpc_rk_substeps: int = field(default=4, metadata={
        "unit": "substeps",
        "desc": "RK4 substeps per dt in the prediction rollout. Two separate "
                "stiff modes set this, and only the first was accounted for "
                "originally: tau_a=0.02 s against dt=0.05 s (lambda*dt = -2.5, "
                "near RK4's real-axis stability edge), which 2 substeps "
                "covers, AND the (v_y, r) lateral sub-dynamics, whose "
                "eigenvalues scale as 1/v_x and so get STIFFER as the car "
                "slows. At 2 substeps the rollout is outright unstable (not "
                "merely inaccurate) across roughly 2.25-3.5 m/s: an "
                "infinitesimal disturbance is amplified ~6e8 over a 20-stage "
                "horizon, so the PREDICTION itself is garbage and every "
                "line-search trial scores worse than the unstepped iterate, "
                "which freezes the controller at exactly zero steering/accel. "
                "4 decays cleanly over the whole 0.1-25 m/s envelope. "
                "CORRECTED 2026-09-15: an earlier version of this docstring "
                "claimed 3 substeps also fails at 2.50 m/s exactly -- a "
                "direct re-measurement (perturbation growth through this "
                "same _rollout, all 8 states individually perturbed, several "
                "control-sequence shapes) found 3 fully stable (<=1.6x "
                "growth) everywhere tested in and around that band; the "
                "original claim's basis is not reproduced. 3 is used above "
                "nmpc_rk_gate_speed via nmpc_rk_substeps_fast. This is the "
                "SAME stiffness mechanism as nmpc_jac_substeps below, but a "
                "distinct defect: that one corrupts the QP's step DIRECTION, "
                "this one corrupts the predicted TRAJECTORY the step is "
                "scored against, so raising jac_substeps alone does not fix "
                "it. See fsae_MPCTest/docs/logs/nmpc_low_speed_"
                "accel_stall_investigation.md",
        "controller": "nmpc_only",
    })

    nmpc_jac_substeps: int = field(default=4, metadata={
        "unit": "substeps",
        "desc": "RK4 substeps used when finite-differencing the QP's A_k/B_k "
                "sensitivities. Was 1 (coarser than nmpc_rk_substeps=2, on the "
                "assumption that a less-accurate Jacobian only costs a "
                "slightly worse SQP step direction) until the (v_y, r) "
                "sub-dynamics were found to go numerically UNSTABLE (not just "
                "less accurate) below ~6.5-7 m/s with only 1 substep -- RK4's "
                "stability limit is exceeded, the divergence compounds across "
                "the horizon's condensing loop, and the Hessian becomes so "
                "ill-conditioned that OSQP's only representable solution is "
                "exactly zero steering/accel, frozen once warm-started into "
                "that state. 4 is the validated fix: see "
                "fsae_MPCTest/docs/logs/nmpc_low_speed_accel_stall_"
                "investigation.md for the root-cause derivation, the "
                "substeps=1/2/4 comparison (2 is insufficient at 2.5-3.0 "
                "m/s), and the full closed-loop lap A/B (tracking improves, "
                "but mean solve time nearly doubles and p95 approaches the "
                "nmpc_solve_budget_ms=25ms deadline -- not yet measured on "
                "embedded/Jetson hardware, see GAP E2)",
        "controller": "nmpc_only",
    })
    nmpc_jac_gate_speed: float = field(default=8.0, metadata={
        "unit": "m/s",
        "desc": "below this speed (checked against the SLOWEST predicted stage "
                "in the horizon, not the instantaneous speed, so the gate "
                "changes rarely), _jacobians uses the full nmpc_jac_substeps. "
                "At or above it, nmpc_jac_substeps_fast is used instead. The "
                "jac_substeps=4 fix's own instability envelope (measured "
                "max|A_k| vs the converged value) shows the divergence is "
                "confined to low speed: 2.41e2 at 2.5 m/s but only 4.06 at "
                "8 m/s and 4.01 at 14 m/s (js=1 vs converged js=4), so the "
                "cost of the fix does not have to apply everywhere it was "
                "needed nowhere. An analytic Jacobian would not lower this "
                "floor either -- the variational equation shares RK4's "
                "stability region with the nominal ODE (verified: both "
                "diverge at the same lambda*dt), so the floor is inherent to "
                "RK4 sensitivity propagation at low speed, not to finite "
                "differencing. Set equal to a speed below the operating range "
                "to disable the gate (nmpc_jac_substeps_fast is then never "
                "read).",
        "controller": "nmpc_only",
    })
    nmpc_jac_substeps_fast: int = field(default=2, metadata={
        "unit": "substeps",
        "desc": "nmpc_jac_substeps used at/above nmpc_jac_gate_speed. 2 tracks "
                "the converged (4-substep) sensitivity closely with no "
                "divergence in that speed range (measured max|A_k| 3.07 vs "
                "3.18 at 8 m/s, 4.90 vs 4.93 at 14 m/s). 1 is NOT safe here "
                "despite not diverging: it is inaccurate rather than unstable "
                "at speed (1.30 vs a converged 3.85 at 10 m/s), which is a "
                "worse SQP step direction, not a fix. Set equal to "
                "nmpc_jac_substeps to disable the gate exactly.",
        "controller": "nmpc_only",
    })
    nmpc_rk_gate_speed: float = field(default=4.0, metadata={
        "unit": "m/s",
        "desc": "same technique as nmpc_jac_gate_speed, applied to the "
                "ROLLOUT itself (checked per predicted STAGE, not the whole "
                "horizon at once, since _rollout builds X incrementally and "
                "a stage's speed can cross the gate mid-horizon on a hard "
                "launch/brake). The rollout's instability is confined to a "
                "NARROWER band than the Jacobian's (measured stable, <=1.6x "
                "perturbation growth, at and above ~3.75 m/s vs the "
                "Jacobian's ~8 m/s), so this gate opens earlier.",
        "controller": "nmpc_only",
    })
    nmpc_rk_substeps_fast: int = field(default=3, metadata={
        "unit": "substeps",
        "desc": "nmpc_rk_substeps used at/above nmpc_rk_gate_speed. NOT 2: "
                "2 is the one substep count confirmed unstable (up to ~260x "
                "perturbation growth) in the 2.25-3.75 m/s band. 3 is fully "
                "converged (<=1.6x growth) everywhere measured at and above "
                "the gate speed, across all 8 states individually perturbed "
                "and several control-sequence shapes. Set equal to "
                "nmpc_rk_substeps to disable the gate exactly.",
        "controller": "nmpc_only",
    })

    # ── Standstill steering damping ─────────────────────────────────────
    # At v_x = 0 steering has NO physical effect (the kinematic branch gives
    # r_kin = v_x*tan(d)/L = 0, and the dynamic branch is blended out), but
    # the SQP's cost is summed over the WHOLE horizon, and the rolled-out
    # v_x profile leaves zero by stage 1 ([0, 0.118, 0.294, 0.465, ...]).
    # Nothing in the cost distinguishes "this stage cannot act yet" from
    # "this stage will act soon", so the optimiser pre-commits U[0] toward
    # whatever helps the later, physically-active stages. Measured live and
    # reproduced offline: steering ramps to ~-6.8 deg over the ~1 s before
    # the car physically moves, so it launches already turned and curves
    # sideways until the correction catches up.
    nmpc_standstill_steer_damp_enabled: bool = field(default=False, metadata={
        "desc": "damp the SQP's stage-0 steering effort while the car is "
                "measurably stationary, so it does not pre-commit a steering "
                "angle it cannot act on and then launch already turned. Only "
                "stage 0 is damped: the predicted v_x leaves zero by stage 1, "
                "so every later stage can genuinely act and its planning is "
                "left untouched, and U[0] is the only element actually "
                "shipped to the car.",
        "controller": "nmpc_only",
    })
    nmpc_standstill_speed: float = field(default=0.5, metadata={
        "unit": "m/s",
        "desc": "below this MEASURED speed (x0's own v_x, not a predicted "
                "stage), stage 0's steering effort weight is scaled by "
                "nmpc_standstill_steer_r_scale. Keyed on the measurement so "
                "the damping disengages the moment the car actually moves.",
        "controller": "nmpc_only",
    })
    nmpc_standstill_steer_r_scale: float = field(default=20.0, metadata={
        "desc": "multiplier on r_delta for stage 0 only, while below "
                "nmpc_standstill_speed. A weight sweep on the standstill "
                "reproduction gives pre-load -6.71 deg at 1x, -3.45 at ~3.7x, "
                "-1.03 at ~15x and -0.19 at ~74x, so 20x leaves a small "
                "residual rather than pinning steering to zero. This is a "
                "tuning value, not a derived constant: re-check it live "
                "rather than treating it as exact.",
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
    nmpc_publish_prediction_enabled: bool = field(default=False, metadata={
        "unit": "bool",
        "desc": "true -> convert the predicted horizon X to Cartesian (x,y) "
                "each tick and stash it on NMPCController.last_prediction_xy "
                "for the node to publish (RViz visualisation). Default false: "
                "skips the conversion entirely (visualisation-only, no effect "
                "on the solve) so there is no per-tick cost unless opted in.",
        "controller": "nmpc_only",
    })
    nmpc_publish_telemetry_enabled: bool = field(default=False, metadata={
        "unit": "bool",
        "desc": "true -> JSON-serialise NMPCController.last_telemetry (plus "
                "vx_source and the car's own pose) onto /fsae/viz/"
                "nmpc_telemetry each tick, for nmpc_telemetry_gui.py "
                "(GAP F1's stopgap: no other telemetry topic exists in this "
                "repo). Default false: skips the dict-copy/json.dumps entirely "
                "so there is no per-tick cost unless opted in, mirroring "
                "nmpc_publish_prediction_enabled's own convention.",
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

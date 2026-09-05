"""
Shared physical limits and current-state weight-shaping helpers that
nmpc_core.py needs from the LTV-QP controller (mpc_core.py) without pulling
in the LTV-QP controller itself.

fsae_autonomous does not carry mpc_core.py (it needs cvxpy/clarabel, which
this repo deliberately does not depend on -- osqp alone is enough for the
NMPC path). These 3 constants and 4 functions are copied verbatim from
ros2/src/fsae_planning/control/fsae_control/fsae_control/mpc/mpc_core.py
(the sim-side LTV-QP module) so nmpc_core.py's import surface is unchanged.
Keep byte-identical with that file's copies -- see CLAUDE.md's
"Planning/control parity" section. Do not edit the logic here without also
updating mpc_core.py's copy on the sim side.
"""

import math

import numpy as np

# Maximum physical steering deflection. 25deg matches this stack's limit
# (fsae_control.control_utils / fsds_bridge); upstream used 35deg.
MAX_STEER_RAD: float = math.radians(25.0)
MAX_ACCEL: float = 12.0
MAX_BRAKE: float = 7.0


def _steer_rate_anti_hunt(
    kappa: float,
    e_y: float,
    R_rate_base: np.ndarray,
    enabled: bool,
    e_psi: float = 0.0,
    boost_max: float = 6.0,
) -> np.ndarray:
    """
    TEMPORARY/EXPERIMENTAL, NOT VALIDATED: heavily penalise steering
    rate-of-change on top of _adaptive_R_rate's existing curvature softening,
    strongest when the car is centred (|e_y| small), well-aligned (|e_psi|
    small), AND not currently curving (kappa small). Mirrors
    model_utils.steer_rate_anti_hunt in fsae_MPCTest -- keep both constants
    in sync. enabled=False returns R_rate_base untouched.

    Continuous, not a hard AND-gated threshold: a discontinuous step would
    risk the same QP-solver-iteration-spike problem the
    enable_in_corners/kappa_straight history above already found from
    threshold cutoffs on curvature, so straight-line hunting is instead
    penalised more strongly via a higher continuous ceiling.
    boost_kappa, boost_ey, and boost_epsi each saturate independently
    toward 1.0 as their input shrinks toward 0 (same saturating-curve style
    as _adaptive_R_rate's own floor); their product is the applied scale,
    so the full boost_max (default MPCParams.anti_hunt_boost_max) only
    applies when all three are near their "straight, centred, and aligned"
    ideal, and it fades smoothly -- never snaps -- as any one of them
    grows.

    e_psi (radians, NOT the degrees used in telemetry/logging -- same units
    _error_state's x0[2]/e_psi already use internally) is included because
    without it, a car that enters a straight MISALIGNED (large |e_psi|,
    small |e_y| -- e.g. just exited a corner still pointed the wrong way)
    would get the full straight-line boost anyway, since kappa/e_y alone
    can't distinguish "straight and correctly aligned" from "straight but
    needs to yaw back into line" -- making exactly the correction it needs
    artificially expensive. k_epsi=23.0 sets half-fade at ~2.5 deg of e_psi.

    boost_kappa/boost_ey/boost_epsi are current-state signals only (no
    forward-scan term).
    """
    if not enabled:
        return R_rate_base
    # Relaxed 2026-08-19 (halved from 60.0/30.0/23.0): the original constants
    # faded the boost out too fast on genuinely gentle curves -- boost_kappa
    # was already down to ~0.45 by |kappa|=0.02 (a ~50 m-radius bend), so
    # R_rate[0,0] had mostly relaxed back toward baseline exactly where
    # residual steering jitter was still visible. Halving each k_* doubles
    # the |kappa|/|e_y|/|e_psi| each factor reaches before dropping to half
    # its max contribution (kappa: ~0.017 -> ~0.033 1/m; e_y: ~3.3 -> ~6.7 cm;
    # e_psi: ~2.5 -> ~5.0 deg). Applies to both controllers -- nmpc_core.py
    # imports this function verbatim, not a separate copy.
    k_kappa, k_ey, k_epsi = 30.0, 15.0, 11.5
    boost_kappa = 1.0 / (1.0 + k_kappa * abs(kappa))
    boost_ey    = 1.0 / (1.0 + k_ey * abs(e_y))
    boost_epsi  = 1.0 / (1.0 + k_epsi * abs(e_psi))
    scale = 1.0 + (boost_max - 1.0) * boost_kappa * boost_ey * boost_epsi
    R = R_rate_base.copy()
    R[0, 0] *= scale
    return R


def _reversal_penalty_boost(
    u_prev_steer: float,
    R_rate_base: np.ndarray,
    enabled: bool,
    boost_max: float = 4.0,
    k: float = 8.0,
) -> np.ndarray:
    """
    TEMPORARY/EXPERIMENTAL, NOT VALIDATED: soft constraint against steering
    REVERSALS (a tick-to-tick sign flip), approximated inside the convex QP
    by boosting R_rate[0,0] whenever LAST tick's steering command
    (u_prev_steer, rad) was already close to zero -- the one state a
    reversal must pass through, since delta_cmd is continuous. A reversal
    can't be detected directly inside one solve (it depends on this tick's
    OWN decision, the thing being optimised), so this penalises the
    precondition instead: the closer steering already sits to zero, the
    more it costs to change it further this tick, making a full sign flip
    specifically (as opposed to a same-side ramp toward/away from zero)
    disproportionately expensive relative to a swing of the same size made
    from a large starting angle.

    Same saturating-curve style as _steer_rate_anti_hunt (single input here,
    not a product of several) so it fades continuously rather than snapping,
    and composes the same way: applied multiplicatively on top of whatever
    _adaptive_R_rate/_steer_rate_anti_hunt/the corner blend already produced,
    never replacing them. enabled=False returns R_rate_base untouched.

    k=8.0 (rad^-1) sets half-boost at ~7.2 deg of PREVIOUS steering (a
    reversal starting from near-centre gets close to the full boost_max;
    one starting from a large existing angle -- already unlikely to flip
    sign in one 50ms tick without an equally large du -- is barely
    affected). Deliberately keyed on u_prev, not the CURRENT solve's u[0,0]
    (a QP variable): using the variable itself would make the cost
    non-convex (a rational function of the decision), whereas u_prev is a
    known constant by solve time, keeping this an ordinary quadratic term.
    """
    if not enabled:
        return R_rate_base
    boost_near_zero = 1.0 / (1.0 + k * abs(u_prev_steer))
    scale = 1.0 + (boost_max - 1.0) * boost_near_zero
    R = R_rate_base.copy()
    R[0, 0] *= scale
    return R


def _corner_factor(kappa: float, k: float) -> float:
    """
    0 (straight) -> 1 (full corner), a single continuous saturating curve
    of the CURRENT |kappa| (the ~1m-preview curvature _error_state already
    computes every tick, same signal _adaptive_R_rate/_steer_rate_anti_hunt
    use). Deliberately the SAME functional shape for both rising (entry)
    and falling (exit) curvature -- no separate decay-distance timer, no
    hysteresis state: this is a pure function of the current instantaneous
    signal, replacing the whole deleted lookahead approach/exit-boost
    family. k is MPCParams.corner_factor_k, the curve's sharpness.
    """
    return 1.0 - 1.0 / (1.0 + k * abs(kappa))


def _blend(straight_val: float, corner_val: float, corner_frac: float) -> float:
    """
    Simple linear interpolation from straight_val (corner_frac=0) to
    corner_val (corner_frac=1). Shared helper for every current-state
    Q/R_rate weight schedule -- see _corner_factor for how corner_frac
    itself is built.
    """
    return straight_val + (corner_val - straight_val) * corner_frac

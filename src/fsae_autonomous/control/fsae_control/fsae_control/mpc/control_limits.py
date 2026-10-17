"""
Physical limits and current-state weight-shaping helpers used by
nmpc_core.py.

Kept in their own module so the NMPC path depends only on osqp, with no
cvxpy/clarabel dependency.
"""

import math

import numpy as np

# Steering and acceleration limits are defaults from the simulated car model,
# UNVERIFIED for the real car. The go-kart overrides the steering limit via
# the node's plant_max_steer_deg parameter (see nmpc_controller.py and
# docs/NMPC_GOKART_GROUND_TEST.md). 25deg matches control_utils.MAX_STEER_RAD.
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
    small), AND not currently curving (kappa small). enabled=False returns
    R_rate_base untouched. Constants tuned in simulation; UNVERIFIED on the
    car or kart.

    Continuous, not a hard AND-gated threshold: a discontinuous step on
    curvature risks spikes in QP solver iterations, so straight-line
    hunting is instead penalised more strongly via a higher continuous
    ceiling.
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
    artificially expensive. k_epsi=11.5 sets half-fade at ~5.0 deg of e_psi.

    boost_kappa/boost_ey/boost_epsi are current-state signals only (no
    forward-scan term).
    """
    if not enabled:
        return R_rate_base
    # Each k_* sets where its factor drops to half its max contribution
    # (kappa: ~0.033 1/m, e_y: ~6.7 cm, e_psi: ~5.0 deg). Larger k_* fade the
    # boost out sooner, which relaxes R_rate[0,0] on gentle bends where
    # residual steering jitter can still appear. Tuned in simulation;
    # UNVERIFIED on the car or kart.
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
    signal. k is MPCParams.corner_factor_k, the curve's sharpness.
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

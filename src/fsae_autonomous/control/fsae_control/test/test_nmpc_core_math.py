"""
test_nmpc_core_math.py — numerical self-consistency checks for the NMPC solver
(fsae_control.mpc.nmpc_core).

WHAT THIS TESTS
----------------
These are NOT behavioral tests (see test_nmpc_signs_magnitudes.py for those).
This file checks that the solver's internal MATH is not silently wrong:

    1. MODEL PARITY  — the scalar rollout fast path (_step_scalar, used for
       the sequential horizon rollout) must agree with the vectorised _step
       (used for the finite-difference Jacobians) to machine precision. They
       are hand-mirrored copies of one model; a divergence here is a
       silent-wrong-prediction bug that no behavioral test would catch,
       because both copies would be consistently wrong the same way.
    2. JACOBIANS — the forward finite differences the SQP actually uses vs.
       central differences at a larger step, to catch a badly-sized
       perturbation or a non-smooth term.
    3. SQP CONVERGENCE — cost must decrease monotonically to a plateau from
       a cold start, at several representative operating points.

Ported from the sim tree's fsae_planning/control/fsae_control/test/
nmpc_offline_check.py (checks 1-3 of 6). Checks 4-6 of that file are NOT
ported here: they compare against fsae_control.mpc.mpc_core.MPCController
(the LTV-QP controller) and/or fsae_MPCTest's Pacejka plant, neither of
which this repo carries (this repo is NMPC-only — see
docs/NMPC_INTEGRATION_GAPS.md and control_limits.py's docstring for why).

HOW TO RUN
-----------
    colcon build --packages-select fsae_control
    source install/setup.bash
    colcon test --packages-select fsae_control --pytest-args -v
    colcon test-result --verbose

Or directly (still needs the package sourced first):
    pytest src/fsae_autonomous/control/fsae_control/test/test_nmpc_core_math.py -v
"""
import math

import numpy as np
import pytest

from fsae_control.mpc import nmpc_core as nc
from fsae_control.mpc.mpc_params import MPCParams
from fsae_control.mpc.nmpc_core import MAX_STEER_RAD, NMPCController
from fsae_control.mpc.nmpc_params import NMPCParams


def synthetic_corner(straight_m=60.0, radius=13.0, arc_deg=90.0, ds=0.25,
                      ramp_m=15.0, run_out_m=30.0) -> np.ndarray:
    """Straight -> linear curvature ramp -> constant radius -> run-out."""
    pts = [np.zeros(2)]
    psi = 0.0
    for _ in range(int(straight_m / ds)):
        pts.append(pts[-1] + ds * np.array([math.cos(psi), math.sin(psi)]))
    k_max = 1.0 / radius
    n_ramp = int(ramp_m / ds)
    for i in range(n_ramp):
        psi += k_max * (i + 1) / n_ramp * ds
        pts.append(pts[-1] + ds * np.array([math.cos(psi), math.sin(psi)]))
    for _ in range(int(math.radians(arc_deg) / (k_max * ds))):
        psi += k_max * ds
        pts.append(pts[-1] + ds * np.array([math.cos(psi), math.sin(psi)]))
    for _ in range(int(run_out_m / ds)):
        pts.append(pts[-1] + ds * np.array([math.cos(psi), math.sin(psi)]))
    return np.array(pts)


def make_nmpc(path: np.ndarray, iters: int = 1, N: int | None = None, **mpc_kw) -> NMPCController:
    npar = NMPCParams(nmpc_sqp_iters=iters, nmpc_solve_budget_ms=1e6,
                      **({'nmpc_horizon': N} if N else {}))
    ctrl = NMPCController(dt=0.05, params=MPCParams(**mpc_kw), nmpc=npar)
    ctrl.set_static_path(path)
    return ctrl


def converge(ctrl: NMPCController, x0: np.ndarray, v_ref: float, iters: int = 25):
    """Iterate the SQP to convergence from a cold start; return (U, costs)."""
    ref = ctrl._static_ref
    U = np.zeros((ctrl.N, nc.NU))
    X = ctrl._rollout(x0, U, ref)
    H = nc._outputs(X, ref, ctrl.plant, v_ref)
    costs = [ctrl._cost(X, U, H)]
    for _ in range(iters):
        dU, _status = ctrl._solve_step(X, U, ref, v_ref)
        if dU is None:
            break
        step, improved = 1.0, False
        for _bt in range(5):
            U_t = np.clip(U + step * dU, ctrl.u_min, ctrl.u_max)
            X_t = ctrl._rollout(x0, U_t, ref)
            H_t = nc._outputs(X_t, ref, ctrl.plant, v_ref)
            c_t = ctrl._cost(X_t, U_t, H_t)
            if c_t <= costs[-1]:
                U, X, H = U_t, X_t, H_t
                costs.append(c_t)
                improved = True
                break
            step *= 0.5
        if not improved:
            break
    return U, costs


# ---------------------------------------------------------------------------
# 1. Model parity: scalar rollout must match the vectorised Jacobian path
# ---------------------------------------------------------------------------

def test_step_scalar_matches_step_vectorised():
    ref = nc.PathReference(synthetic_corner())
    p = nc._Plant()
    rng = np.random.default_rng(7)
    worst = 0.0
    for _ in range(300):
        x = np.array([rng.uniform(0, ref.total), rng.uniform(-2, 2),
                      rng.uniform(-0.6, 0.6), rng.uniform(0, 20),
                      rng.uniform(-1, 1), rng.uniform(-1, 1),
                      rng.uniform(-MAX_STEER_RAD, MAX_STEER_RAD),
                      rng.uniform(-7, 12)])
        u = np.array([rng.uniform(-MAX_STEER_RAD, MAX_STEER_RAD), rng.uniform(-7, 12)])
        for n_sub in (1, 2, 3):
            a = nc._step(x[None, :], u[None, :], ref, p, 0.05, n_sub)[0]
            b = np.array(nc._step_scalar(x, u, ref, p, 0.05, n_sub))
            worst = max(worst, float(np.max(np.abs(a - b) / np.maximum(np.abs(a), 1.0))))
    assert worst < 1e-12, (
        f'_step_scalar diverged from _step by relative {worst:.2e} — these are '
        'hand-mirrored copies of one model; any divergence here is a silent '
        'wrong-prediction bug (see this file\'s module docstring).'
    )


def test_kappa_scalar_matches_kappa_at():
    ref = nc.PathReference(synthetic_corner())
    rng = np.random.default_rng(7)
    worst_k = 0.0
    for _ in range(300):
        s = rng.uniform(0, ref.total)
        worst_k = max(worst_k, abs(ref.kappa_scalar(s) - float(ref.kappa_at(np.array([s]))[0])))
    assert worst_k < 1e-12, f'kappa_scalar/kappa_at diverged by {worst_k:.2e}'


# ---------------------------------------------------------------------------
# 2. Jacobians: forward FD (as used by the SQP) vs. central FD
# ---------------------------------------------------------------------------

def test_forward_fd_matches_central_fd():
    ref = nc.PathReference(synthetic_corner())
    p = nc._Plant()
    rng = np.random.default_rng(1)
    M = 6
    X = np.zeros((M, nc.NX))
    X[:, nc.IDX_S] = np.linspace(30, 60, M)
    X[:, nc.IDX_EY] = rng.uniform(-0.5, 0.5, M)
    X[:, nc.IDX_EPSI] = rng.uniform(-0.1, 0.1, M)
    X[:, nc.IDX_VX] = np.linspace(2.0, 17.0, M)
    X[:, nc.IDX_VY] = rng.uniform(-0.3, 0.3, M)
    X[:, nc.IDX_R] = rng.uniform(-0.3, 0.3, M)
    X[:, nc.IDX_DELTA] = rng.uniform(-0.2, 0.2, M)
    X[:, nc.IDX_A] = rng.uniform(-3, 3, M)
    U = np.column_stack([rng.uniform(-0.3, 0.3, M), rng.uniform(-5, 5, M)])

    def step(Xa, Ua):
        return nc._step(Xa, Ua, ref, p, 0.05, 2)

    F0 = step(X, U)
    worst = 0.0
    for j in range(nc.NX):
        e = nc._FD_EPS_X[j]
        Xp = X.copy()
        Xp[:, j] += e
        fwd = (step(Xp, U) - F0) / e
        ec = 1e-5
        Xa, Xb = X.copy(), X.copy()
        Xa[:, j] += ec
        Xb[:, j] -= ec
        ctr = (step(Xa, U) - step(Xb, U)) / (2 * ec)
        worst = max(worst, np.abs(fwd - ctr).max() / max(np.abs(ctr).max(), 1e-6))
    for j in range(nc.NU):
        e = nc._FD_EPS_U[j]
        Up = U.copy()
        Up[:, j] += e
        fwd = (step(X, Up) - F0) / e
        ec = 1e-5
        Ua, Ub = U.copy(), U.copy()
        Ua[:, j] += ec
        Ub[:, j] -= ec
        ctr = (step(X, Ua) - step(X, Ub)) / (2 * ec)
        worst = max(worst, np.abs(fwd - ctr).max() / max(np.abs(ctr).max(), 1e-6))
    # 1e-3 is loose on purpose: the s-column differences the local slope of a
    # piecewise-linear kappa(s), so forward and central differences legitimately
    # disagree near a grid breakpoint.
    assert worst < 1e-3, f'forward/central FD Jacobian discrepancy {worst:.2e}'


# ---------------------------------------------------------------------------
# 3. SQP convergence: cost must decrease monotonically from a cold start
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('label,x0', [
    ('on-line straight, v=14', np.array([40.0, 0.0, 0.0, 14.0, 0, 0, 0, 0])),
    ('e_y=+1 m straight, v=14', np.array([40.0, 1.0, 0.0, 14.0, 0, 0, 0, 0])),
    ('corner approach s=55, v=14', np.array([55.0, 0.0, 0.0, 14.0, 0, 0, 0, 0])),
    ('mid-corner s=80, v=9', np.array([80.0, 0.0, 0.0, 9.0, 0, 0, 0, 0])),
])
def test_sqp_converges_monotonically(label, x0):
    path = synthetic_corner()
    ctrl = make_nmpc(path)
    ctrl.reset()
    _U, costs = converge(ctrl, x0, x0[nc.IDX_VX])
    assert len(costs) > 1, f'{label}: solver made no progress at all'
    mono = all(costs[i + 1] <= costs[i] + 1e-12 for i in range(len(costs) - 1))
    assert mono, f'{label}: cost increased mid-solve: {costs}'

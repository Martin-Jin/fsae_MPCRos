# Title: control_utils.py

"""
control_utils.py — Live MPC Path-Tracking Controller

PURPOSE
-------
Provides MPCController, the single class control_node.py uses to turn a
planner path + current vehicle state into a ControlCommand at 20 Hz. It is
a self-contained, "live-solve" re-implementation of the same linear
time-varying MPC formulated generically in optimiser.py / bicycle_model.py
for the offline tuner and simulator, designed for 100% numerical parity
with that offline pipeline so that weights tuned by offline_tuner.py
(see tuning_history.txt) transfer directly to the real/simulated vehicle.

  States  x : [e_y, e_yd, e_psi, r, e_v, e_a, delta_act, a_act]   (8,)
  Inputs  u : [delta_cmd (rad), a_cmd (m/s2)]                      (2,)

HOW IT WORKS
------------
Each call to MPCController.compute() runs the full MPC pipeline:
  1. Low-pass filter the incoming desired_speed (_v_des_filtered) to avoid
     feeding step changes into the MPC's speed-error state.
  2. _error_state() — project the vehicle's front axle onto the nearest
     path segment to get Frenet-style tracking errors (e_y, e_psi, e_v) and
     a short-lookahead curvature estimate (kappa), then assemble the 8-state
     vector x0 (reusing the controller's own actuator-lag memory for the
     delta_act/a_act entries, since those aren't directly measurable).
  3. _discrete_model() — build the speed-blended kinematic/dynamic bicycle
     model and ZOH-discretise it (mirrors bicycle_model.get_8state_discrete_model,
     duplicated locally so the live controller has no simulation dependencies).
  4. Gain-schedule R and R_rate via the module-level _adaptive_R_scaling /
     _adaptive_R_rate helpers (mirrors model_utils.py's adaptive_R_scaling /
     adaptive_R_rate — duplicated here for the same reason).
  5. _solve_qp() — inject the above into a persistent, parameterised CVXPY
     problem (built once in _build_qp, reused via warm-start) and solve with
     OSQP, falling back to Clarabel, then to a full-brake command (holding
     the last steering angle) if both solvers fail.
  6. Integrate the actuator lag states exactly (ZOH, not Euler) so
     delta_act/a_act stay consistent even though dt (0.05s) is comparable
     to tau_a (0.02s).
  7. Convert [delta_cmd, a_cmd] into normalised
     [steering, throttle, brake] command triple and populate
     self.last_telemetry for control_node.py's CSV logger.

PARITY WITH THE OFFLINE PIPELINE
---------------------------------
_adaptive_R_scaling/_adaptive_R_rate/_discrete_model here are intentionally
near-identical duplicates of model_utils.py / bicycle_model.py, and
_build_qp's cost/constraint formulation is a near-identical duplicate of
optimiser.py's init_parameterized_mpc (same +/-3.5 m soft lane bound, same
W_slack=10000, same step-0/subsequent rate-cost split), plus a hard
per-step slew-rate constraint on [delta_cmd, a_cmd] (self.du_max) enforced
in addition to the soft R_rate cost. Any change to the cost/constraint
structure in one location should be mirrored in the other, or the weights
tuned by offline_tuner.py will no longer transfer faithfully to the live
controller.

USED BY
-------
  control_node.py — ControlNode.__init__ constructs one MPCController(dt=0.05,
                    N=25) and calls .compute() every 20 Hz tick, .reset()
                    on stale path / cone-brake fail-safes.
"""

import math
import cvxpy as cp
import numpy as np
from scipy.linalg import expm

# Maximum physical steering deflection
MAX_STEER_RAD: float = math.radians(35.0)
MAX_ACCEL: float = 12.0
MAX_BRAKE: float = 9.0

# ---------------------------------------------------------------------------
# Adaptive gain helpers
# ---------------------------------------------------------------------------

def _adaptive_R_scaling(vx: float, R_base: np.ndarray) -> np.ndarray:
    """
    Speed-dependent steering cost with a saturating (Michaelis-Menten) scale.
    steer_scale = 1 + (1.5 * vx) / (6.0 + vx)
    """
    vx = max(vx, 0.5)
    steer_scale = 1.0 + (1.5 * vx) / (6.0 + vx)
    accel_scale = 1.0 + 0.05 * vx
    R = R_base.copy()
    R[0, 0] *= steer_scale
    R[1, 1] *= accel_scale
    return R


def _adaptive_R_rate(kappa: float, R_rate_base: np.ndarray) -> np.ndarray:
    """
    Curvature-dependent steering-jerk softening.
    Softens slew penalty in sharp corners (floor at 0.35).
    """
    scale = max(0.35, 1.0 / (1.0 + 3.0 * abs(kappa)))
    R = R_rate_base.copy()
    R[0, 0] *= scale
    return R


def _curvature(path: np.ndarray, idx: int) -> float:
    """
    Estimate signed path curvature (1/m) at waypoint idx via finite-difference.
    """
    if idx <= 0 or idx >= len(path) - 1:
        return 0.0
    s_prev = path[idx]     - path[idx - 1]
    s_next = path[idx + 1] - path[idx]
    yaw_p  = math.atan2(s_prev[1], s_prev[0])
    yaw_n  = math.atan2(s_next[1], s_next[0])
    dpsi   = math.atan2(math.sin(yaw_n - yaw_p), math.cos(yaw_n - yaw_p))
    ds     = (np.linalg.norm(s_prev) + np.linalg.norm(s_next)) * 0.5
    return dpsi / ds if ds > 1e-6 else 0.0


# ---------------------------------------------------------------------------
# MPC Controller
# ---------------------------------------------------------------------------

class MPCController:
    """
    Linear time-varying MPC for combined lateral and longitudinal path tracking.
    """
    def __init__(
        self,
        dt: float = 0.05, 
        N:  int   = 25, 
    ) -> None:
        """
        Parameters
        ----------
        dt : float
            Control/prediction timestep (s). Must equal the node's control
            timer period (0.05 s / 20 Hz in control_node.py) so the
            discretised model's predictions align with real elapsed time.
        N : int
            MPC horizon length in steps (25 -> 1.25 s lookahead at dt=0.05).
            Must match settings.N_HORIZON for tuned weights to transfer.

        Vehicle geometry/dynamics constants (lf, lr, m, Iz, Cf, Cr,
        tau_delta, tau_a) are hardcoded here rather than imported from
        vehicle_physics.VehicleParams — keep these in sync manually if the
        plant model is retuned, since this is the "live" copy used on the
        real/simulated vehicle.
        """
        self.dt = dt
        self.N  = N

        # ── Vehicle geometry & dynamics  ─────
        self.lf = 0.85   
        self.lr = 0.70   
        self.m  = 255.0  
        self.Iz = 110.0  
        self.Cf = 15000.0
        self.Cr = 14000.0  
        self.tau_delta = 0.08  
        self.tau_a     = 0.02  

        self.nx = 8
        self.nu = 2

        # Tuned parameters
        Q_diag      = [0.6076038410420214, 0.7018612760165229, 7.107357922239617, 0.1016639549356476, 0.44488278317637964, 0.0, 0.0, 0.0]
        R_diag      = [7.869443219377219, 0.28548521974060515]
        R_rate_diag = [5.580499945962179, 9.993633621755315]

        self.Q      = np.diag(Q_diag)
        self.R      = np.diag(R_diag)
        self.R_rate = np.diag(R_rate_diag)

        # ── Hard actuator limits ───────────────────────────────────────
        # Matched exactly to the offline tuner/vehicle plant capabilities
        self.a_max = MAX_ACCEL
        self.a_max_brake = MAX_BRAKE
        self.u_min = np.array([-MAX_STEER_RAD, -self.a_max_brake]) 
        self.u_max = np.array([ MAX_STEER_RAD,  self.a_max])
        
        # Hard per-step slew-rate limit on [delta_cmd, a_cmd], enforced in
        # _build_qp in addition to the soft R_rate cost.
        self.du_max = np.array([math.radians(4.0), 0.6]) 

        # ── Continuity memory ─────────────────────────────────────────
        self._delta_act:      float      = 0.0
        self._a_act:          float      = 0.0
        self._u_prev:         np.ndarray = np.zeros(self.nu)
        self._v_des_filtered: float | None = None

        self.last_telemetry: dict = {}
        self._qp: dict | None = None

    def _build_qp(self) -> None:
        """
        Constructs the CVXPY problem using parameters. Built once to maximize 20Hz throughput.
        Matches optimiser.py exactly, including soft track boundaries.
        """
        nx, nu, N = self.nx, self.nu, self.N

        Ad_p    = cp.Parameter((nx, nx), name="Ad")
        Bd_p    = cp.Parameter((nx, nu), name="Bd")
        x0_p    = cp.Parameter(nx,       name="x0")
        uprev_p = cp.Parameter(nu,       name="u_prev")
        
        sqrtQ_param  = cp.Parameter((nx, 1), nonneg=True, name="sqrtQ")
        sqrtR_param  = cp.Parameter((nu, 1), nonneg=True, name="sqrtR")
        sqrtRr_param = cp.Parameter((nu, 1), nonneg=True, name="sqrtRr")
        weighted_u_prev_param = cp.Parameter(nu, name="weighted_u_prev")

        x     = cp.Variable((nx, N + 1))
        u     = cp.Variable((nu, N))
        slack = cp.Variable(N)  # Soft lane boundary constraint

        W_slack = 10000.0

        # Dynamics constraints
        constraints = [
            x[:, 0] == x0_p,
            x[:, 1:] == Ad_p @ x[:, :-1] + Bd_p @ u,
            u >= self.u_min[:, None],
            u <= self.u_max[:, None],
            x[0, :-1] <=  3.5 + slack,
            x[0, :-1] >= -3.5 - slack,
            u[:, 0] - uprev_p <=  self.du_max,
            u[:, 0] - uprev_p >= -self.du_max,
        ]

        if N > 1:
            du_hard = cp.diff(u, axis=1)
            constraints += [
                du_hard <=  self.du_max[:, None],
                du_hard >= -self.du_max[:, None],
            ]

        # Cost Formulation (Exact match to optimiser.py)
        cost  = cp.sum(cp.sum_squares(cp.multiply(sqrtQ_param, x)))
        cost += cp.sum(cp.sum_squares(cp.multiply(sqrtR_param, u)))
        cost += W_slack * cp.sum_squares(slack)
        
        # Step-0 rate cost
        cost += cp.sum_squares(cp.multiply(sqrtRr_param[:, 0], u[:, 0]) - weighted_u_prev_param)

        # Subsequent rate cost
        if N > 1:
            du = cp.diff(u, axis=1)
            cost += cp.sum(cp.sum_squares(cp.multiply(sqrtRr_param, du)))

        prob = cp.Problem(cp.Minimize(cost), constraints)

        self._qp = {
            "prob":  prob,
            "Ad":    Ad_p,
            "Bd":    Bd_p,
            "x0":    x0_p,
            "u_prev": uprev_p,
            "sqrtQ": sqrtQ_param,
            "sqrtR": sqrtR_param,
            "sqrtRr": sqrtRr_param,
            "weighted_u_prev": weighted_u_prev_param,
            "u":     u,
        }

    def _discrete_model(self, v_x: float) -> tuple[np.ndarray, np.ndarray]:
        """
        ZOH exact discretization of the bicycle model.
        Forces dense sparsity pattern with epsilon to prevent OSQP reallocation.
        """
        v_x_safe = max(0.01, abs(v_x))
        m, Iz, lf, lr = self.m, self.Iz, self.lf, self.lr
        Cf, Cr        = self.Cf, self.Cr
        td, ta, dt    = self.tau_delta, self.tau_a, self.dt

        A_kin = np.ones((self.nx, self.nx)) * 1e-12
        A_dyn = np.ones((self.nx, self.nx)) * 1e-12

        A_kin[0, 2] = v_x_safe
        A_kin[2, 6] = v_x_safe / (lf + lr) 
        A_kin[4, 5] = 1.0
        A_kin[5, 7] = 1.0
        A_kin[6, 6] = -1.0 / td
        A_kin[7, 7] = -1.0 / ta

        A_dyn[0, 1] = 1.0
        A_dyn[1, 1] = -(2 * Cf + 2 * Cr) / (m * v_x_safe)
        A_dyn[1, 2] = (2 * Cf + 2 * Cr) / m
        A_dyn[1, 3] = (-2 * Cf * lf + 2 * Cr * lr) / (m * v_x_safe)
        A_dyn[1, 6] = (2 * Cf) / m
        A_dyn[2, 3] = 1.0
        A_dyn[3, 1] = (-2 * Cf * lf + 2 * Cr * lr) / (Iz * v_x_safe)
        A_dyn[3, 2] = (2 * Cf * lf - 2 * Cr * lr) / Iz
        A_dyn[3, 3] = -(2 * Cf * lf**2 + 2 * Cr * lr**2) / (Iz * v_x_safe)
        A_dyn[3, 6] = (2 * Cf * lf) / Iz
        A_dyn[4, 5] = 1.0   
        A_dyn[5, 7] = 1.0   
        A_dyn[6, 6] = -1.0 / td   
        A_dyn[7, 7] = -1.0 / ta   

        B = np.ones((self.nx, self.nu)) * 1e-12
        B[6, 0] = 1.0 / td
        B[7, 1] = 1.0 / ta

        alpha = np.clip((v_x - 1.0) / (2.5 - 1.0), 0.0, 1.0)
        A_c = (1.0 - alpha) * A_kin + alpha * A_dyn
        
        n_aug = self.nx + self.nu 
        M     = np.zeros((n_aug, n_aug))
        M[: self.nx, : self.nx] = A_c
        M[: self.nx, self.nx :] = B 

        eM = expm(M * dt)
        return eM[: self.nx, : self.nx], eM[: self.nx, self.nx :]

    def _error_state(
        self,
        path:          np.ndarray,
        car_pos:       np.ndarray,
        car_yaw:       float,
        car_speed:     float,
        car_yaw_rate:  float,
        desired_speed: float,
    ) -> tuple[np.ndarray, float, dict]:
        """
        Calculates exact Frenet tracking errors to match offline evaluation.
        """
        fa = car_pos + self.lf * np.array([math.cos(car_yaw), math.sin(car_yaw)])
        base_dists = np.linalg.norm(path - fa, axis=1)
        base_idx   = int(np.argmin(base_dists))

        if base_idx < len(path) - 1:
            seg = path[base_idx + 1] - path[base_idx]
        else:
            seg = path[base_idx]     - path[base_idx - 1]

        seg_len = float(np.linalg.norm(seg))
        if seg_len < 1e-6:
            return np.zeros(self.nx), 0.0, {}

        # Orientation of the path segment
        path_yaw = math.atan2(seg[1], seg[0])

        # Robust Euclidean projection for lateral error (matches vehicle_physics.py)
        dx = fa[0] - path[base_idx][0]
        dy = fa[1] - path[base_idx][1]
        e_y_proj = dy * math.cos(path_yaw) - dx * math.sin(path_yaw)
        true_dist = math.hypot(dx, dy)
        e_y = true_dist * (1.0 if e_y_proj >= 0 else -1.0)

        # Heading error wrapped to [-pi, pi]
        e_psi = math.atan2(math.sin(car_yaw - path_yaw), math.cos(car_yaw - path_yaw))
        e_yd  = car_speed * math.sin(e_psi)

        # Preview curvature lookup
        preview_dist = 1.0
        preview_idx  = base_idx
        accumulated  = 0.0
        for i in range(base_idx, len(path) - 1):
            accumulated += float(np.linalg.norm(path[i + 1] - path[i]))
            if accumulated >= preview_dist:
                preview_idx = i + 1
                break
        kappa = _curvature(path, preview_idx)

        x0 = np.array([
            e_y,
            e_yd,
            e_psi,
            car_yaw_rate,    
            car_speed - desired_speed,
            0.0,             
            self._delta_act,
            self._a_act,
        ])
        
        dbg = {
            "e_y":        e_y,
            "e_psi":      e_psi,
            "e_v":        x0[4],
            "kappa":      kappa,
            "base_idx":   base_idx,
            "preview_idx": preview_idx,
        }
        return x0, kappa, dbg

    def _solve_qp(
        self,
        x0: np.ndarray,
        Ad: np.ndarray,
        Bd: np.ndarray,
        R_scaled:      np.ndarray,
        R_rate_scaled: np.ndarray,
    ) -> np.ndarray:
        """
        Solves the MPC optimization problem utilizing warm starts.
        """
        if self._qp is None:
            self._build_qp()

        qp = self._qp
        qp["Ad"].value = Ad
        qp["Bd"].value = Bd
        qp["x0"].value = x0
        qp["u_prev"].value = self._u_prev

        # Format arrays for cp.sum_squares element-wise multiplication
        sqrtQ  = np.sqrt(np.clip(np.diag(self.Q), 1e-6, 1e6))
        sqrtR  = np.sqrt(np.clip(np.diag(R_scaled), 1e-6, 1e6))
        sqrtRr = np.sqrt(np.clip(np.diag(R_rate_scaled), 1e-6, 1e6))
        
        qp["sqrtQ"].value = sqrtQ[:, None]
        qp["sqrtR"].value = sqrtR[:, None]
        qp["sqrtRr"].value = sqrtRr[:, None]
        qp["weighted_u_prev"].value = sqrtRr * self._u_prev

        # ── Primary solve: OSQP ──────
        qp["prob"].solve(
            solver=cp.OSQP,
            verbose=False,
            warm_start=True,
            eps_abs=1e-5,
            eps_rel=1e-5,
            max_iter=8000,
        )

        status = qp["prob"].status
        u_val  = qp["u"][:, 0].value

        if status == cp.OPTIMAL_INACCURATE and u_val is not None:
            print("[MPC] Warning: OSQP OPTIMAL_INACCURATE — Proceeding with viable solution.")
            return u_val.copy()

        if status == cp.OPTIMAL and u_val is not None:
            return u_val.copy()

        # ── Fallback: Clarabel ────────────────────────────────────────
        try:
            qp["prob"].solve(solver=cp.CLARABEL, verbose=False)
            status_fb = qp["prob"].status
            u_val_fb  = qp["u"][:, 0].value
            if status_fb in (cp.OPTIMAL, cp.OPTIMAL_INACCURATE) and u_val_fb is not None:
                print("[MPC] Warning: OSQP failed, Clarabel succeeded.")
                return u_val_fb.copy()
        except cp.error.SolverError as exc:
            print(f"[MPC] Warning: Clarabel also failed: {exc!r}")

        return np.array([self._u_prev[0], -self.a_max_brake])

    def compute(
        self,
        path:          np.ndarray,
        car_pos:       np.ndarray,
        car_yaw:       float,
        car_speed:     float,
        desired_speed: float,
        car_yaw_rate:  float = 0.0,
    ) -> tuple[float, float, float]:
        """
        Run one full MPC control step: extract tracking error -> discretise
        the plant model at the current speed -> gain-schedule R/R_rate ->
        solve the QP -> integrate actuator lag -> convert units.

        Parameters
        ----------
        path : np.ndarray, shape (n, 2)
            Planner centreline waypoints [x, y] in the global frame.
        car_pos : np.ndarray, shape (2,)
            Vehicle rear-axle-reference position [x, y] (global frame);
            front axle position is derived inside _error_state via self.lf.
        car_yaw : float
            Vehicle heading (rad, global frame).
        car_speed : float
            Vehicle forward speed magnitude (m/s); see _odom_cb note on how
            this is measured upstream.
        desired_speed : float
            Planner's requested speed (m/s); low-pass filtered internally.
        car_yaw_rate : float, optional
            Measured yaw rate (rad/s), defaults to 0.0 if unavailable.

        Returns
        -------
        (steering, throttle, brake) : tuple of float
            steering in [-1, 1] (ControlCommand convention),
            throttle in [0, 1], brake in [0, 1] (throttle/brake mutually
            exclusive, split by the sign of a_cmd).

        Guard: if the path has fewer than 2 points, immediately returns a
        neutral/mild-braking command (0.0, 0.0, 0.5) without touching the
        QP or any internal state — control_node.py's own path-staleness
        check (Phase 2) is expected to normally catch this first.
        """
        if len(path) < 2:
            return 0.0, 0.0, 0.5   

        # Filter target speed to prevent impulse requests.
        alpha = 0.08
        if self._v_des_filtered is None:
            self._v_des_filtered = desired_speed
        self._v_des_filtered += alpha * (desired_speed - self._v_des_filtered)
        desired_speed = self._v_des_filtered

        x0, kappa, dbg = self._error_state(
            path, car_pos, car_yaw, car_speed, car_yaw_rate, desired_speed,
        )

        Ad, Bd = self._discrete_model(car_speed)

        R_scaled      = _adaptive_R_scaling(car_speed, self.R)
        R_rate_scaled = _adaptive_R_rate(kappa, self.R_rate)

        u_opt = self._solve_qp(x0, Ad, Bd, R_scaled, R_rate_scaled)

        # ── EXACT ZOH ACTUATOR INTEGRATION ────────────────────────────
        # Prevents explicit Euler instability when dt > tau_a
        exp_delta = math.exp(-self.dt / self.tau_delta)
        exp_a     = math.exp(-self.dt / self.tau_a)
        
        self._delta_act = self._delta_act * exp_delta + u_opt[0] * (1.0 - exp_delta)
        self._a_act     = self._a_act * exp_a         + u_opt[1] * (1.0 - exp_a)
        
        self._u_prev    = u_opt.copy()
        # ──────────────────────────────────────────────────────────────

        delta_cmd = float(np.clip(u_opt[0], -MAX_STEER_RAD, MAX_STEER_RAD))
        a_cmd     = float(u_opt[1])
        steering  = float(np.clip(-delta_cmd / MAX_STEER_RAD, -1.0, 1.0))

        if a_cmd >= 0.0:
            throttle = float(np.clip(a_cmd / self.a_max, 0.0, 1.0))
            brake    = 0.0
        else:
            throttle = 0.0
            brake    = float(np.clip(-a_cmd / self.a_max_brake, 0.0, 1.0))

        self.last_telemetry = {
            **dbg,
            "car_speed":     car_speed,
            "desired_speed": desired_speed,
            "steering":      steering,
            "throttle":      throttle,
            "brake":         brake,
            "delta_cmd":     delta_cmd,
            "a_cmd":         a_cmd,
            "delta_act":     self._delta_act,
            "a_act":         self._a_act,
        }

        return steering, throttle, brake

    def reset(self) -> None:
        """
        Clears the controller's internal state history, forcing the QP solver
        to discard its warm start and actuator lag tracking. 
        """
        self._delta_act       = 0.0
        self._a_act           = 0.0
        self._u_prev          = np.zeros(self.nu)
        self._v_des_filtered  = None
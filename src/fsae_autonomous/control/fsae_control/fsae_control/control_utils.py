# Title: control_utils.py

"""
control_utils.py — The steering/speed "brain" for the car

WHAT THIS FILE DOES
--------------------
This file defines MPCController, the class that decides how much to steer,
how much to accelerate, and how much to brake, so the car follows the path
it has been given. mpc_controller.py (the ROS node) calls this class once
every time a new car-position update arrives, feeds it the current path and
the car's current position/speed/heading, and gets back a steering command
and a throttle/brake command.

"MPC" stands for Model Predictive Control. In plain terms: instead of just
reacting to where the car is *right now* (like a simple "steer toward the
path" rule would), this controller keeps a rough internal model of how the
car moves, and uses it to look roughly a second and a quarter into the
future. It asks "if I do this steering/throttle now, and roughly this for
the next dozen or so ticks, where does that leave me?", tries out many such
plans very quickly, and picks the one that stays closest to the path while
also being smooth on the steering wheel and pedals. It then only *acts* on
the very first step of that plan — and repeats this whole "look ahead and
pick a plan" process again on the next tick, using the new sensor data. Each
call to compute() is one full instance of this look-ahead-and-decide cycle.

  Internal tracking values (8 numbers), used to work out how "off track"
  the car currently is:
    [sideways offset from path, rate of change of that offset,
     heading error, current turn rate, speed error,
     (unused speed-error-rate slot), current steering-actuator lag state,
     current accel-actuator lag state]

  Commands MPC decides on each tick (2 numbers):
    [steering angle command (radians), acceleration command (m/s^2)]

STEP BY STEP: WHAT compute() DOES EACH TICK
---------------------------------------------
  1. Smooth the requested speed. If the target speed suddenly jumps (e.g.
     the planner asks for a very different speed from one tick to the
     next), this softens that jump with a simple running-average filter so
     the car doesn't lurch.
  2. Work out how far off-track the car currently is (_error_state()):
     project the car's front-axle position onto the nearest point of the
     given path to get a sideways offset and a heading error, and take a
     short look ahead along the path to estimate how sharp the upcoming
     turn is (see "curvature preview" below).
  3. Build a short-term model of how the car responds to steering and
     acceleration at the current speed (_discrete_model()) — see "why two
     driving styles" below.
  4. Loosen or tighten the smoothness penalties depending on current speed
     and how sharp the upcoming corner is, so the car can react faster
     through hairpins without being twitchy on straights.
  5. Hand all of that to an optimizer (_solve_qp()) that searches for the
     best steering/accel plan over the lookahead window, and solves it with
     a fast numerical solver (OSQP), falling back to a second solver
     (Clarabel), and if both of those fail, falling back to a safe "hold
     the last steering angle and brake" command so the car never does
     something wild.
  6. Update its internal memory of what the steering/accel actuators are
     probably doing right now (see "why actuator lag matters" below).
  7. Convert the raw steering angle (radians) and acceleration (m/s^2) into
     the normalized [-1,1] steering / [0,1] throttle / [0,1] brake values
     that the rest of the stack expects, and save some diagnostic numbers
     to self.last_telemetry for logging/debugging.

A FEW TERMS EXPLAINED
-----------------------
- **Sideways offset / heading error**: instead of describing the car with a
  raw (X, Y) map coordinate, the controller describes it as "how far along
  the path am I" plus "how far to the side of the path am I, and how many
  degrees off is my heading from the path's direction". This is much more
  directly useful for a controller whose whole job is "stay on this line"
  than a plain map coordinate would be.
- **Why two driving styles ("kinematic" vs "dynamic") get blended**: at
  very low speed (e.g. crawling into a hairpin), the car turns almost like
  a shopping trolley — steering angle alone predicts the turn well. At
  higher speed, how much grip the tires have starts to matter more than
  geometry alone. Rather than switching abruptly between two different
  internal models as speed crosses some threshold (which would cause a
  jolt in the commands), this controller smoothly blends between the two
  based on current speed.
- **Curvature preview**: a short look-ahead along the given path, used to
  estimate how sharp the upcoming turn is. This lets the controller soften
  or tighten its steering effort *before* the car is already mid-corner,
  rather than only reacting once it's already there.
- **Why actuator lag matters**: on a real car, the steering motor and the
  throttle/brake system don't respond instantly to a command — there's a
  short delay before the actual angle/acceleration catches up to what was
  requested. This controller keeps a running internal estimate of that lag
  (`_delta_act` for steering, `_a_act` for acceleration) so its predictions
  about "where will the car be in a second" account for that delay instead
  of assuming instant response.
- **Why the actuator state isn't measured directly**: this stack doesn't
  have a sensor that reports the steering system's actual angle or the
  drivetrain's actual acceleration back to this node, so the controller
  estimates both internally by simulating how those actuators respond over
  time, rather than reading them from a live source. If a real steering-
  angle or acceleration sensor is ever added to this stack, that measured
  value should replace this internal estimate for better accuracy.

TUNING WEIGHTS
---------------
The numbers in Q_diag / R_diag / R_rate_diag below control how strongly the
controller penalizes being off-path vs. penalizing aggressive steering/
throttle vs. penalizing jerky changes in steering/throttle. These were
tuned offline (outside this repository, in a separate simulator project)
and are simply hardcoded here as the result of that tuning process — they
are not computed or adjusted by anything in this file at runtime.

USED BY
-------
  mpc_controller.py — the ROS node that owns one MPCController instance
                       (dt=0.05s, N=25 steps -> 1.25s lookahead) and calls
                       .compute() every time a new car-position message
                       arrives, and .reset() when the path goes stale or a
                       fail-safe brake condition is hit.
"""

import math
import cvxpy as cp
import numpy as np
from scipy.linalg import expm

# Maximum physical steering deflection the car's steering system can reach.
MAX_STEER_RAD: float = math.radians(35.0)
# Maximum forward acceleration this controller is allowed to command (m/s^2).
MAX_ACCEL: float = 12.0
# Maximum braking (deceleration) this controller is allowed to command (m/s^2).
MAX_BRAKE: float = 9.0

# ---------------------------------------------------------------------------
# Speed- and corner-aware adjustments
# ---------------------------------------------------------------------------
# These two helpers don't change *what* the controller is trying to do —
# they change how strongly it penalizes aggressive or jerky commands,
# depending on how fast the car is going and how sharp the upcoming turn
# is. This makes the car feel calmer on straights and more responsive in
# corners, instead of using one fixed "stiffness" everywhere.

def _adaptive_R_scaling(vx: float, R_base: np.ndarray) -> np.ndarray:
    """
    Makes steering and acceleration commands cost more (i.e. be penalized
    more heavily) as the car goes faster, so the controller naturally
    avoids sharp inputs at high speed. The scaling factor rises quickly
    at low speed and levels off at higher speed, rather than growing
    without bound.
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
    Relaxes the "don't change the steering angle too abruptly" penalty
    when the upcoming path is curving sharply (kappa = curvature, i.e. how
    tight the turn is), so the controller isn't fighting itself to turn
    quickly through a hairpin. Never relaxes below 35% of the normal
    penalty, so steering changes are still damped even in the tightest
    corners.
    """
    scale = max(0.35, 1.0 / (1.0 + 3.0 * abs(kappa)))
    R = R_rate_base.copy()
    R[0, 0] *= scale
    return R


def _curvature(path: np.ndarray, idx: int) -> float:
    """
    Estimates how sharply the path is turning at a given point (1 / metres
    — a bigger number means a tighter turn), by comparing the path's
    direction just before and just after that point.
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
    The path-following controller used on this car. Given the car's current
    position, heading, speed, turn rate, and the path it should be
    following, this repeatedly plans a short sequence of steering/
    acceleration moves, picks the best one for right now, and returns a
    steering + throttle/brake command every time compute() is called.
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
            How much real time (in seconds) one planning step represents.
            Must match how often mpc_controller.py actually calls
            compute() (currently roughly every 0.05s / 20 times a second,
            triggered by incoming car-position updates rather than a fixed
            timer), otherwise the controller's internal predictions won't
            line up with how much time is actually passing on the car.
        N : int
            How many steps ahead the controller plans on each call
            (25 steps x 0.05s = about 1.25 seconds of lookahead).

        Vehicle geometry and dynamics constants below (distance from
        center of mass to front/rear axle, mass, moment of inertia, tire
        stiffness, and how quickly the steering/throttle actuators
        respond) describe the physical car this controller is running on.
        They're hardcoded here — if the physical car changes (different
        weight, different tires, etc.), these need to be updated manually
        to match, since nothing in this file measures them automatically.
        """
        self.dt = dt
        self.N  = N

        # ── Vehicle geometry & dynamics (describes the physical car) ────
        self.lf = 0.85    # distance from center of mass to front axle (m)
        self.lr = 0.70    # distance from center of mass to rear axle (m)
        self.m  = 255.0   # vehicle mass (kg)
        self.Iz = 110.0   # rotational inertia around the vertical axis (kg*m^2)
        self.Cf = 15000.0 # front-tire cornering stiffness
        self.Cr = 14000.0 # rear-tire cornering stiffness
        self.tau_delta = 0.08  # how quickly the steering actuator responds (s)
        self.tau_a     = 0.02  # how quickly the accel/brake response settles (s)

        self.nx = 8  # number of internal tracking values (see file header)
        self.nu = 2  # number of commands the controller outputs (steer, accel)

        # Tuning weights (see "TUNING WEIGHTS" note in the file header —
        # these numbers were arrived at through offline tuning, not
        # computed here). Roughly: Q controls how strongly the car is
        # pulled back toward the path, R controls how "expensive" large
        # steering/accel commands are, and R_rate controls how expensive
        # abrupt *changes* in those commands are (i.e. how jerky the ride
        # feels).
        Q_diag      = [0.6076038410420214, 0.7018612760165229, 7.107357922239617, 0.1016639549356476, 0.44488278317637964, 0.0, 0.0, 0.0]
        R_diag      = [7.869443219377219, 0.28548521974060515]
        R_rate_diag = [5.580499945962179, 9.993633621755315]

        self.Q      = np.diag(Q_diag)
        self.R      = np.diag(R_diag)
        self.R_rate = np.diag(R_rate_diag)

        # ── Hard actuator limits ────────────────────────────────────────
        # These are the physical limits of the real car — the controller
        # is never allowed to ask for more steering angle, acceleration,
        # or braking than these values, no matter what the optimizer would
        # otherwise prefer.
        self.a_max = MAX_ACCEL
        self.a_max_brake = MAX_BRAKE
        self.u_min = np.array([-MAX_STEER_RAD, -self.a_max_brake]) 
        self.u_max = np.array([ MAX_STEER_RAD,  self.a_max])
        
        # Hard limit on how much the steering angle / acceleration command
        # is allowed to change in a single tick (enforced as a strict rule
        # in _build_qp, on top of the softer "don't change too fast"
        # penalty from R_rate above). This caps worst-case jerkiness even
        # if the optimizer would otherwise want a bigger jump.
        self.du_max = np.array([math.radians(4.0), 0.6]) 

        # ── Values the controller remembers between ticks ───────────────
        self._delta_act:      float      = 0.0  # estimated current steering-actuator position
        self._a_act:          float      = 0.0  # estimated current accel-actuator output
        self._u_prev:         np.ndarray = np.zeros(self.nu)  # last commanded [steer, accel]
        self._v_des_filtered: float | None = None  # smoothed version of the requested speed

        self.last_telemetry: dict = {}  # diagnostic values from the most recent compute() call
        self._qp: dict | None = None    # the reusable optimization problem, built on first use

    def _build_qp(self) -> None:
        """
        Sets up the optimization problem (the "plan the next N steps"
        search) once, using placeholder values that get refilled on every
        tick. Building this once and reusing it — rather than rebuilding
        it from scratch every single tick — is what keeps this fast enough
        to run in real time.

        Includes a "soft" boundary: the car is allowed to drift up to
        3.5m to either side of the path if it truly has to, but doing so
        adds a very large penalty to the plan's score, so the optimizer
        will only actually use that room as a last resort.
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
        slack = cp.Variable(N)  # how far outside the soft lane boundary the plan drifts, if at all

        W_slack = 10000.0  # how heavily drifting outside the soft boundary is penalized

        # Rules the planned sequence of steering/accel commands must obey.
        constraints = [
            x[:, 0] == x0_p,                                # start from where the car actually is
            x[:, 1:] == Ad_p @ x[:, :-1] + Bd_p @ u,          # each future step follows the car's motion model
            u >= self.u_min[:, None],                        # never exceed physical steering/accel limits
            u <= self.u_max[:, None],
            x[0, :-1] <=  3.5 + slack,                        # stay within (or just barely outside) the lane
            x[0, :-1] >= -3.5 - slack,
            u[:, 0] - uprev_p <=  self.du_max,                # don't jump too abruptly from the last command
            u[:, 0] - uprev_p >= -self.du_max,
        ]

        if N > 1:
            du_hard = cp.diff(u, axis=1)
            constraints += [
                du_hard <=  self.du_max[:, None],             # same "don't jump abruptly" rule between future steps
                du_hard >= -self.du_max[:, None],
            ]

        # How a candidate plan's "score" is calculated (lower is better):
        # being off-path costs something, using large steering/accel costs
        # something, drifting outside the soft lane boundary costs a lot,
        # and changing the command abruptly from tick to tick costs
        # something too.
        cost  = cp.sum(cp.sum_squares(cp.multiply(sqrtQ_param, x)))
        cost += cp.sum(cp.sum_squares(cp.multiply(sqrtR_param, u)))
        cost += W_slack * cp.sum_squares(slack)
        
        # Penalty for how different this tick's command is from last tick's.
        cost += cp.sum_squares(cp.multiply(sqrtRr_param[:, 0], u[:, 0]) - weighted_u_prev_param)

        # Penalty for jerkiness *within* the planned sequence itself.
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
        Builds a short-term prediction of how the car's state changes over
        one tick, given the current speed. Blends the low-speed
        ("kinematic", geometry-only) and higher-speed ("dynamic",
        tire-grip-aware) descriptions of the car's motion, weighted by how
        fast the car is currently going — see "why two driving styles" in
        the file header. A tiny numerical epsilon is added throughout to
        keep the underlying math library's internal structure consistent
        from tick to tick, which keeps the solver fast.
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

        # Blend factor: fully "kinematic" (geometry-only) below 1 m/s,
        # fully "dynamic" (tire-grip-aware) above 2.5 m/s, smoothly
        # blended in between.
        alpha = np.clip((v_x - 1.0) / (2.5 - 1.0), 0.0, 1.0)
        A_c = (1.0 - alpha) * A_kin + alpha * A_dyn
        
        # Converts the continuous-time model above into a step-by-step
        # ("if we're here now, where are we one tick later") prediction
        # matched exactly to the tick length (dt), rather than an
        # approximation — this matters because dt (0.05s) is close in
        # scale to how fast the accel actuator responds (0.02s), and a
        # cruder approximation could become numerically unstable there.
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
        Figures out exactly how "off track" the car currently is, and
        packages that up (along with the car's current turn rate and speed
        error) into the internal tracking-value list the optimizer needs.
        Also estimates how sharp the path is curving a short distance
        ahead, for the corner-softening adjustment in _adaptive_R_rate.
        """
        # Project forward from the car's reference position to its front
        # axle, since that's the point whose position relative to the path
        # actually matters for steering.
        fa = car_pos + self.lf * np.array([math.cos(car_yaw), math.sin(car_yaw)])
        base_dists = np.linalg.norm(path - fa, axis=1)
        base_idx   = int(np.argmin(base_dists))

        if base_idx < len(path) - 1:
            seg = path[base_idx + 1] - path[base_idx]
        else:
            seg = path[base_idx]     - path[base_idx - 1]

        seg_len = float(np.linalg.norm(seg))
        if seg_len < 1e-6:
            # Two path points sit on top of each other — nothing useful to
            # compute; return a "no error" state rather than dividing by
            # (near) zero.
            return np.zeros(self.nx), 0.0, {}

        # Direction the path is pointing at this point.
        path_yaw = math.atan2(seg[1], seg[0])

        # How far to the side of the path the car's front axle currently
        # sits (positive = one side, negative = the other).
        dx = fa[0] - path[base_idx][0]
        dy = fa[1] - path[base_idx][1]
        e_y_proj = dy * math.cos(path_yaw) - dx * math.sin(path_yaw)
        true_dist = math.hypot(dx, dy)
        e_y = true_dist * (1.0 if e_y_proj >= 0 else -1.0)

        # How many radians off the car's heading is from the path's
        # direction, wrapped to a sensible -180..180 degree range.
        e_psi = math.atan2(math.sin(car_yaw - path_yaw), math.cos(car_yaw - path_yaw))
        # Approximate rate at which the sideways offset is changing. This
        # approximation assumes the car has no meaningful sideways
        # (skidding) velocity of its own — a reasonable assumption here
        # since this stack has no sensor that measures sideways velocity
        # directly; it's derived only from forward speed and heading error.
        e_yd  = car_speed * math.sin(e_psi)

        # Look a short distance (1m) further along the path from the
        # car's current position, and estimate the curvature there — this
        # is the "curvature preview" used to soften/tighten steering
        # ahead of a corner rather than only reacting once in it.
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
        Runs the actual search for the best steering/acceleration plan,
        given where the car is right now and how it's expected to move.
        Reuses the same optimization problem set up in _build_qp on every
        call (rather than building a fresh one each time) so this stays
        fast enough to run in real time on every tick.
        """
        if self._qp is None:
            self._build_qp()

        qp = self._qp
        qp["Ad"].value = Ad
        qp["Bd"].value = Bd
        qp["x0"].value = x0
        qp["u_prev"].value = self._u_prev

        # The optimizer library wants penalty weights as square roots, so
        # it can compute "penalty x squared-difference" efficiently.
        sqrtQ  = np.sqrt(np.clip(np.diag(self.Q), 1e-6, 1e6))
        sqrtR  = np.sqrt(np.clip(np.diag(R_scaled), 1e-6, 1e6))
        sqrtRr = np.sqrt(np.clip(np.diag(R_rate_scaled), 1e-6, 1e6))
        
        qp["sqrtQ"].value = sqrtQ[:, None]
        qp["sqrtR"].value = sqrtR[:, None]
        qp["sqrtRr"].value = sqrtRr[:, None]
        qp["weighted_u_prev"].value = sqrtRr * self._u_prev

        # ── Primary solver: OSQP ─────────────────────────────────────
        # Fast enough to comfortably run every tick; "warm_start=True"
        # lets it reuse the previous solve as a starting point, which
        # makes it converge faster tick-to-tick.
        try:
            qp["prob"].solve(
                solver=cp.OSQP, verbose=False, warm_start=True,
                eps_abs=1e-5, eps_rel=1e-5, max_iter=8000,
            )
        except cp.error.SolverError as exc:
            print(f"[MPC] Warning: OSQP raised an error: {exc!r}")
            status, u_val = None, None
        else:
            status = qp["prob"].status
            u_val = qp["u"][:, 0].value

        status = qp["prob"].status
        u_val  = qp["u"][:, 0].value

        if status == cp.OPTIMAL_INACCURATE and u_val is not None:
            print("[MPC] Warning: OSQP OPTIMAL_INACCURATE — Proceeding with viable solution.")
            return u_val.copy()

        if status == cp.OPTIMAL and u_val is not None:
            return u_val.copy()

        # ── Fallback solver: Clarabel ──────────────────────────────────
        # Only tried if OSQP fails outright — slower, but a good backup.
        try:
            qp["prob"].solve(solver=cp.CLARABEL, verbose=False)
            status_fb = qp["prob"].status
            u_val_fb  = qp["u"][:, 0].value
            if status_fb in (cp.OPTIMAL, cp.OPTIMAL_INACCURATE) and u_val_fb is not None:
                print("[MPC] Warning: OSQP failed, Clarabel succeeded.")
                return u_val_fb.copy()
        except cp.error.SolverError as exc:
            print(f"[MPC] Warning: Clarabel also failed: {exc!r}")

        # ── Last resort: both solvers failed ────────────────────────────
        # Rather than returning a nonsensical or stale command, hold the
        # last steering angle and apply full braking. This is a safety
        # fallback, not a normal operating path.
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
        Runs one full control decision: work out how off-track the car is
        -> predict how the car responds to inputs at its current speed ->
        adjust smoothness penalties for current speed/corner sharpness ->
        search for the best steering/accel plan -> update the actuator-lag
        estimate -> convert to normalized output values.

        Parameters
        ----------
        path : np.ndarray, shape (n, 2)
            The path to follow, as a list of [x, y] waypoints in the same
            global coordinate frame as car_pos. Points should run roughly
            evenly spaced from behind the car to ahead of it — big gaps
            make the curvature estimate noisy.
        car_pos : np.ndarray, shape (2,)
            The car's current [x, y] position (global frame). This should
            be a consistent reference point on the car (e.g. rear axle);
            the controller projects forward to the front axle internally.
        car_yaw : float
            The car's current heading, in radians, using the same
            zero-reference and rotation direction as the path's
            coordinates.
        car_speed : float
            The car's current forward speed in metres per second. Always
            positive/forward — should not go negative even in reverse.
        desired_speed : float
            The speed the car is currently being asked to reach, in
            metres per second. Smoothed internally, so it's fine for this
            to change abruptly between calls.
        car_yaw_rate : float, optional
            How fast the car's heading is currently changing, in radians
            per second (positive = turning left). Defaults to 0.0 if not
            available.

        Returns
        -------
        (steering, throttle, brake) : tuple of float
            steering in [-1, 1] (negative/positive convention matches
            whatever this stack's output message expects — see
            mpc_controller.py for the exact conversion),
            throttle in [0, 1], brake in [0, 1]. Throttle and brake are
            mutually exclusive — the controller is always doing exactly
            one or the other, never both at once.

        Safety guard: if fewer than 2 path points are given, this
        immediately returns a neutral, mildly-braking command
        (0.0, 0.0, 0.5) without touching any of the internal state or
        running the optimizer. In normal operation, mpc_controller.py is
        expected to catch a missing/too-short path before ever calling
        compute() with one, so this guard should rarely trigger in
        practice — but it's here in case it does.
        """
        if len(path) < 2:
            return 0.0, 0.0, 0.5   

        # Smooth the requested speed so a sudden jump doesn't translate
        # into a sudden jerk in the commanded acceleration.
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

        # ── Update the actuator-lag estimate ────────────────────────────
        # Simulates how far the steering/accel actuators would have moved
        # toward the just-issued command over one tick, given how quickly
        # they're expected to respond (tau_delta / tau_a). Uses an exact
        # formula rather than a simple step-by-step approximation, because
        # a simple approximation can become unstable here (the tick length
        # is comparable to how fast the accel actuator responds).
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
        Clears everything the controller remembers between ticks
        (actuator-lag estimates, last command, smoothed target speed), and
        discards the optimizer's warm-start state. Call this whenever the
        car's situation has changed enough that old memory would be
        misleading — for example, if the path being followed has gone
        stale, or after a fail-safe brake, so the controller doesn't try
        to smoothly continue from a command that's no longer relevant.
        """
        self._delta_act       = 0.0
        self._a_act           = 0.0
        self._u_prev           = np.zeros(self.nu)
        self._v_des_filtered  = None
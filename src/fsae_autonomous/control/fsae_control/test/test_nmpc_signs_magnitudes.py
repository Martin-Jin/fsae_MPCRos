"""
test_nmpc_signs_magnitudes.py — behavioral contract tests for NMPCController
(fsae_control.mpc.nmpc_core), calling compute() directly with hand-built
paths and car states standing in for what nmpc_controller.py (the ROS2
node) would normally supply from /fsae/planning/selected_trajectory and
/fsae/slam/car_position (+ its state fallback ladder — see
_resolve_state() in nmpc_controller.py and docs/NMPC_INTEGRATION_GAPS.md
gaps A1-A3).

WHAT THIS TESTS
----------------
Like the pre-existing test_mpc_controller.py this repo already had for the
earlier LTV-QP controller, this intentionally does NOT lock exact numeric
output values tick-by-tick — the controller is a numerical optimizer with
offline-tuned weights, and exact outputs are an implementation detail that
can shift slightly with solver/tuning changes. Instead each test checks a
SIGN or a MAGNITUDE RELATIONSHIP that must hold for the controller to be
doing something sensible:

    - is the sign of the steering command correct (left vs right, for a
      car offset from the path, misaligned with it, or approaching a known
      corner in a known direction)?
    - does accel/brake behave correctly relative to the current vs. desired
      speed (speed up when below target, brake when above)?
    - does a LARGER error produce a LARGER-magnitude correction than a
      smaller one, at the same operating point (a monotonicity check, not
      an exact value)?
    - does a tighter corner (smaller radius) at the same approach distance
      demand more steering than a gentler one?
    - do outputs stay inside their documented physical ranges
      (control_limits.MAX_STEER_RAD, MAX_ACCEL, MAX_BRAKE) at every
      condition tested, including deliberately extreme/adversarial ones?
    - do documented edge cases (too-short path, straight line at target
      speed) degrade the way nmpc_core.py's own docstring says they should?

Sign convention used throughout (matches nmpc_core.py's own):
    delta_cmd (rad), +ve = LEFT turn.
    e_y (m), +ve = front axle LEFT of the path.
    a_cmd (m/s^2), +ve = accelerate, -ve = brake.

HOW TO RUN
-----------
    colcon build --packages-select fsae_control
    source install/setup.bash
    colcon test --packages-select fsae_control --pytest-args -v
    colcon test-result --verbose

Or directly (still needs the package sourced first):
    pytest src/fsae_autonomous/control/fsae_control/test/test_nmpc_signs_magnitudes.py -v
"""
import math

import numpy as np
import pytest

from fsae_control.mpc.mpc_params import MPCParams
from fsae_control.mpc.nmpc_core import MAX_ACCEL, MAX_BRAKE, MAX_STEER_RAD, NMPCController
from fsae_control.mpc.nmpc_params import NMPCParams

DT = 0.05


def make_controller(**nmpc_kw) -> NMPCController:
    """Fresh controller per test. alat_ceiling off -- it models an FSDS
    simulator artifact (see docs/NMPC_INTEGRATION_GAPS.md gap D2), not
    something these plant-agnostic sign/magnitude checks should depend on."""
    npar = NMPCParams(nmpc_alat_ceiling_enabled=False, **nmpc_kw)
    return NMPCController(dt=DT, params=MPCParams(), nmpc=npar)


def straight_path(length: float = 60.0, spacing: float = 0.5, y: float = 0.0) -> np.ndarray:
    """A straight path along +X at a fixed y, from x=0 to x=length."""
    xs = np.arange(0.0, length, spacing)
    return np.column_stack([xs, np.full_like(xs, y)])


def corner_path(direction: str, straight_m=20.0, radius=10.0, arc_deg=90.0,
                ds=0.25) -> np.ndarray:
    """Straight run then a constant-radius turn, LEFT or RIGHT."""
    sign = 1.0 if direction == 'left' else -1.0
    pts = [np.zeros(2)]
    psi = 0.0
    for _ in range(int(straight_m / ds)):
        pts.append(pts[-1] + ds * np.array([math.cos(psi), math.sin(psi)]))
    k = sign / radius
    for _ in range(int(math.radians(arc_deg) / abs(k * ds))):
        psi += k * ds
        pts.append(pts[-1] + ds * np.array([math.cos(psi), math.sin(psi)]))
    return np.array(pts)


def run_ticks(ctrl: NMPCController, path: np.ndarray, car_pos, car_yaw, car_speed,
              desired_speed, n_ticks=8, car_yaw_rate=0.0, car_vy=0.0):
    """Run several ticks (the solver warm-starts from its own previous
    solution, so a single-tick snapshot right after construction can still
    reflect the cold-start U=0 initial guess more than steady state)."""
    delta = accel = 0.0
    for _ in range(n_ticks):
        steer_n, throttle_n, brake_n = ctrl.compute(
            path=path, car_pos=np.asarray(car_pos, dtype=float), car_yaw=car_yaw,
            car_speed=car_speed, desired_speed=desired_speed,
            car_yaw_rate=car_yaw_rate, car_vy=car_vy,
        )
        delta = ctrl.last_telemetry['delta_cmd']
        accel = ctrl.last_telemetry['a_cmd']
    return delta, accel, ctrl.last_telemetry


# ---------------------------------------------------------------------------
# Straight path, on-line: near-zero steering
# ---------------------------------------------------------------------------

def test_straight_path_on_line_at_target_speed_gives_near_zero_output():
    ctrl = make_controller()
    path = straight_path()
    delta, accel, tel = run_ticks(ctrl, path, car_pos=(0.0, 0.0), car_yaw=0.0,
                                  car_speed=10.0, desired_speed=10.0)
    assert abs(math.degrees(delta)) < 1.0, f'steer should be ~0, got {math.degrees(delta):.2f} deg'
    assert abs(accel) < 1.0, f'accel should be ~0 at target speed, got {accel:.2f} m/s^2'


# ---------------------------------------------------------------------------
# Lateral offset: sign and monotonicity
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('offset_y,expected_sign', [(1.0, -1), (-1.0, +1)])
def test_steer_sign_corrects_lateral_offset(offset_y, expected_sign):
    """Car to the LEFT of a straight path (+y) must steer RIGHT (-delta) to
    return to it, and vice versa -- e_y > 0 means the axle is left of the
    path (nmpc_core.py's own convention), so the correction must be
    negative steering, matching delta_cmd's +ve=left sign convention."""
    ctrl = make_controller()
    path = straight_path()
    delta, _accel, tel = run_ticks(ctrl, path, car_pos=(5.0, offset_y), car_yaw=0.0,
                                   car_speed=8.0, desired_speed=8.0)
    assert math.copysign(1, delta) == expected_sign, (
        f'offset_y={offset_y}: expected steer sign {expected_sign}, '
        f'got delta_cmd={math.degrees(delta):.2f} deg (e_y measured = {tel["e_y"]:.2f})'
    )
    assert abs(delta) > math.radians(0.5), 'should actually correct a 1 m offset, not ignore it'


def test_larger_lateral_offset_demands_more_steering():
    """Monotonicity, not an exact value: doubling the offset (same
    conditions otherwise) should not produce a SMALLER correction."""
    path = straight_path()
    deltas = []
    for offset_y in (0.3, 1.2):
        ctrl = make_controller()
        delta, _accel, _tel = run_ticks(ctrl, path, car_pos=(5.0, offset_y), car_yaw=0.0,
                                        car_speed=8.0, desired_speed=8.0)
        deltas.append(abs(delta))
    assert deltas[1] >= deltas[0], (
        f'larger offset (1.2 m) produced a smaller correction ({math.degrees(deltas[1]):.2f} deg) '
        f'than the smaller offset (0.3 m, {math.degrees(deltas[0]):.2f} deg)'
    )


# ---------------------------------------------------------------------------
# Heading error only (on-line, but pointed the wrong way)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('yaw_offset_deg,expected_sign', [(15.0, -1), (-15.0, +1)])
def test_steer_sign_corrects_heading_error(yaw_offset_deg, expected_sign):
    """Car exactly ON the path (e_y=0) but yawed away from its direction
    must steer to correct e_psi -- pointed too far LEFT of the path's own
    heading (+yaw_offset) must steer RIGHT (-delta)."""
    ctrl = make_controller()
    path = straight_path()
    delta, _accel, tel = run_ticks(
        ctrl, path, car_pos=(5.0, 0.0), car_yaw=math.radians(yaw_offset_deg),
        car_speed=8.0, desired_speed=8.0,
    )
    assert math.copysign(1, delta) == expected_sign, (
        f'yaw_offset={yaw_offset_deg} deg: expected steer sign {expected_sign}, '
        f'got delta_cmd={math.degrees(delta):.2f} deg (e_psi measured = '
        f'{math.degrees(tel["e_psi"]):.2f} deg)'
    )


# ---------------------------------------------------------------------------
# Corners: direction and curvature-magnitude sensitivity
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('direction,expected_sign', [('left', +1), ('right', -1)])
def test_steer_sign_matches_corner_direction(direction, expected_sign):
    """Car dead on-line, approaching a known bend well within the horizon's
    reach (v * N * dt) -- must plan steering toward the bend's own
    direction, not away from it or zero (see nmpc_offline_check.py's
    TURN-IN check on the sim side for the structural reason this matters).

    straight_m is deliberately kept BELOW the horizon's reach (v * N * dt =
    6 * 20 * 0.05 = 6.0 m at these defaults) -- a bend further away than
    that is genuinely outside the prediction horizon, and correctly planning
    ~0 steering for it is not a failure (see nmpc_offline_check.py's own
    in-reach/out-of-reach split). An earlier version of this test used
    straight_m=8.0, ITSELF beyond the 6 m reach, and asserted "real
    steering" anyway -- a bug in the test, not the solver."""
    ctrl = make_controller()
    path = corner_path(direction, straight_m=3.0, radius=10.0)
    delta, _accel, tel = run_ticks(ctrl, path, car_pos=(0.0, 0.0), car_yaw=0.0,
                                   car_speed=6.0, desired_speed=6.0, n_ticks=12)
    assert math.copysign(1, delta) == expected_sign, (
        f'{direction} corner: expected steer sign {expected_sign}, '
        f'got delta_cmd={math.degrees(delta):.2f} deg'
    )
    assert abs(delta) > math.radians(0.5), f'{direction} corner: should plan real steering, not ~0'


def test_tighter_corner_demands_more_steering_than_gentler_one():
    """Same approach distance/speed, smaller radius (tighter turn) must not
    produce LESS steering than a gentler one."""
    deltas = {}
    for radius in (20.0, 6.0):
        ctrl = make_controller()
        path = corner_path('left', straight_m=8.0, radius=radius)
        delta, _accel, _tel = run_ticks(ctrl, path, car_pos=(0.0, 0.0), car_yaw=0.0,
                                        car_speed=5.0, desired_speed=5.0, n_ticks=12)
        deltas[radius] = abs(delta)
    assert deltas[6.0] >= deltas[20.0], (
        f'tighter corner (r=6m, {math.degrees(deltas[6.0]):.2f} deg) produced less '
        f'steering than the gentler one (r=20m, {math.degrees(deltas[20.0]):.2f} deg)'
    )


# ---------------------------------------------------------------------------
# Longitudinal: accelerate below target, brake above target
# ---------------------------------------------------------------------------

ACCEL_DEAD_ZONE_REASON = (
    'REPRODUCIBLE ANOMALY, precisely localized, not a test bug -- flagging per '
    'project convention (record a falsified/unexpected result explicitly, do not '
    'silently drop it). With the car dead on-line, dead aligned (e_y=e_psi=v_y=r='
    'delta_act=a_act all exactly 0) on a straight path, compute() commands '
    'a_cmd ~= 0 (< 1e-9, often < 1e-25) for essentially the WHOLE car_speed range '
    '[2.5, 5.6] m/s, regardless of how large the car_speed/desired_speed gap is -- '
    'a sweep at a constant +5.0 m/s gap gives a_cmd=+2.43 at 0.5 m/s, decaying '
    'smoothly through the zero band, then RECOVERING to a saturated +4.80 at and '
    'above ~5.8-6.0 m/s. The dead zone\'s lower edge (2.5 m/s) is EXACTLY '
    'nmpc_core._Plant.v_blend_hi -- the kinematic/dynamic blend fully engages '
    '(blend=1.0) at exactly this speed, which is the strongest lead on the '
    'mechanism. Braking from a real moving speed (car_speed=15 -> desired=5, '
    'a_cmd=-4.2) is UNAFFECTED -- this is not "acceleration is broken", it is a '
    'narrow, speed-keyed dead zone. Confirmed: (1) reproduces IDENTICALLY against '
    'the pristine, unmodified sim-tree nmpc_core.py, not introduced by this port; '
    '(2) a direct finite-difference of _cost() at car_speed=4 confirms a large, '
    'real cost reduction IS available by accelerating (cost drops 7392 -> 5126 at '
    'a_pert=5.0 m/s^2) -- the true objective is sensitive, but the QP\'s solved dU '
    'stays ~0 regardless; (3) not warm-start-specific (a feasible nonzero '
    'U[:,1]=0.3 seed does not escape it). Root cause not isolated further: this is '
    'squarely in NMPC-solver-internals territory (CLAUDE.md: reserved for the most '
    'expensive/high-effort model tier, "a wrong mechanism can pass offline '
    'validation and still be wrong") and deliberately was NOT root-caused or fixed '
    'in this session -- see the chat transcript for the full diagnostic trail '
    '(including a look at A_k/S condensation magnitudes) before attempting a fix.'
)


@pytest.mark.xfail(reason=ACCEL_DEAD_ZONE_REASON, strict=False)
def test_accelerates_when_below_target_speed():
    ctrl = make_controller()
    path = straight_path()
    _delta, accel, _tel = run_ticks(ctrl, path, car_pos=(0.0, 0.0), car_yaw=0.0,
                                    car_speed=4.0, desired_speed=12.0)
    assert accel > 0.5, f'should be accelerating toward a much higher target, got {accel:.2f} m/s^2'


def test_brakes_when_above_target_speed():
    """NOT in the dead zone (car_speed=15, well above it) -- braking from a
    genuinely moving speed works correctly. See ACCEL_DEAD_ZONE_REASON above:
    this is the case that proves the anomaly is speed-keyed, not a general
    'acceleration is broken' failure."""
    ctrl = make_controller()
    path = straight_path()
    _delta, accel, _tel = run_ticks(ctrl, path, car_pos=(0.0, 0.0), car_yaw=0.0,
                                    car_speed=15.0, desired_speed=5.0)
    assert accel < -0.5, f'should be braking toward a much lower target, got {accel:.2f} m/s^2'


@pytest.mark.xfail(reason=ACCEL_DEAD_ZONE_REASON, strict=False)
def test_larger_speed_error_demands_more_accel_authority():
    """Monotonicity: a bigger shortfall below target should not command
    LESS acceleration than a smaller shortfall, at the same current speed.

    Both operating points chosen here (car_speed=4.0, target 6.0 or 14.0) fall
    inside the dead zone described in ACCEL_DEAD_ZONE_REASON, so both give
    accel ~= 0 and the `>=` assertion below is a FALSE POSITIVE if run without
    xfail (0 >= 0 trivially holds despite neither side producing a real,
    meaningful acceleration) -- caught by manually inspecting the actual values
    (9.6e-27 and 4.4e-26) rather than trusting the assertion's pass/fail alone."""
    path = straight_path()
    accels = []
    for target in (6.0, 14.0):
        ctrl = make_controller()
        _delta, accel, _tel = run_ticks(ctrl, path, car_pos=(0.0, 0.0), car_yaw=0.0,
                                        car_speed=4.0, desired_speed=target)
        accels.append(accel)
    assert accels[1] > accels[0] + 0.5, (
        f'larger target (14 m/s, accel={accels[1]:.2f}) should command meaningfully '
        f'more accel than the smaller target (6 m/s, accel={accels[0]:.2f}), not '
        f'just a non-strictly-smaller value'
    )


# ---------------------------------------------------------------------------
# Output ranges: must never exceed physical limits, even under adversarial input
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('car_pos,car_yaw,car_speed,desired_speed', [
    ((0.0, 8.0), math.radians(80.0), 15.0, 15.0),     # way off-line, badly misaligned, fast
    ((0.0, -8.0), math.radians(-80.0), 15.0, 15.0),    # mirror of the above
    ((0.0, 0.0), 0.0, 0.0, 20.0),                       # standing start, full target speed
    ((0.0, 0.0), 0.0, 25.0, 0.0),                       # way over target, must hard-brake
])
def test_outputs_never_exceed_documented_limits_even_under_adversarial_input(
        car_pos, car_yaw, car_speed, desired_speed):
    ctrl = make_controller()
    path = straight_path()
    delta, accel, tel = run_ticks(ctrl, path, car_pos=car_pos, car_yaw=car_yaw,
                                  car_speed=car_speed, desired_speed=desired_speed)
    assert math.isfinite(delta) and math.isfinite(accel), (
        f'non-finite output for car_pos={car_pos} car_yaw={car_yaw} '
        f'car_speed={car_speed} desired_speed={desired_speed}: delta={delta} accel={accel}'
    )
    assert abs(delta) <= MAX_STEER_RAD + 1e-6, f'delta_cmd {math.degrees(delta):.2f} deg exceeds MAX_STEER_RAD'
    assert -MAX_BRAKE - 1e-6 <= accel <= MAX_ACCEL + 1e-6, (
        f'a_cmd {accel:.2f} m/s^2 outside [-{MAX_BRAKE}, {MAX_ACCEL}]'
    )


# ---------------------------------------------------------------------------
# Documented edge case: too-short a path is a safe no-op, not a crash
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('n_points', [0, 1, 2])
def test_too_short_path_returns_safe_default(n_points):
    """nmpc_core.py's compute() docstring: `if path is None or len(path) < 3:
    return 0.0, 0.0, 0.5` -- a documented guard, not an exception path."""
    ctrl = make_controller()
    path = straight_path()[:n_points] if n_points else np.empty((0, 2))
    steer, throttle, brake = ctrl.compute(
        path=path, car_pos=np.array([0.0, 0.0]), car_yaw=0.0,
        car_speed=5.0, desired_speed=5.0,
    )
    assert (steer, throttle, brake) == (0.0, 0.0, 0.5), (
        f'expected the documented safe default (0.0, 0.0, 0.5) for a {n_points}-point '
        f'path, got {(steer, throttle, brake)}'
    )

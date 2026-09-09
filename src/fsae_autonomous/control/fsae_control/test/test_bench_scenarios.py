"""
test_bench_scenarios.py — geometry checks for the bench-rig test-path
library (fsae_control.mpc.bench_scenarios).

WHAT THIS TESTS
----------------
Pure geometry, no ROS graph (mirrors test_nmpc_core_math.py's own
import-without-rclpy style):

    1. STRAIGHT-PATH REGRESSION — straight_path() must reproduce
       mock_pose_path_publisher.py's old inline np.linspace generation
       exactly, since scenario='straight' is the rig's default and must
       stay byte-identical to before this library existed.
    2. CONTINUITY — turn_path()/s_curve_path() waypoints stay evenly spaced
       (no gaps/jumps at a segment join).
    3. BOUNDED CURVATURE — per-step heading change never exceeds the arc's
       own commanded curvature by more than a small numerical tolerance.
    4. S-CURVE SIGN FLIP — the two arcs bend opposite ways by equal
       magnitude, so net heading change over the whole path is ~0.
    5. RANDOM_START_OFFSET BOUNDS — sampled (dy, dyaw) always falls within
       the caller-specified bound, across many seeded draws.

HOW TO RUN
-----------
    colcon build --packages-select fsae_control
    source install/setup.bash
    colcon test --packages-select fsae_control --pytest-args -v
    colcon test-result --verbose

Or directly (still needs the package sourced first):
    pytest src/fsae_autonomous/control/fsae_control/test/test_bench_scenarios.py -v
"""
import numpy as np

from fsae_control.mpc import bench_scenarios as scen


# ── 1. Straight-path regression ─────────────────────────────────────────

def test_straight_path_matches_old_inline_generation():
    length_m, spacing_m = 100.0, 0.5
    n_pts = max(2, int(length_m / spacing_m) + 1)
    xs_old = np.linspace(0.0, length_m, n_pts)
    expected = np.column_stack([xs_old, np.zeros_like(xs_old)])

    actual = scen.straight_path(length_m, spacing_m)

    assert actual.shape == expected.shape
    assert np.allclose(actual, expected, atol=0.0)


# ── 2. Continuity ────────────────────────────────────────────────────────

def _spacings(path_xy):
    seg = np.diff(path_xy, axis=0)
    return np.hypot(seg[:, 0], seg[:, 1])


def test_turn_path_spacing_is_uniform():
    path = scen.turn_path(radius_m=15.0, arc_deg=45.0, spacing_m=0.5)
    spacings = _spacings(path)
    assert np.allclose(spacings, 0.5, atol=1e-9)


def test_s_curve_path_spacing_is_uniform():
    path = scen.s_curve_path(radius_m=15.0, arc_deg=45.0, spacing_m=0.5)
    spacings = _spacings(path)
    assert np.allclose(spacings, 0.5, atol=1e-9)


# ── 3. Bounded curvature ────────────────────────────────────────────────

def _headings(path_xy):
    seg = np.diff(path_xy, axis=0)
    return np.arctan2(seg[:, 1], seg[:, 0])


def test_turn_path_curvature_matches_commanded_radius():
    radius_m, spacing_m = 15.0, 0.5
    path = scen.turn_path(radius_m=radius_m, arc_deg=45.0, spacing_m=spacing_m)
    psi = _headings(path)
    dpsi = np.diff(psi)
    kappa_expected = 1.0 / radius_m
    # Every step's heading change is either ~0 (straight segment) or
    # ~kappa*spacing_m (arc segment) -- never larger in magnitude than the
    # commanded curvature (no spurious spikes from the segment joins).
    assert np.all(np.abs(dpsi) <= kappa_expected * spacing_m + 1e-9)


def test_s_curve_path_curvature_matches_commanded_radius():
    radius_m, spacing_m = 15.0, 0.5
    path = scen.s_curve_path(radius_m=radius_m, arc_deg=45.0, spacing_m=spacing_m)
    psi = _headings(path)
    dpsi = np.diff(psi)
    kappa_expected = 1.0 / radius_m
    assert np.all(np.abs(dpsi) <= kappa_expected * spacing_m + 1e-9)


# ── 4. S-curve sign flip ────────────────────────────────────────────────

def test_s_curve_net_heading_change_is_near_zero():
    path = scen.s_curve_path(radius_m=15.0, arc_deg=45.0, spacing_m=0.5)
    psi = _headings(path)
    # Heading returns to (approximately) its starting value after both
    # arcs -- a proper double bend, not two turns in the same direction.
    assert abs(psi[-1] - psi[0]) < 1e-6


def test_s_curve_reaches_a_nonzero_peak_heading():
    path = scen.s_curve_path(radius_m=15.0, arc_deg=45.0, spacing_m=0.5)
    psi = _headings(path)
    # Sanity: it's not just a straight line end-to-end.
    assert np.max(np.abs(psi)) > np.radians(10.0)


# ── 5. random_start_offset bounds ───────────────────────────────────────

def test_random_start_offset_within_bounds():
    max_lateral_m, max_heading_deg = 1.0, 15.0
    rng = np.random.default_rng(0)
    for _ in range(500):
        dx, dy, dyaw = scen.random_start_offset(max_lateral_m, max_heading_deg, rng)
        assert dx == 0.0
        assert -max_lateral_m <= dy <= max_lateral_m
        assert -np.radians(max_heading_deg) <= dyaw <= np.radians(max_heading_deg)


def test_random_start_offset_is_reproducible_with_same_seed():
    rng1 = np.random.default_rng(42)
    rng2 = np.random.default_rng(42)
    offset1 = scen.random_start_offset(1.0, 15.0, rng1)
    offset2 = scen.random_start_offset(1.0, 15.0, rng2)
    assert offset1 == offset2

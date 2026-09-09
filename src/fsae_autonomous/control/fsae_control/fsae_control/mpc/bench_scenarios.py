"""
bench_scenarios -- path-shape generators for mock_pose_path_publisher.py.

Kept in its own module (not inlined in mock_pose_path_publisher.py) so the
pure geometry is importable/unit-testable with no rclpy dependency, matching
nmpc_core.py's PathReference / test_nmpc_core_math.py split.

Every generator returns an (N, 2) float64 ndarray of Cartesian waypoints in
the mock 'map' frame, starting at the origin, initial heading = +X -- the
same contract mock_pose_path_publisher.py's straight-line path already
satisfied, so straight_path()'s output is byte-identical to the old inline
xs/ys generation it replaces (see test_bench_scenarios.py's regression
check).

Geometry approach: straight segments + arcs of constant curvature, not a
spline library. An arc has exactly-known, trivially bounded curvature
(kappa = 1/radius, discontinuous only at segment joins) -- adequate for a
bench rig whose job is to give the NMPC a directionally-varying reference,
not to be raceline-quality smooth. scipy is already a fsae_control
dependency but is not needed here.
"""
import numpy as np

DEFAULT_SPACING_M = 0.5


def straight_path(length_m: float, spacing_m: float = DEFAULT_SPACING_M) -> np.ndarray:
    """Unchanged straight-line generator, factored out of
    mock_pose_path_publisher.py's old inline __init__ code verbatim."""
    n_pts = max(2, int(length_m / spacing_m) + 1)
    xs = np.linspace(0.0, length_m, n_pts)
    return np.column_stack([xs, np.zeros_like(xs)])


def _integrate_heading(spacing_m: float, dpsi_per_step_segments: list) -> np.ndarray:
    """
    Walks forward in fixed-length steps, each segment contributing a
    constant per-step heading change (0.0 for a straight run, +-kappa*
    spacing_m for an arc), so curved scenarios are one continuous run (no
    heading discontinuity at a segment join, unlike concatenating
    independently-built arrays).
    """
    pts = [np.array([0.0, 0.0])]
    psi = 0.0
    for dpsi_per_step, n_steps in dpsi_per_step_segments:
        for _ in range(n_steps):
            psi += dpsi_per_step
            pts.append(pts[-1] + spacing_m * np.array([np.cos(psi), np.sin(psi)]))
    return np.array(pts)


def turn_path(radius_m: float, arc_deg: float, straight_in_m: float = 20.0,
              straight_out_m: float = 20.0, spacing_m: float = DEFAULT_SPACING_M) -> np.ndarray:
    """
    Straight-in -> constant-radius arc -> straight-out. Positive radius_m
    is a left turn (positive kappa), matching this repo's e_y-left-positive
    convention. Used for both 'gentle_turn' and 'sharp_turn' -- they share
    this one code path, differing only in the radius_m/arc_deg values
    passed at launch (see MPC_NODE_DOCS.md for recommended values).
    """
    kappa = 1.0 / radius_m
    arc_len_m = radius_m * np.radians(arc_deg)
    n_in = max(1, int(straight_in_m / spacing_m))
    n_arc = max(1, int(arc_len_m / spacing_m))
    n_out = max(1, int(straight_out_m / spacing_m))
    return _integrate_heading(spacing_m, [
        (0.0, n_in),
        (kappa * spacing_m, n_arc),
        (0.0, n_out),
    ])


def s_curve_path(radius_m: float, arc_deg: float, straight_in_m: float = 15.0,
                  straight_mid_m: float = 10.0, straight_out_m: float = 15.0,
                  spacing_m: float = DEFAULT_SPACING_M) -> np.ndarray:
    """
    Straight -> +kappa arc -> short straight -> -kappa arc (opposite sign,
    same magnitude) -> straight. A double bend that returns to the
    original heading, built as one continuous heading-integration run so
    the two arcs share a common psi state at their shared straight-mid
    segment (no seam discontinuity).
    """
    kappa = 1.0 / radius_m
    arc_len_m = radius_m * np.radians(arc_deg)
    n_in = max(1, int(straight_in_m / spacing_m))
    n_arc = max(1, int(arc_len_m / spacing_m))
    n_mid = max(1, int(straight_mid_m / spacing_m))
    n_out = max(1, int(straight_out_m / spacing_m))
    return _integrate_heading(spacing_m, [
        (0.0, n_in),
        (kappa * spacing_m, n_arc),
        (0.0, n_mid),
        (-kappa * spacing_m, n_arc),
        (0.0, n_out),
    ])


def random_start_offset(max_lateral_m: float, max_heading_deg: float,
                         rng: np.random.Generator) -> tuple:
    """
    Returns (dx, dy, dyaw_rad) to be ADDED to the path-start pose (not the
    path shape). dx is always 0.0 -- only lateral offset and heading are
    randomized, matching the bench rig's existing e_y/e_psi-isolation
    spirit; along-track start position is uninteresting for path-tracking.
    Caller supplies rng (np.random.default_rng(seed)) so a fixed seed
    reproduces the same offset -- no seeding decision made in here.
    """
    dy = float(rng.uniform(-max_lateral_m, max_lateral_m))
    dyaw = float(np.radians(rng.uniform(-max_heading_deg, max_heading_deg)))
    return 0.0, dy, dyaw

"""Unit tests for the ROS-free LiDAR refinement primitives (Component A)."""

import math

import numpy as np

from src.fsae_autonomous.perception.fsae_lidar.fsae_lidar.refinement import crop_sphere, estimate_ground_z, split_ground


def _make_cloud(points):
    """Build an (N, 5) cloud (x, y, z, intensity, ring) from xyz triples."""
    pts = np.asarray(points, dtype=float)
    out = np.zeros((pts.shape[0], 5), dtype=float)
    out[:, :3] = pts
    return out


def test_crop_sphere_keeps_only_inside_points():
    """crop_sphere returns exactly the points within r of the seed."""
    seed = (0.0, 0.0, 0.0)
    inside = [
        (0.0, 0.0, 0.0),     # at the seed
        (0.5, 0.0, 0.0),     # 0.5 m away
        (0.0, -0.9, 0.0),    # 0.9 m away
        (0.3, 0.3, 0.3),     # ~0.52 m away
    ]
    outside = [
        (1.5, 0.0, 0.0),     # 1.5 m away
        (0.0, 0.0, 2.0),     # 2.0 m away
        (1.0, 1.0, 1.0),     # ~1.73 m away
    ]
    cloud = _make_cloud(inside + outside)

    cropped = crop_sphere(cloud, seed, r_sphere=1.0)

    assert cropped.shape[0] == len(inside)
    # every returned point is genuinely within the radius
    d = np.linalg.norm(cropped[:, :3] - np.asarray(seed), axis=1)
    assert np.all(d <= 1.0 + 1e-9)


def test_crop_sphere_offset_seed():
    """Cropping works when the seed is not at the origin."""
    seed = (2.0, -1.0, 0.5)
    cloud = _make_cloud([
        (2.0, -1.0, 0.5),    # at seed
        (2.4, -1.0, 0.5),    # 0.4 m
        (5.0, -1.0, 0.5),    # 3.0 m -> excluded
    ])
    cropped = crop_sphere(cloud, seed, r_sphere=1.0)
    assert cropped.shape[0] == 2


def test_crop_sphere_empty_cloud():
    """An empty cloud yields an empty (0, 5) result, not an error."""
    cloud = np.empty((0, 5), dtype=float)
    cropped = crop_sphere(cloud, (0.0, 0.0, 0.0), r_sphere=1.0)
    assert cropped.shape == (0, 5)


def test_crop_sphere_boundary_inclusive():
    """A point exactly on the radius is kept (<= comparison)."""
    cloud = _make_cloud([(1.0, 0.0, 0.0), (1.0001, 0.0, 0.0)])
    cropped = crop_sphere(cloud, (0.0, 0.0, 0.0), r_sphere=1.0)
    assert cropped.shape[0] == 1


# --------------------------------------------------------------------------- #
# Ground removal (A4 + A5)
# --------------------------------------------------------------------------- #
def test_estimate_ground_z_median_of_bottom_percentile():
    """z_ground is the median z of the lowest ground_percentile of points."""
    # 10 points, bottom 20% -> lowest 2 (z = -0.52, -0.48), median = -0.50.
    zs = [-0.52, -0.48, -0.45, -0.44, -0.30, -0.20, 0.0, 0.1, 0.2, 0.3]
    cloud = _make_cloud([(0.0, 0.0, z) for z in zs])
    assert math.isclose(estimate_ground_z(cloud, 0.20), -0.50)


def test_estimate_ground_z_sparse_sphere_uses_at_least_one_point():
    """With few points, at least the single lowest point defines the ground."""
    cloud = _make_cloud([(0.0, 0.0, -0.4), (0.0, 0.0, 0.1), (0.0, 0.0, 0.2)])
    # 20% of 3 points -> ceil = 1 point -> the lowest z.
    assert math.isclose(estimate_ground_z(cloud, 0.20), -0.4)


def test_split_ground_separates_cone_from_ground():
    """Ground-level points are discarded; elevated cone points survive."""
    ground = [(x, y, -0.40 + dz) for x, y, dz in [
        (0.1, 0.0, 0.0), (-0.2, 0.3, 0.01), (0.4, -0.4, -0.01),
        (0.0, 0.5, 0.02), (-0.5, -0.1, 0.0), (0.3, 0.3, -0.02),
        (0.6, 0.1, 0.01), (-0.4, 0.4, 0.0),
    ]]
    cone = [(0.0, 0.0, -0.25), (0.02, 0.01, -0.15), (-0.01, 0.02, -0.05)]
    cloud = _make_cloud(ground + cone)

    above, at_ground, z_ground = split_ground(cloud, 0.20, 0.05)

    assert above.shape[0] == len(cone)
    assert at_ground.shape[0] == len(ground)
    assert -0.43 < z_ground < -0.37
    # every survivor is genuinely above the cut, every discard at/below it
    assert np.all(above[:, 2] > z_ground + 0.05)
    assert np.all(at_ground[:, 2] <= z_ground + 0.05)


def test_split_ground_points_within_offset_band_count_as_ground():
    """Points no more than z_offset above z_ground are still AT_GROUND."""
    cloud = _make_cloud([
        (0.0, 0.0, 0.0),    # defines the ground
        (0.1, 0.0, 0.05),   # exactly z_ground + z_offset -> AT_GROUND (strict >)
        (0.2, 0.0, 0.051),  # just above the band -> ABOVE_GROUND
    ])
    above, at_ground, z_ground = split_ground(cloud, 0.20, 0.05)
    assert math.isclose(z_ground, 0.0)
    assert above.shape[0] == 1
    assert math.isclose(above[0, 2], 0.051)
    assert at_ground.shape[0] == 2


def test_split_ground_all_ground_yields_empty_above():
    """A sphere with only ground returns everything as AT_GROUND."""
    cloud = _make_cloud([(x * 0.1, 0.0, -0.4) for x in range(8)])
    above, at_ground, _ = split_ground(cloud)
    assert above.shape[0] == 0
    assert at_ground.shape[0] == 8


def test_split_ground_empty_cloud():
    """An empty cloud yields two empty (0, 5) arrays and NaN ground."""
    above, at_ground, z_ground = split_ground(np.empty((0, 5), dtype=float))
    assert above.shape == (0, 5)
    assert at_ground.shape == (0, 5)
    assert math.isnan(z_ground)


def test_split_ground_preserves_all_columns():
    """The split keeps intensity and ring columns intact."""
    cloud = np.array([
        [0.0, 0.0, -0.40, 11.0, 3.0],   # ground
        [0.1, 0.0, -0.10, 42.0, 7.0],   # cone
    ])
    above, at_ground, _ = split_ground(cloud, 0.50, 0.05)
    assert above.shape == (1, 5)
    assert above[0, 3] == 42.0 and above[0, 4] == 7.0
    assert at_ground[0, 3] == 11.0 and at_ground[0, 4] == 3.0

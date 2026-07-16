"""Regression tests for the camera/LiDAR time-sync fix (Component B).

Covers two things that were both broken until this fix:

1. ``ConeDetection.msg`` had no ``header`` field, so ``fusion_node.py`` was
   reading ``msg.header.stamp`` off a field that didn't exist.
2. ``LidarFusionNode`` built its LiDAR-cloud buffer with
   ``deque(maxLen=10)`` -- Python's ``deque`` only accepts ``maxlen``
   (lowercase), so the node crashed with a ``TypeError`` on construction,
   before any temporal matching could run at all.

These exercise the exact code fusion_node.py runs: ``_find_closest_cloud``
picks the nearest buffered LiDAR cloud to a camera detection's timestamp,
within ``max_time_diff``, and refuses to match anything further away.

Requires a sourced ROS 2 workspace (rclpy + fsae_interfaces + fsae_lidar
built) -- this repo's Windows dev checkout has no ROS 2 install, so these
cannot be run there. On the robot/dev Linux box, from the workspace root:

    colcon build --packages-select fsae_interfaces fsae_lidar
    source install/setup.bash
    colcon test --packages-select fsae_lidar --event-handlers console_direct+
    colcon test-result --verbose

or, directly with pytest once the workspace is sourced:

    pytest perception/fsae_lidar/test/test_fusion_time_sync.py -v
"""
import pytest
import rclpy
from rclpy.time import Time
from std_msgs.msg import Header
from builtin_interfaces.msg import Time as TimeMsg
from fsae_interfaces.msg import ConeDetection

from fsae_lidar.fusion_node import LidarFusionNode


def make_stamp(seconds: float) -> TimeMsg:
    """Build a builtin_interfaces/Time from a float seconds value."""
    stamp = TimeMsg()
    stamp.sec = int(seconds)
    stamp.nanosec = int(round((seconds - stamp.sec) * 1e9))
    return stamp


@pytest.fixture(scope='module', autouse=True)
def ros_context():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture
def node():
    n = LidarFusionNode()
    yield n
    n.destroy_node()


def test_cone_detection_has_header_field():
    """ConeDetection.msg must carry a std_msgs/Header for temporal matching.

    Without this, _detections_cb's ``msg.header.stamp`` read would fail --
    this is the field the whole fix added.
    """
    fields = ConeDetection.get_fields_and_field_types()
    assert 'header' in fields, (
        "ConeDetection is missing its header field -- lidar_fusion's "
        "temporal matching (_detections_cb reads msg.header.stamp) "
        "cannot work without it")
    assert fields['header'] == 'std_msgs/Header'


def test_header_stamp_round_trips_through_time_from_msg():
    """The exact conversion fusion_node.py uses to turn a header into a float stamp."""
    msg = ConeDetection()
    msg.header = Header()
    msg.header.stamp = make_stamp(12.5)

    det_stamp = Time.from_msg(msg.header.stamp).nanoseconds * 1e-9
    assert det_stamp == pytest.approx(12.5, abs=1e-6)


def test_node_constructs_without_crashing(node):
    """Regression test for the deque(maxLen=...) typo that crashed __init__."""
    assert node._cloud_buffer.maxlen == 10
    assert len(node._cloud_buffer) == 0


def test_find_closest_cloud_picks_nearest_within_tolerance(node):
    node.max_time_diff = 0.10
    node._cloud_buffer.append((10.00, 'cloud_a', 'points_a'))
    node._cloud_buffer.append((10.05, 'cloud_b', 'points_b'))
    node._cloud_buffer.append((10.30, 'cloud_c', 'points_c'))

    msg, points = node._find_closest_cloud(10.06)

    assert msg == 'cloud_b'
    assert points == 'points_b'


def test_find_closest_cloud_rejects_beyond_max_time_diff(node):
    node.max_time_diff = 0.10
    node._cloud_buffer.append((9.0, 'cloud_a', 'points_a'))

    msg, points = node._find_closest_cloud(10.0)

    assert (msg, points) == (None, None)


def test_find_closest_cloud_empty_buffer_returns_none(node):
    msg, points = node._find_closest_cloud(0.0)
    assert (msg, points) == (None, None)

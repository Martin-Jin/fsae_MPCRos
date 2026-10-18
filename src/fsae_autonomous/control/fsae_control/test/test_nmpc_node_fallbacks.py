"""
test_nmpc_node_fallbacks.py: nmpc_controller.py's behaviour when an input degrades.

- The open-loop v_x estimate (no speed source live) must rise at the planned
  acceleration, not run away towards v_max.
- A path the solver cannot use (2 points) must produce a safe-stop, not the previous
  tick's command published again.
- Repeated waypoints in a planner path are dropped, so the path still solves.

The node is driven tick by tick: callbacks are skipped, the cached inputs are set
directly and _control_step() is called.
"""
import numpy as np
import pytest
import rclpy
from geometry_msgs.msg import Pose, PoseArray

from fsae_control.mpc.nmpc_controller import CONTROL_HZ, NMPCControllerNode

STRAIGHT = np.column_stack([np.arange(0.0, 30.5, 0.5), np.zeros(61)])


@pytest.fixture
def node():
    rclpy.init()
    n = NMPCControllerNode()
    sent = []
    n.pub_cmd.publish = sent.append
    n.sent = sent
    accel = []
    n.pub_accel.publish = accel.append
    n.accel = accel
    yield n
    n.destroy_node()
    rclpy.shutdown()


def _tick(n, path, speed=None):
    """One control tick. speed: a fresh odometry v_x, or None for no speed source."""
    if speed is not None:
        n._have_odom = True
        n._odom_stamp = n.get_clock().now()
        n._odom_vx = speed
    n._path = path
    n._path_stamp = n.get_clock().now()
    n._have_pose = True
    n._pose_stamp = n.get_clock().now()
    n._control_step()
    return n.sent[-1]


def test_open_loop_speed_integrates_the_acceleration_command(node):
    # No odometry, curr_vel or drive_status: v_x comes from the open-loop estimate,
    # which must be the integral of the commanded acceleration and nothing more.
    for _ in range(40):
        msg = _tick(node, STRAIGHT)
        assert msg.header.frame_id == 'nmpc_controller'
    assert node._active_vx_source == 'last_cmd (open-loop)'
    a = np.array([m.drive.acceleration for m in node.accel])
    assert a.sum() > 0.0   # the NMPC is asking to speed up, so a runaway would show
    assert node._open_loop_speed == pytest.approx(a.sum() / CONTROL_HZ, abs=1e-6)


def test_unsolvable_path_gives_a_safe_stop_not_the_last_command(node):
    node._car_yaw = 0.3   # a heading error, so the first command steers
    first = _tick(node, STRAIGHT, speed=3.0)
    assert first.header.frame_id == 'nmpc_controller'
    assert abs(first.drive.steering_angle) > 0.0

    two_points = STRAIGHT[:2].copy()   # passes the node's gate, too short for the solver
    second = _tick(node, two_points, speed=3.0)
    assert second.header.frame_id == 'nmpc_safe_stop'
    assert second.drive.steering_angle == 0.0
    assert second.drive.speed == 0.0


def test_repeated_waypoints_are_dropped_and_the_path_still_solves(node):
    # A path padded with copies of its last point, as the planner sometimes sends.
    padded = np.vstack([STRAIGHT[:8], np.repeat(STRAIGHT[7:8], 13, axis=0)])
    msg = PoseArray()
    for x, y in padded:
        p = Pose()
        p.position.x, p.position.y = float(x), float(y)
        msg.poses.append(p)
    node._path_cb(msg)
    assert len(node._path) == 8
    node._have_pose = True
    node._pose_stamp = node.get_clock().now()
    node._control_step()
    assert node.sent[-1].header.frame_id == 'nmpc_controller'

"""
test_path_end_stop.py: the speed-target cap that makes the NMPC stop at the end of a
path (control_utils.remaining_path_length / path_end_speed_cap, applied in
nmpc_controller.py after every other speed-target step).
"""
import math

import numpy as np
import pytest

from fsae_control.control_utils import (
    curvature_speed, path_end_speed_cap, remaining_path_length,
)
from fsae_control.mpc.mpc_params import MPCParams
from fsae_control.mpc.nmpc_core import NMPCController
from fsae_control.mpc.nmpc_params import NMPCParams

DT = 0.05
STRAIGHT = np.column_stack([np.arange(0.0, 30.5, 0.5), np.zeros(61)])   # 0 .. 30 m


@pytest.mark.parametrize('x,expected', [(0.0, 30.0), (10.2, 19.8), (29.9, 0.1), (31.0, 0.0)])
def test_remaining_path_length_on_a_straight(x, expected):
    assert remaining_path_length(STRAIGHT, (x, 0.3)) == pytest.approx(expected, abs=1e-6)


def test_cap_is_the_stopping_speed_and_zero_inside_the_margin():
    assert path_end_speed_cap(STRAIGHT, (0.0, 0.0), 0.0, 1.5, 0.5, 1.0) == pytest.approx(
        math.sqrt(2 * 1.5 * 29.5))
    # 2 m/s with a 1 s lag allowance takes 2 m off the remaining distance.
    assert path_end_speed_cap(STRAIGHT, (0.0, 0.0), 2.0, 1.5, 0.5, 1.0) == pytest.approx(
        math.sqrt(2 * 1.5 * 27.5))
    assert path_end_speed_cap(STRAIGHT, (29.7, 0.0), 0.0, 1.5, 0.5, 1.0) == 0.0


def test_zero_decel_disables_the_cap():
    assert path_end_speed_cap(STRAIGHT, (29.9, 0.0), 1.0, 0.0, 0.5, 1.0) == math.inf


def test_nmpc_stops_before_the_end_of_a_straight():
    """Closed loop on the longitudinal axis: the car starts at 3 m/s 20 m from the end and
    follows the NMPC's acceleration command. With the cap it must come to rest before the
    end. Without it, the curvature-only target (v_min floor 1.5 m/s) never lets it stop."""
    ctrl = NMPCController(dt=DT, params=MPCParams(),
                          nmpc=NMPCParams(nmpc_alat_ceiling_enabled=False))
    x, v = 10.0, 3.0
    for _ in range(int(15.0 / DT)):
        target = max(1.5, curvature_speed(STRAIGHT, v_max=3.0, v_min=1.5))
        target = min(target, path_end_speed_cap(STRAIGHT, (x, 0.0), v, 1.5, 0.5, 1.0))
        ctrl.compute(path=STRAIGHT, car_pos=np.array([x, 0.0]), car_yaw=0.0, car_speed=v,
                     desired_speed=target, car_yaw_rate=0.0, car_vy=0.0)
        v = max(0.0, v + ctrl.last_telemetry['a_cmd'] * DT)
        x += v * DT
    assert v < 0.3, f'still moving at {v:.2f} m/s'
    assert x < 30.0, f'ran past the end of the path (x = {x:.2f} m)'
    assert x > 28.5, f'stopped too early (x = {x:.2f} m)'

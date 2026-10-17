"""
test_nmpc_plant_overrides.py: NMPCController's plant_overrides and
max_steer_rad arguments, which the go-kart launch (nmpc_gokart.launch.py)
uses to replace the built-in plant geometry with the kart's.

Checks that omitting them leaves the built-in default plant untouched, that
bad input
is rejected, and that the kart geometry (shorter wheelbase, purely
kinematic model) asks for the kinematic steering angle on a steady arc:
delta = atan(L / R).
"""
import math

import numpy as np
import pytest

from fsae_control.mpc.mpc_params import MPCParams
from fsae_control.mpc.nmpc_core import MAX_STEER_RAD, NMPCController, _Plant
from fsae_control.mpc.nmpc_params import NMPCParams

DT = 0.05
KART = {'lf': 0.86, 'lr': 0.14, 'v_blend_lo': 8.0, 'v_blend_hi': 9.0}


def make(**kw) -> NMPCController:
    return NMPCController(dt=DT, params=MPCParams(),
                          nmpc=NMPCParams(nmpc_alat_ceiling_enabled=False), **kw)


def arc_path(radius: float, arc_deg: float = 120.0, ds: float = 0.25) -> np.ndarray:
    """Left arc starting at the origin heading +X."""
    s = np.arange(0.0, math.radians(arc_deg) * radius, ds)
    return np.column_stack([radius * np.sin(s / radius), radius * (1.0 - np.cos(s / radius))])


def closed_loop_delta(ctrl: NMPCController, wheelbase: float, lr: float, radius: float,
                      speed: float, seconds: float = 10.0) -> float:
    """Mean steering command over the last 3 s of a closed-loop drive round a left arc,
    on a kinematic bicycle whose reference point sits lr ahead of the rear axle (the
    kart's ZED lens). The pose stays static in a single-tick test, so the tracking
    error never builds and the solver's answer is not the steady-state one."""
    path = arc_path(radius, arc_deg=300.0)
    x = y = yaw = d_act = 0.0
    hist = []
    for _ in range(int(seconds / DT)):
        beta = math.atan(lr / wheelbase * math.tan(d_act))
        r = speed * math.cos(beta) * math.tan(d_act) / wheelbase
        ctrl.compute(path=path, car_pos=np.array([x, y]), car_yaw=yaw, car_speed=speed,
                     desired_speed=speed, car_yaw_rate=r, car_vy=speed * math.sin(beta))
        delta = ctrl.last_telemetry['delta_cmd']
        d_act += (delta - d_act) * (1.0 - math.exp(-DT / ctrl.plant.tau_delta))
        x += speed * math.cos(yaw + beta) * DT
        y += speed * math.sin(yaw + beta) * DT
        yaw += r * DT
        hist.append(delta)
    return float(np.mean(hist[-int(3.0 / DT):]))


def steady_delta(ctrl: NMPCController, radius: float, speed: float, ticks: int = 30) -> float:
    path = arc_path(radius)
    delta = 0.0
    for _ in range(ticks):
        ctrl.compute(path=path, car_pos=np.zeros(2), car_yaw=0.0, car_speed=speed,
                     desired_speed=speed, car_yaw_rate=speed / radius, car_vy=0.0)
        delta = ctrl.last_telemetry['delta_cmd']
    return delta


def test_defaults_are_the_built_in_plant():
    ctrl = make()
    assert ctrl.plant == _Plant(alat_ceiling_enabled=False)
    assert ctrl.max_steer_rad == MAX_STEER_RAD


def test_unknown_plant_field_is_rejected():
    with pytest.raises(TypeError):
        make(plant_overrides={'wheelbase': 1.0})


def test_inverted_blend_band_is_rejected():
    with pytest.raises(ValueError):
        make(plant_overrides={'v_blend_lo': 3.0, 'v_blend_hi': 2.0})


def test_max_steer_override_bounds_the_command():
    ctrl = make(plant_overrides=KART, max_steer_rad=math.radians(5.0))
    delta = steady_delta(ctrl, radius=4.0, speed=2.0)
    assert abs(delta) <= math.radians(5.0) + 1e-9


def test_kart_geometry_gives_the_kinematic_arc_angle():
    radius, speed = 6.0, 2.0
    wheelbase = KART['lf'] + KART['lr']
    delta = closed_loop_delta(make(plant_overrides=KART), wheelbase, KART['lr'], radius, speed)
    expected = math.atan(wheelbase / radius)
    assert delta > 0.0, 'left arc must steer left'
    assert abs(delta - expected) < math.radians(1.5), (
        f'settled delta {math.degrees(delta):.2f} deg, kinematic {math.degrees(expected):.2f} deg')

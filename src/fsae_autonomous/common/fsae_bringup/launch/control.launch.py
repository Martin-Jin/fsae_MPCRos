import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import EqualsSubstitution, LaunchConfiguration
from launch_ros.actions import Node

# fsae_control is an installed package by the time `ros2 launch` generates
# this file, so this resolves the same way any node's own
# `from fsae_control.mpc.mpc_params import ...` does.
from fsae_control.mpc.mpc_params import MPC_PARAM_FIELDS
from fsae_control.mpc.nmpc_params import NMPC_PARAM_FIELDS


# Control subsystem: a path-tracking controller. Publishes /fsae/control/cmd_vel
# (+ /fsae/control/accel_cmd when controller=nmpc — see mpc/nmpc_controller.py's
# module docstring) - this is the autonomous command source (see can.launch.py
# for the CAN bridge that consumes it).
#
# Selectable with `controller:=stanley|nmpc`, DEFAULT stanley — launching this
# node is opt-in, and controller:=stanley reproduces exactly today's launch
# behaviour with no change. controller:=nmpc runs the ported nonlinear MPC
# (mpc/nmpc_controller.py); see docs/NMPC_INTEGRATION_GAPS.md before using it
# on the car — several of its inputs (v_x/v_y/yaw_rate) have no real sensor
# source in this repo yet and fall back to a documented degraded estimate.
def generate_launch_description():
    config = os.path.join(get_package_share_directory('fsae_bringup'), 'config', 'fsae_params.yaml')
    controller = LaunchConfiguration('controller')

    # Every MPCParams/NMPCParams field, generated from the same field-metadata
    # tuples the sim tree's control.launch.py uses, so this file, the
    # dataclasses, and fsae_params.yaml's defaults can't silently drift against
    # each other (92 near-identical hand-written args is itself a drift risk).
    def _mpc_launch_arg(name, default, meta):
        unit = meta.get('unit', '')
        desc = meta.get('desc', '')
        suffix = f' ({unit})' if unit and unit != 'unitless' else ''
        default_str = ('true' if default else 'false') if isinstance(default, bool) else str(default)
        return DeclareLaunchArgument(
            name, default_value=default_str,
            description=f'{desc}{suffix} (nmpc only; overrides fsae_params.yaml nmpc_controller.{name})',
        )

    mpc_launch_args = [
        _mpc_launch_arg(name, default, meta) for name, default, meta in MPC_PARAM_FIELDS
    ] + [
        _mpc_launch_arg(name, default, meta) for name, default, meta in NMPC_PARAM_FIELDS
    ]
    mpc_param_configs = {name: LaunchConfiguration(name) for name, _d, _m in MPC_PARAM_FIELDS}
    nmpc_param_configs = {name: LaunchConfiguration(name) for name, _d, _m in NMPC_PARAM_FIELDS}

    run_stanley = UnlessCondition(EqualsSubstitution(controller, 'nmpc'))
    run_nmpc = IfCondition(EqualsSubstitution(controller, 'nmpc'))

    return LaunchDescription([
        DeclareLaunchArgument(
            'controller', default_value='stanley',
            description='stanley (default) | nmpc — path-tracking controller to run. '
                        'See docs/NMPC_INTEGRATION_GAPS.md before using nmpc on the car.'),
        *mpc_launch_args,
        Node(
            package='fsae_control',
            executable='controller',
            name='stanley_controller',
            output='screen',
            parameters=[config],
            condition=run_stanley,
        ),
        Node(
            package='fsae_control',
            executable='nmpc_controller',
            name='nmpc_controller',
            output='screen',
            parameters=[config, {**mpc_param_configs, **nmpc_param_configs}],
            condition=run_nmpc,
        ),
    ])

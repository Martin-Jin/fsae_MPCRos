import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'fsae_can_bridge'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='UoA FSAE',
    maintainer_email='fsae@auckland.ac.nz',
    description='CAN bus bridge - merges gocart_control, gocart_driver and CanTalk',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'ack_to_can_node = fsae_can_bridge.ack_to_can:main',       # from gocart_control
            'can_decoder = fsae_can_bridge.can_decoder_jnano:main',    # from gocart_driver
            'candapter_node = fsae_can_bridge.candapter:main',         # from CanTalk (CAN hardware bridge)
            'as_status_node = fsae_can_bridge.sys_status:main',        # from gocart_control
            'joystick_teleop = fsae_can_bridge.joystick_teleop:main',  # from gocart_control
            'mock_stimulus = fsae_can_bridge.mock_stimulus:main',      # bench testing
            # dropped: trajectory_follower (P-controller) and pure_pursuit - superseded by fsae_control (Stanley)
        ],
    },
)

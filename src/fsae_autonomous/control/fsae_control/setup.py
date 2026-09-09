import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'fsae_control'

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
    description='Lateral/longitudinal control (Stanley controller)',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'controller = fsae_control.stanley_controller:main',
            'nmpc_controller = fsae_control.mpc.nmpc_controller:main',
            'mock_pose_path_publisher = fsae_control.mpc.mock_pose_path_publisher:main',
        ],
    },
)

import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'fsae_planning'

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
    description='Path planning: fasttube, fasttube_without_kalman, and centerline planners',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'fasttube = fsae_planning.fasttube_planner:main',
            'fasttube_without_kalman = fsae_planning.fasttube_without_kalman:main',
            'centerline_planner = fsae_planning.centerline_planner:main',
        ],
    },
)

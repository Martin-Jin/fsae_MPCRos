import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'fsae_mission_control'

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
    description='Mission state machine (ports scrutineering as-is; generalises later)',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'inspection_mission_node = fsae_mission_control.inspection_mission:main',
            # dropped: test_node (scrutineering setup.py referenced scrutineering.test_node which has no source file)
        ],
    },
)

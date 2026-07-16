import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'fsae_bringup'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='UoA FSAE',
    maintainer_email='fsae@auckland.ac.nz',
    description='Top-level launch composition and central YAML configuration for the FSAE autonomous system',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # No nodes - this package only ships launch files and config (Stage 3).
        ],
    },
)

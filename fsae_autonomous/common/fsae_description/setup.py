import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'fsae_description'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        (os.path.join('share', package_name, 'meshes'), glob('meshes/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='UoA FSAE',
    maintainer_email='fsae@auckland.ac.nz',
    description='URDF model and meshes for the FSAE go-kart platform',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # NOTE: old gocart_description had NO entry point for state_publisher (so its
            # launch referenced an unbuilt executable). Added here so it's actually runnable.
            'state_publisher = fsae_description.state_publisher:main',
        ],
    },
)

import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'fsae_visualization'

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
    description='Unified visualization - merges base_tf and the cone-map/path/pure-pursuit visualisers',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'base_tf = fsae_visualization.base_tf:main',                    # from base_tf (now a real /tf broadcaster)
            'cone_map_viz = fsae_visualization.visualise_cone_map:main',    # from cone_map_foxglove_visualiser
            'path_viz = fsae_visualization.visualise_trajectories:main',    # from path_planning_visualiser
            'pursuit_viz = fsae_visualization.visualise_pure_pursuit:main', # from pure_pursuit_visualiser
            # dropped: visualise_trajectories_demo, visualise_action_demo, ImageThrollerNode
        ],
    },
)

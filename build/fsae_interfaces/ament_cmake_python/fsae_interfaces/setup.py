from setuptools import find_packages
from setuptools import setup

setup(
    name='fsae_interfaces',
    version='0.1.0',
    packages=find_packages(
        include=('fsae_interfaces', 'fsae_interfaces.*')),
)

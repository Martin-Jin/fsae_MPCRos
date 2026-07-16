import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


# Robot description / TF: robot_state_publisher + state_publisher. Reuses the URDF-loading
# launch shipped by fsae_description.
def generate_launch_description():
    desc_launch = os.path.join(
        get_package_share_directory('fsae_description'), 'launch', 'urdf_model.launch.py')
    return LaunchDescription([
        IncludeLaunchDescription(PythonLaunchDescriptionSource(desc_launch)),
    ])

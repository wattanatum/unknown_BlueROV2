from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'unknown_bluerov2_nav'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'maps'), glob('maps/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ghosts',
    maintainer_email='ghosts@example.com',
    description='Navigation and localization for unknown BlueROV2.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'odom_to_dvl_twist = unknown_bluerov2_nav.odom_to_dvl_twist:main',
            'odom_to_depth_pose = unknown_bluerov2_nav.odom_to_depth_pose:main',
            'depth_thruster_controller = unknown_bluerov2_nav.depth_thruster_controller:main',
            'odom_tf_publisher = unknown_bluerov2_nav.odom_tf_publisher:main',
            'cmd_vel_thruster_mixer = unknown_bluerov2_nav.cmd_vel_thruster_mixer:main',
            'wait_for_nav_ready = unknown_bluerov2_nav.wait_for_nav_ready:main',
        ],
    },
)

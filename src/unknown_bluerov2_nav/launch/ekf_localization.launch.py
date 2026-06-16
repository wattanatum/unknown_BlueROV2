# Copyright 2026
# Apache-2.0

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    nav_share = get_package_share_directory('unknown_bluerov2_nav')
    ekf_config = os.path.join(nav_share, 'config', 'ekf_dvl_imu_depth.yaml')

    return LaunchDescription([
        Node(
            package='unknown_bluerov2_nav',
            executable='odom_to_dvl_twist',
            name='odom_to_dvl_twist',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'input_odom_topic': '/model/bluerov2/odometry',
                'output_twist_topic': '/dvl/twist',
                'base_frame_id': 'base_link',
            }],
        ),

        Node(
            package='unknown_bluerov2_nav',
            executable='odom_to_depth_pose',
            name='odom_to_depth_pose',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'input_odom_topic': '/model/bluerov2/odometry',
                'output_pose_topic': '/depth/pose',
                'odom_frame_id': 'odom',
            }],
        ),

        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[ekf_config],
            remappings=[
                ('odometry/filtered', '/odometry/filtered'),
            ],
        ),
    ])

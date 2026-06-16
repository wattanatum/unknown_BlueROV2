#!/usr/bin/env python3
# Copyright 2026
# Apache-2.0

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    nav_share = get_package_share_directory('unknown_bluerov2_nav')
    slam_share = get_package_share_directory('slam_toolbox')

    slam_config = os.path.join(
        nav_share,
        'config',
        'slam_toolbox.yaml'
    )

    slam_toolbox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                slam_share,
                'launch',
                'online_async_launch.py'
            )
        ),
        launch_arguments={
            'use_sim_time': 'true',
            'slam_params_file': slam_config,
        }.items()
    )

    return LaunchDescription([
        slam_toolbox,
    ])

#!/usr/bin/env python3
# Copyright 2026
# Apache-2.0

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    depth_controller = Node(
        package='unknown_bluerov2_nav',
        executable='depth_thruster_controller',
        name='depth_thruster_controller',
        output='screen',
        parameters=[{
            'use_sim_time': True,

            'odom_topic': '/odom',

            'thruster5_topic': '/thruster5/cmd_thrust',
            'thruster6_topic': '/thruster6/cmd_thrust',

            # Main target depth while this launch is running
            'mapping_depth_m': 9.0,

            # Safe depth when Ctrl+C is pressed
            'shutdown_depth_m': 2.0,

            # z = -9 means depth 9 m
            'depth_positive_down': True,

            # Change to False if positive thrust makes BlueROV2 go up
            'positive_thrust_moves_down': True,

            # Change to True if thruster5 and thruster6 need opposite signs
            'vertical_thrusters_opposite': False,

            'kp_depth': 20.0,
            'max_thrust': 150.0,
            'min_active_thrust': 20.0,

            'depth_tolerance_m': 0.15,
            'shutdown_timeout_sec': 30.0,
        }],
    )

    return LaunchDescription([
        depth_controller,
    ])

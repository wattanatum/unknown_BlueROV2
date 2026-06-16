#!/usr/bin/env python3
# Copyright 2026
# Apache-2.0

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    mixer = Node(
        package='unknown_bluerov2_nav',
        executable='cmd_vel_thruster_mixer',
        name='cmd_vel_to_thrusters',
        output='screen',
        parameters=[{
            'use_sim_time': True,

            'cmd_vel_topic': '/cmd_vel',

            'thruster1_topic': '/thruster1/cmd_thrust',
            'thruster2_topic': '/thruster2/cmd_thrust',
            'thruster3_topic': '/thruster3/cmd_thrust',
            'thruster4_topic': '/thruster4/cmd_thrust',

            # Exact old working defaults
            'max_thrust': 35.0,
            'linear_gain': 25.0,
            'yaw_gain': 22.0,

            'cmd_timeout_sec': 0.5,
            'control_rate_hz': 20.0,

            't1_forward_sign': -1.0,
            't2_forward_sign': -1.0,
            't3_forward_sign': 1.0,
            't4_forward_sign': 1.0,

            't1_yaw_sign': 1.0,
            't2_yaw_sign': -1.0,
            't3_yaw_sign': -1.0,
            't4_yaw_sign': 1.0,

            'force_forward_only': False,
            'block_rotate_in_place': False,

            'yaw_deadband': 0.03,
            'max_yaw_when_moving': 0.025,
            'yaw_scale_when_moving': 0.30,

            'invert_yaw': True,

            'debug_cmd': False,
            'debug_every_n': 20,
        }],
    )

    return LaunchDescription([
        mixer,
    ])

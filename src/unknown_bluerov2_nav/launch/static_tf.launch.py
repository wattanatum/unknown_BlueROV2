# Copyright 2026
# Apache-2.0

from launch import LaunchDescription
from launch_ros.actions import Node


def static_tf(name, parent, child, x, y, z, roll, pitch, yaw):
    return Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name=name,
        arguments=[
            str(x), str(y), str(z),
            str(roll), str(pitch), str(yaw),
            parent, child
        ],
        parameters=[{
            'use_sim_time': True,
        }],
    )


def generate_launch_description():
    return LaunchDescription([
        static_tf(
            'base_to_imu_tf',
            'base_link',
            'imu_link',
            0.0, 0.0, 0.0,
            0.0, 0.0, 0.0
        ),

        static_tf(
            'base_to_dvl_tf',
            'base_link',
            'dvl_link',
            0.0, 0.0, -0.15,
            0.0, 0.0, 0.0
        ),

        static_tf(
            'base_to_depth_tf',
            'base_link',
            'depth_link',
            0.0, 0.0, -0.1,
            0.0, 0.0, 0.0
        ),

        static_tf(
            'base_to_laser_tf',
            'base_link',
            'laser_link',
            0.25, 0.0, 0.0,
            0.0, 0.0, 0.0
        ),
    ])

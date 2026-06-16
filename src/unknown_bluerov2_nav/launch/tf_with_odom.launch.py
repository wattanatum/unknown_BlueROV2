#!/usr/bin/env python3
# Copyright 2026
# Apache-2.0

from launch import LaunchDescription
from launch_ros.actions import Node


def static_tf(name, parent, child, x, y, z, roll, pitch, yaw):
    return Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name=name,
        output="screen",
        arguments=[
            str(x), str(y), str(z),
            str(roll), str(pitch), str(yaw),
            parent,
            child,
        ],
        parameters=[
            {
                "use_sim_time": True,
            }
        ],
    )


def generate_launch_description():
    base_to_imu_tf = static_tf(
        name="base_to_imu_tf",
        parent="base_link",
        child="imu_link",
        x=0.0,
        y=0.0,
        z=0.0,
        roll=0.0,
        pitch=0.0,
        yaw=0.0,
    )

    base_to_dvl_tf = static_tf(
        name="base_to_dvl_tf",
        parent="base_link",
        child="dvl_link",
        x=0.0,
        y=0.0,
        z=-0.15,
        roll=0.0,
        pitch=0.0,
        yaw=0.0,
    )

    base_to_depth_tf = static_tf(
        name="base_to_depth_tf",
        parent="base_link",
        child="depth_link",
        x=0.0,
        y=0.0,
        z=-0.1,
        roll=0.0,
        pitch=0.0,
        yaw=0.0,
    )

    base_to_laser_tf = static_tf(
        name="base_to_laser_tf",
        parent="base_link",
        child="laser_link",
        x=0.25,
        y=0.0,
        z=0.0,
        roll=0.0,
        pitch=0.0,
        yaw=0.0,
    )

    odom_tf_publisher = Node(
        package="unknown_bluerov2_nav",
        executable="odom_tf_publisher",
        name="odom_tf_publisher",
        output="screen",
        parameters=[
            {
                "use_sim_time": True,
                "odom_topic": "/odom",
                "parent_frame": "odom",
                "child_frame": "base_link",
            }
        ],
    )

    return LaunchDescription(
        [
            base_to_imu_tf,
            base_to_dvl_tf,
            base_to_depth_tf,
            base_to_laser_tf,
            odom_tf_publisher,
        ]
    )

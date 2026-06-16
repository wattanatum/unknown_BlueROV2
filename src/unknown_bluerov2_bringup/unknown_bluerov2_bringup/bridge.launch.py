#!/usr/bin/env python3
# Copyright 2026
# Apache-2.0

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="unknown_bluerov2_bridge",
        output="screen",
        arguments=[
            # Gazebo -> ROS 2
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",

            "/world/bluerov2_underwater/model/bluerov2/link/base_link/sensor/imu_sensor/imu"
            "@sensor_msgs/msg/Imu[gz.msgs.IMU",

            "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",

            "/model/bluerov2/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry",

            # ROS 2 -> Gazebo horizontal thrusters
            "/model/bluerov2/joint/thruster1_joint/cmd_thrust"
            "@std_msgs/msg/Float64]gz.msgs.Double",

            "/model/bluerov2/joint/thruster2_joint/cmd_thrust"
            "@std_msgs/msg/Float64]gz.msgs.Double",

            "/model/bluerov2/joint/thruster3_joint/cmd_thrust"
            "@std_msgs/msg/Float64]gz.msgs.Double",

            "/model/bluerov2/joint/thruster4_joint/cmd_thrust"
            "@std_msgs/msg/Float64]gz.msgs.Double",

            # ROS 2 -> Gazebo vertical thrusters
            "/model/bluerov2/joint/thruster5_joint/cmd_thrust"
            "@std_msgs/msg/Float64]gz.msgs.Double",

            "/model/bluerov2/joint/thruster6_joint/cmd_thrust"
            "@std_msgs/msg/Float64]gz.msgs.Double",
        ],
        remappings=[
            # IMU
            (
                "/world/bluerov2_underwater/model/bluerov2/link/base_link/sensor/imu_sensor/imu",
                "/imu",
            ),

            # ODOM
            (
                "/model/bluerov2/odometry",
                "/odom",
            ),

            # THRUSTERS
            (
                "/model/bluerov2/joint/thruster1_joint/cmd_thrust",
                "/thruster1/cmd_thrust",
            ),
            (
                "/model/bluerov2/joint/thruster2_joint/cmd_thrust",
                "/thruster2/cmd_thrust",
            ),
            (
                "/model/bluerov2/joint/thruster3_joint/cmd_thrust",
                "/thruster3/cmd_thrust",
            ),
            (
                "/model/bluerov2/joint/thruster4_joint/cmd_thrust",
                "/thruster4/cmd_thrust",
            ),
            (
                "/model/bluerov2/joint/thruster5_joint/cmd_thrust",
                "/thruster5/cmd_thrust",
            ),
            (
                "/model/bluerov2/joint/thruster6_joint/cmd_thrust",
                "/thruster6/cmd_thrust",
            ),
        ],
        parameters=[
            {
                "use_sim_time": True,
            }
        ],
    )

    return LaunchDescription([
        bridge,
    ])

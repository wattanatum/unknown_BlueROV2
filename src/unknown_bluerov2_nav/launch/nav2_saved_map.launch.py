#!/usr/bin/env python3
# Copyright 2026
# Apache-2.0

from launch import LaunchDescription
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch_ros.actions import Node


def generate_launch_description():
    params_file = "/home/ghosts/unknown_bluerov2_ws/src/unknown_bluerov2_nav/config/nav2_saved_map_params.yaml"
    map_file = "/home/ghosts/unknown_bluerov2_ws/src/unknown_bluerov2_nav/maps/bluerov2_slam_map.yaml"

    # ============================================================
    # 1. Localization
    # ============================================================

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[
            params_file,
            {
                'use_sim_time': True,
                'yaml_filename': map_file,
            },
        ],
    )

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[
            params_file,
            {
                'use_sim_time': True,

                'base_frame_id': 'base_link',
                'odom_frame_id': 'odom',
                'global_frame_id': 'map',

                'tf_broadcast': True,

                'set_initial_pose': True,
                'always_reset_initial_pose': False,
                'initial_pose': {
                    'x': 0.0,
                    'y': 0.0,
                    'z': 0.0,
                    'yaw': 0.0,
                },

                'scan_topic': '/scan',
                'transform_tolerance': 2.0,
            },
        ],
    )

    lifecycle_manager_localization = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': [
                'map_server',
                'amcl',
            ],
        }],
    )

    # ============================================================
    # 2. Start navigation nodes now, but do NOT activate yet
    #
    # This lets their TF buffers exist before lifecycle activation.
    # The lifecycle manager for navigation starts only after
    # wait_for_nav_ready exits successfully.
    # ============================================================

    controller_server = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=[params_file],
    )

    smoother_server = Node(
        package='nav2_smoother',
        executable='smoother_server',
        name='smoother_server',
        output='screen',
        parameters=[params_file],
    )

    planner_server = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=[params_file],
    )

    behavior_server = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=[params_file],
    )

    bt_navigator = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=[params_file],
    )

    # ============================================================
    # 3. Condition checker
    #
    # This node exits only when:
    #   map_server active
    #   amcl active
    #   odom -> base_link exists
    #   base_link -> laser_link exists
    #   map -> base_link exists
    # ============================================================

    wait_for_nav_ready = Node(
        package='unknown_bluerov2_nav',
        executable='wait_for_nav_ready',
        name='wait_for_nav_ready',
        output='screen',
        parameters=[{
            'use_sim_time': True,

            'map_server_node': '/map_server',
            'amcl_node': '/amcl',

            'global_frame': 'map',
            'odom_frame': 'odom',
            'base_frame': 'base_link',
            'laser_frame': 'laser_link',

            'check_period_sec': 0.25,
            'required_success_count': 8,
        }],
    )

    # ============================================================
    # 4. Navigation lifecycle manager
    #
    # This is not started immediately.
    # It starts only after wait_for_nav_ready exits.
    # ============================================================

    lifecycle_manager_navigation = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': [
                'controller_server',
                'smoother_server',
                'planner_server',
                'behavior_server',
                'bt_navigator',
            ],
        }],
    )

    start_navigation_lifecycle_when_ready = RegisterEventHandler(
        OnProcessExit(
            target_action=wait_for_nav_ready,
            on_exit=[
                lifecycle_manager_navigation,
            ],
        )
    )

    return LaunchDescription([
        # Localization
        map_server,
        amcl,
        lifecycle_manager_localization,

        # Navigation nodes start, but remain inactive
        controller_server,
        smoother_server,
        planner_server,
        behavior_server,
        bt_navigator,

        # Condition checker
        wait_for_nav_ready,

        # Start lifecycle manager after condition is met
        start_navigation_lifecycle_when_ready,
    ])
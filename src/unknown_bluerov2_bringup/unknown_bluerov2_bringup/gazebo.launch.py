#!/usr/bin/env python3

import os

from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable
from launch.substitutions import EnvironmentVariable


def generate_launch_description():
    ws_src = os.path.expanduser("~/unknown_bluerov2_ws/src")
    bluerov2_gz_path = os.path.join(ws_src, "bluerov2_gz")

    models_path = os.path.join(bluerov2_gz_path, "models")
    worlds_path = os.path.join(bluerov2_gz_path, "worlds")

    world_file = os.path.join(worlds_path, "bluerov2_underwater.world")

    gz_resource_path = [
        EnvironmentVariable("GZ_SIM_RESOURCE_PATH", default_value=""),
        ":",
        models_path,
        ":",
        worlds_path,
    ]

    set_gz_resource_path = SetEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value=gz_resource_path,
    )

    gazebo = ExecuteProcess(
        cmd=[
            "gz",
            "sim",
            "-r",          # IMPORTANT: start simulation unpaused/running
            "-v",
            "4",
            world_file,
        ],
        output="screen",
    )

    return LaunchDescription([
        set_gz_resource_path,
        gazebo,
    ])

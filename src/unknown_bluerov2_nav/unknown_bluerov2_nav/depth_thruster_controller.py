#!/usr/bin/env python3
# Copyright 2026
# Apache-2.0

import signal
import threading
import time

import rclpy
from rclpy.node import Node

from nav_msgs.msg import Odometry
from std_msgs.msg import Float64


class DepthThrusterController(Node):
    def __init__(self):
        super().__init__('depth_thruster_controller')

        # Topics
        self.declare_parameter('odom_topic', '/odom')
        self.declare_parameter('thruster5_topic', '/thruster5/cmd_thrust')
        self.declare_parameter('thruster6_topic', '/thruster6/cmd_thrust')

        # Depth targets
        self.declare_parameter('mapping_depth_m', 9.0)
        self.declare_parameter('shutdown_depth_m', 2.0)

        # z = -9 means depth 9 m
        self.declare_parameter('depth_positive_down', True)

        # Change to False if positive thrust makes BlueROV2 go up
        self.declare_parameter('positive_thrust_moves_down', True)

        # Change to True if thruster5 and thruster6 need opposite signs
        self.declare_parameter('vertical_thrusters_opposite', False)

        # Controller gains
        self.declare_parameter('kp_depth', 20.0)
        self.declare_parameter('max_thrust', 150.0)
        self.declare_parameter('min_active_thrust', 20.0)
        self.declare_parameter('depth_tolerance_m', 0.15)
        self.declare_parameter('shutdown_timeout_sec', 30.0)

        self.odom_topic = self.get_parameter('odom_topic').value
        self.thruster5_topic = self.get_parameter('thruster5_topic').value
        self.thruster6_topic = self.get_parameter('thruster6_topic').value

        self.mapping_depth_m = float(self.get_parameter('mapping_depth_m').value)
        self.shutdown_depth_m = float(self.get_parameter('shutdown_depth_m').value)

        self.depth_positive_down = bool(
            self.get_parameter('depth_positive_down').value
        )
        self.positive_thrust_moves_down = bool(
            self.get_parameter('positive_thrust_moves_down').value
        )
        self.vertical_thrusters_opposite = bool(
            self.get_parameter('vertical_thrusters_opposite').value
        )

        self.kp_depth = float(self.get_parameter('kp_depth').value)
        self.max_thrust = float(self.get_parameter('max_thrust').value)
        self.min_active_thrust = float(self.get_parameter('min_active_thrust').value)
        self.depth_tolerance_m = float(self.get_parameter('depth_tolerance_m').value)
        self.shutdown_timeout_sec = float(
            self.get_parameter('shutdown_timeout_sec').value
        )

        self.current_depth = None
        self.target_depth = self.mapping_depth_m

        self.shutdown_requested = False
        self.shutdown_start_time = None

        self.lock = threading.Lock()

        self.thruster5_pub = self.create_publisher(
            Float64,
            self.thruster5_topic,
            10
        )
        self.thruster6_pub = self.create_publisher(
            Float64,
            self.thruster6_topic,
            10
        )

        self.odom_sub = self.create_subscription(
            Odometry,
            self.odom_topic,
            self.odom_callback,
            20
        )

        self.timer = self.create_timer(0.05, self.control_loop)

        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        self.get_logger().info('Depth thruster controller started')
        self.get_logger().info(f'odom_topic: {self.odom_topic}')
        self.get_logger().info(f'thruster5_topic: {self.thruster5_topic}')
        self.get_logger().info(f'thruster6_topic: {self.thruster6_topic}')
        self.get_logger().info(f'mapping_depth_m: {self.mapping_depth_m}')
        self.get_logger().info(f'shutdown_depth_m: {self.shutdown_depth_m}')

    def signal_handler(self, signum, frame):
        with self.lock:
            if not self.shutdown_requested:
                self.shutdown_requested = True
                self.shutdown_start_time = time.time()
                self.target_depth = self.shutdown_depth_m

                self.get_logger().warn(
                    f'Cancel detected. Driving to safe depth '
                    f'{self.shutdown_depth_m:.2f} m before exit.'
                )

    def odom_callback(self, msg: Odometry):
        z = msg.pose.pose.position.z

        if self.depth_positive_down:
            depth = -z
        else:
            depth = z

        with self.lock:
            self.current_depth = depth

    def clamp(self, value, low, high):
        return max(low, min(high, value))

    def publish_thrusters(self, thrust):
        msg5 = Float64()
        msg6 = Float64()

        msg5.data = float(thrust)

        if self.vertical_thrusters_opposite:
            msg6.data = float(-thrust)
        else:
            msg6.data = float(thrust)

        self.thruster5_pub.publish(msg5)
        self.thruster6_pub.publish(msg6)

    def stop_thrusters(self):
        self.publish_thrusters(0.0)

    def control_loop(self):
        with self.lock:
            current_depth = self.current_depth
            target_depth = self.target_depth
            shutdown_requested = self.shutdown_requested
            shutdown_start_time = self.shutdown_start_time

        if current_depth is None:
            self.get_logger().warn(
                f'Waiting for odometry on {self.odom_topic}',
                throttle_duration_sec=2.0
            )
            self.stop_thrusters()
            return

        depth_error = target_depth - current_depth

        if abs(depth_error) <= self.depth_tolerance_m:
            thrust = 0.0
        else:
            # depth_error > 0 means need to go deeper
            thrust = self.kp_depth * depth_error

            if not self.positive_thrust_moves_down:
                thrust = -thrust

            thrust = self.clamp(
                thrust,
                -self.max_thrust,
                self.max_thrust
            )

            if 0.0 < abs(thrust) < self.min_active_thrust:
                if thrust > 0.0:
                    thrust = self.min_active_thrust
                else:
                    thrust = -self.min_active_thrust

        self.publish_thrusters(thrust)

        self.get_logger().info(
            f'depth={current_depth:.2f} m | '
            f'target={target_depth:.2f} m | '
            f'error={depth_error:.2f} | '
            f'thrust={thrust:.2f}',
            throttle_duration_sec=1.0
        )

        if shutdown_requested:
            reached = abs(depth_error) <= self.depth_tolerance_m

            timeout = False
            if shutdown_start_time is not None:
                timeout = (
                    time.time() - shutdown_start_time
                ) >= self.shutdown_timeout_sec

            if reached:
                self.get_logger().warn(
                    f'Safe depth reached: {current_depth:.2f} m. Exiting.'
                )
                self.stop_thrusters()
                rclpy.shutdown()

            elif timeout:
                self.get_logger().error(
                    f'Shutdown timeout. Current depth: {current_depth:.2f} m. '
                    f'Exiting anyway.'
                )
                self.stop_thrusters()
                rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = DepthThrusterController()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_thrusters()
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

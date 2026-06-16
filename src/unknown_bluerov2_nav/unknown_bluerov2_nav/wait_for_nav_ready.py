#!/usr/bin/env python3
# Copyright 2026
# Apache-2.0

import sys

import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.time import Time

from tf2_ros import Buffer, TransformListener


class WaitForNavReady(Node):
    def __init__(self):
        super().__init__('wait_for_nav_ready')

        self.declare_parameter('global_frame', 'map')
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('laser_frame', 'laser_link')

        self.declare_parameter('check_period_sec', 0.25)
        self.declare_parameter('required_success_count', 8)

        self.global_frame = self.get_parameter('global_frame').value
        self.odom_frame = self.get_parameter('odom_frame').value
        self.base_frame = self.get_parameter('base_frame').value
        self.laser_frame = self.get_parameter('laser_frame').value

        self.check_period_sec = float(self.get_parameter('check_period_sec').value)
        self.required_success_count = int(self.get_parameter('required_success_count').value)

        self.success_count = 0
        self.ready = False
        self.print_count = 0

        self.tf_buffer = Buffer(cache_time=Duration(seconds=30.0))
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.timer = self.create_timer(self.check_period_sec, self.check_ready)

        self.get_logger().info('Waiting for saved-map Nav2 TF ready condition...')
        self.get_logger().info('Required TF:')
        self.get_logger().info(f'  {self.odom_frame} -> {self.base_frame}')
        self.get_logger().info(f'  {self.base_frame} -> {self.laser_frame}')
        self.get_logger().info(f'  {self.global_frame} -> {self.base_frame}')

    def can_tf(self, target_frame: str, source_frame: str) -> bool:
        try:
            return self.tf_buffer.can_transform(
                target_frame,
                source_frame,
                Time(),
                timeout=Duration(seconds=0.05),
            )
        except Exception:
            return False

    def check_ready(self):
        odom_to_base_ok = self.can_tf(self.odom_frame, self.base_frame)
        base_to_laser_ok = self.can_tf(self.base_frame, self.laser_frame)
        map_to_base_ok = self.can_tf(self.global_frame, self.base_frame)

        all_ok = (
            odom_to_base_ok
            and base_to_laser_ok
            and map_to_base_ok
        )

        if all_ok:
            self.success_count += 1
        else:
            self.success_count = 0

        self.print_count += 1
        if self.print_count >= 8 or self.success_count > 0:
            self.print_count = 0
            self.get_logger().info(
                'Ready check: '
                f'{self.odom_frame}->{self.base_frame}={int(odom_to_base_ok)}, '
                f'{self.base_frame}->{self.laser_frame}={int(base_to_laser_ok)}, '
                f'{self.global_frame}->{self.base_frame}={int(map_to_base_ok)}, '
                f'success_count={self.success_count}/{self.required_success_count}'
            )

        if self.success_count >= self.required_success_count:
            self.get_logger().info('TF ready condition met. Starting Nav2 lifecycle manager.')
            self.ready = True


def main(args=None):
    rclpy.init(args=args)
    node = WaitForNavReady()

    try:
        while rclpy.ok() and not node.ready:
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass

    ready = node.ready

    node.destroy_node()
    rclpy.shutdown()

    if ready:
        sys.exit(0)

    sys.exit(1)


if __name__ == '__main__':
    main()

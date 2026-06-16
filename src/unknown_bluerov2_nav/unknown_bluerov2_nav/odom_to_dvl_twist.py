# Copyright 2026
# Apache-2.0

import rclpy
from rclpy.node import Node

from nav_msgs.msg import Odometry
from geometry_msgs.msg import TwistWithCovarianceStamped


class OdomToDvlTwist(Node):
    def __init__(self):
        super().__init__('odom_to_dvl_twist')

        self.declare_parameter('input_odom_topic', '/model/bluerov2/odometry')
        self.declare_parameter('output_twist_topic', '/dvl/twist')
        self.declare_parameter('base_frame_id', 'base_link')

        input_topic = self.get_parameter('input_odom_topic').value
        output_topic = self.get_parameter('output_twist_topic').value

        self.pub = self.create_publisher(
            TwistWithCovarianceStamped,
            output_topic,
            10
        )

        self.sub = self.create_subscription(
            Odometry,
            input_topic,
            self.odom_callback,
            10
        )

        self.get_logger().info(f'Converting {input_topic} to {output_topic}')

    def odom_callback(self, msg: Odometry):
        out = TwistWithCovarianceStamped()
        out.header.stamp = msg.header.stamp
        out.header.frame_id = self.get_parameter('base_frame_id').value

        # In simulation we use Gazebo odometry velocity as DVL velocity.
        # EKF will fuse only the twist part.
        out.twist.twist = msg.twist.twist

        # Reasonable covariance for simulated DVL.
        # Lower = trust more, higher = trust less.
        out.twist.covariance = [0.0] * 36
        out.twist.covariance[0] = 0.03   # vx
        out.twist.covariance[7] = 0.03   # vy
        out.twist.covariance[14] = 0.05  # vz
        out.twist.covariance[21] = 999.0
        out.twist.covariance[28] = 999.0
        out.twist.covariance[35] = 999.0

        self.pub.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = OdomToDvlTwist()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

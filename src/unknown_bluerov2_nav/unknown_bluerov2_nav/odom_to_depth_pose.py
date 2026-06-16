# Copyright 2026
# Apache-2.0

import rclpy
from rclpy.node import Node

from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseWithCovarianceStamped


class OdomToDepthPose(Node):
    def __init__(self):
        super().__init__('odom_to_depth_pose')

        self.declare_parameter('input_odom_topic', '/model/bluerov2/odometry')
        self.declare_parameter('output_pose_topic', '/depth/pose')
        self.declare_parameter('odom_frame_id', 'odom')

        input_topic = self.get_parameter('input_odom_topic').value
        output_topic = self.get_parameter('output_pose_topic').value

        self.pub = self.create_publisher(
            PoseWithCovarianceStamped,
            output_topic,
            10
        )

        self.sub = self.create_subscription(
            Odometry,
            input_topic,
            self.odom_callback,
            10
        )

        self.get_logger().info(f'Converting {input_topic} z-position to {output_topic}')

    def odom_callback(self, msg: Odometry):
        out = PoseWithCovarianceStamped()
        out.header.stamp = msg.header.stamp
        out.header.frame_id = self.get_parameter('odom_frame_id').value

        # Only z is used by EKF.
        out.pose.pose.position.z = msg.pose.pose.position.z

        out.pose.covariance = [0.0] * 36
        out.pose.covariance[0] = 999.0
        out.pose.covariance[7] = 999.0
        out.pose.covariance[14] = 0.02   # z/depth
        out.pose.covariance[21] = 999.0
        out.pose.covariance[28] = 999.0
        out.pose.covariance[35] = 999.0

        self.pub.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = OdomToDepthPose()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

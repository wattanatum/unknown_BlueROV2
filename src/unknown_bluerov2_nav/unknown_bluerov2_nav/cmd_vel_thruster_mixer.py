#!/usr/bin/env python3
# Copyright 2026
# Apache-2.0

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from std_msgs.msg import Float64


class CmdVelToThrusters(Node):
    def __init__(self):
        super().__init__("cmd_vel_to_thrusters")

        # -----------------------------
        # Topics
        # -----------------------------
        self.declare_parameter("cmd_vel_topic", "/cmd_vel")

        self.declare_parameter("thruster1_topic", "/thruster1/cmd_thrust")
        self.declare_parameter("thruster2_topic", "/thruster2/cmd_thrust")
        self.declare_parameter("thruster3_topic", "/thruster3/cmd_thrust")
        self.declare_parameter("thruster4_topic", "/thruster4/cmd_thrust")

        # -----------------------------
        # Gains
        # -----------------------------
        self.declare_parameter("max_thrust", 35.0)
        self.declare_parameter("linear_gain", 25.0)
        self.declare_parameter("yaw_gain", 45.0)

        # -----------------------------
        # Timing
        # -----------------------------
        self.declare_parameter("cmd_timeout_sec", 0.5)
        self.declare_parameter("control_rate_hz", 20.0)

        # -----------------------------
        # Forward signs
        # ROS convention:
        # linear.x > 0 = move forward
        # -----------------------------
        self.declare_parameter("t1_forward_sign", -1.0)
        self.declare_parameter("t2_forward_sign", -1.0)
        self.declare_parameter("t3_forward_sign", 1.0)
        self.declare_parameter("t4_forward_sign", 1.0)

        # -----------------------------
        # Yaw signs
        # Base yaw pattern from your Gazebo test:
        # thruster1 = +
        # thruster2 = -
        # thruster3 = -
        # thruster4 = +
        #
        # Because your robot turns right when angular.z > 0,
        # we use invert_yaw=True below.
        # -----------------------------
        self.declare_parameter("t1_yaw_sign", 1.0)
        self.declare_parameter("t2_yaw_sign", -1.0)
        self.declare_parameter("t3_yaw_sign", -1.0)
        self.declare_parameter("t4_yaw_sign", 1.0)

        # -----------------------------
        # Nav2 filters
        # -----------------------------
        self.declare_parameter("force_forward_only", True)

        # Keep False because BlueROV2 must rotate at goal direction.
        self.declare_parameter("block_rotate_in_place", False)

        # Small deadband only. Do not make this too large.
        self.declare_parameter("yaw_deadband", 0.01)

        # Allow yaw while moving.
        self.declare_parameter("max_yaw_when_moving", 0.08)
        self.declare_parameter("yaw_scale_when_moving", 0.80)

        # IMPORTANT:
        # Your test showed:
        # angular.z > 0 makes robot turn right.
        # ROS/Nav2 expects angular.z > 0 to turn left.
        # So this must be True.
        self.declare_parameter("invert_yaw", True)

        # Debug log every N control loops
        self.declare_parameter("debug_cmd", False)
        self.declare_parameter("debug_every_n", 20)

        # -----------------------------
        # Read parameters
        # -----------------------------
        self.cmd_vel_topic = self.get_parameter("cmd_vel_topic").value

        self.thruster1_topic = self.get_parameter("thruster1_topic").value
        self.thruster2_topic = self.get_parameter("thruster2_topic").value
        self.thruster3_topic = self.get_parameter("thruster3_topic").value
        self.thruster4_topic = self.get_parameter("thruster4_topic").value

        self.max_thrust = float(self.get_parameter("max_thrust").value)
        self.linear_gain = float(self.get_parameter("linear_gain").value)
        self.yaw_gain = float(self.get_parameter("yaw_gain").value)

        self.cmd_timeout_sec = float(self.get_parameter("cmd_timeout_sec").value)
        self.control_rate_hz = float(self.get_parameter("control_rate_hz").value)

        self.t1_forward_sign = float(self.get_parameter("t1_forward_sign").value)
        self.t2_forward_sign = float(self.get_parameter("t2_forward_sign").value)
        self.t3_forward_sign = float(self.get_parameter("t3_forward_sign").value)
        self.t4_forward_sign = float(self.get_parameter("t4_forward_sign").value)

        self.t1_yaw_sign = float(self.get_parameter("t1_yaw_sign").value)
        self.t2_yaw_sign = float(self.get_parameter("t2_yaw_sign").value)
        self.t3_yaw_sign = float(self.get_parameter("t3_yaw_sign").value)
        self.t4_yaw_sign = float(self.get_parameter("t4_yaw_sign").value)

        self.force_forward_only = bool(
            self.get_parameter("force_forward_only").value
        )
        self.block_rotate_in_place = bool(
            self.get_parameter("block_rotate_in_place").value
        )
        self.yaw_deadband = float(self.get_parameter("yaw_deadband").value)
        self.max_yaw_when_moving = float(
            self.get_parameter("max_yaw_when_moving").value
        )
        self.yaw_scale_when_moving = float(
            self.get_parameter("yaw_scale_when_moving").value
        )
        self.invert_yaw = bool(self.get_parameter("invert_yaw").value)

        self.debug_cmd = bool(self.get_parameter("debug_cmd").value)
        self.debug_every_n = int(self.get_parameter("debug_every_n").value)
        self.debug_count = 0

        self.last_cmd = Twist()
        self.last_cmd_time = None

        # -----------------------------
        # ROS interfaces
        # -----------------------------
        self.cmd_sub = self.create_subscription(
            Twist,
            self.cmd_vel_topic,
            self.cmd_callback,
            10,
        )

        self.t1_pub = self.create_publisher(Float64, self.thruster1_topic, 10)
        self.t2_pub = self.create_publisher(Float64, self.thruster2_topic, 10)
        self.t3_pub = self.create_publisher(Float64, self.thruster3_topic, 10)
        self.t4_pub = self.create_publisher(Float64, self.thruster4_topic, 10)

        self.timer = self.create_timer(
            1.0 / self.control_rate_hz,
            self.control_loop,
        )

        self.print_startup_info()

    def print_startup_info(self):
        self.get_logger().info("cmd_vel_to_thrusters started.")
        self.get_logger().info(f"Subscribing: {self.cmd_vel_topic}")
        self.get_logger().info(f"Publishing: {self.thruster1_topic}")
        self.get_logger().info(f"Publishing: {self.thruster2_topic}")
        self.get_logger().info(f"Publishing: {self.thruster3_topic}")
        self.get_logger().info(f"Publishing: {self.thruster4_topic}")

        self.get_logger().info(
            "Forward signs: "
            f"t1={self.t1_forward_sign}, "
            f"t2={self.t2_forward_sign}, "
            f"t3={self.t3_forward_sign}, "
            f"t4={self.t4_forward_sign}"
        )

        self.get_logger().info(
            "Yaw signs: "
            f"t1={self.t1_yaw_sign}, "
            f"t2={self.t2_yaw_sign}, "
            f"t3={self.t3_yaw_sign}, "
            f"t4={self.t4_yaw_sign}"
        )

        self.get_logger().info(
            "Nav2 filters: "
            f"force_forward_only={self.force_forward_only}, "
            f"block_rotate_in_place={self.block_rotate_in_place}, "
            f"yaw_deadband={self.yaw_deadband}, "
            f"max_yaw_when_moving={self.max_yaw_when_moving}, "
            f"yaw_scale_when_moving={self.yaw_scale_when_moving}, "
            f"invert_yaw={self.invert_yaw}"
        )

        self.get_logger().info(
            f"Gains: linear_gain={self.linear_gain}, "
            f"yaw_gain={self.yaw_gain}, "
            f"max_thrust={self.max_thrust}"
        )

    def cmd_callback(self, msg: Twist):
        self.last_cmd = msg
        self.last_cmd_time = self.get_clock().now()

    def clamp(self, value):
        return max(-self.max_thrust, min(self.max_thrust, value))

    def publish_thrusters(self, t1, t2, t3, t4):
        msg1 = Float64()
        msg2 = Float64()
        msg3 = Float64()
        msg4 = Float64()

        msg1.data = float(self.clamp(t1))
        msg2.data = float(self.clamp(t2))
        msg3.data = float(self.clamp(t3))
        msg4.data = float(self.clamp(t4))

        self.t1_pub.publish(msg1)
        self.t2_pub.publish(msg2)
        self.t3_pub.publish(msg3)
        self.t4_pub.publish(msg4)

    def stop_thrusters(self):
        self.publish_thrusters(0.0, 0.0, 0.0, 0.0)

    def filter_cmd_vel(self, linear_x, yaw_z):
        raw_linear_x = linear_x
        raw_yaw_z = yaw_z

        # Do not allow Nav2 to command reverse movement.
        if self.force_forward_only and linear_x < 0.0:
            linear_x = 0.0

        # Invert yaw to match ROS convention.
        if self.invert_yaw:
            yaw_z = -yaw_z

        # Remove very small yaw noise.
        if abs(yaw_z) < self.yaw_deadband:
            yaw_z = 0.0

        # Optional block rotate-in-place.
        if self.block_rotate_in_place:
            if abs(linear_x) < 0.015 and abs(yaw_z) > 0.0:
                yaw_z = 0.0

        # While moving forward, allow yaw but limit it.
        if abs(linear_x) >= 0.015:
            yaw_z = yaw_z * self.yaw_scale_when_moving

            if yaw_z > self.max_yaw_when_moving:
                yaw_z = self.max_yaw_when_moving
            elif yaw_z < -self.max_yaw_when_moving:
                yaw_z = -self.max_yaw_when_moving

        # When not moving, allow slow rotate-to-heading.
        else:
            max_yaw_rotate_in_place = 0.18

            if yaw_z > max_yaw_rotate_in_place:
                yaw_z = max_yaw_rotate_in_place
            elif yaw_z < -max_yaw_rotate_in_place:
                yaw_z = -max_yaw_rotate_in_place

        if self.debug_cmd:
            self.debug_count += 1
            if self.debug_count >= self.debug_every_n:
                self.debug_count = 0
                self.get_logger().info(
                    "cmd filter: "
                    f"raw linear_x={raw_linear_x:.3f}, raw yaw_z={raw_yaw_z:.3f} -> "
                    f"filtered linear_x={linear_x:.3f}, filtered yaw_z={yaw_z:.3f}"
                )

        return linear_x, yaw_z

    def control_loop(self):
        if self.last_cmd_time is None:
            self.stop_thrusters()
            return

        now = self.get_clock().now()
        age = (now - self.last_cmd_time).nanoseconds / 1e9

        if age > self.cmd_timeout_sec:
            self.stop_thrusters()
            return

        linear_x = float(self.last_cmd.linear.x)
        yaw_z = float(self.last_cmd.angular.z)

        linear_x, yaw_z = self.filter_cmd_vel(linear_x, yaw_z)

        forward_cmd = self.linear_gain * linear_x
        yaw_cmd = self.yaw_gain * yaw_z

        t1 = self.t1_forward_sign * forward_cmd + self.t1_yaw_sign * yaw_cmd
        t2 = self.t2_forward_sign * forward_cmd + self.t2_yaw_sign * yaw_cmd
        t3 = self.t3_forward_sign * forward_cmd + self.t3_yaw_sign * yaw_cmd
        t4 = self.t4_forward_sign * forward_cmd + self.t4_yaw_sign * yaw_cmd

        self.publish_thrusters(t1, t2, t3, t4)


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelToThrusters()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.stop_thrusters()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

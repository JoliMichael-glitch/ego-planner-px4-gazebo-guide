#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSDurabilityPolicy, QoSHistoryPolicy
from std_msgs.msg import String


class KeyPublisher(Node):
    def __init__(self):
        super().__init__('key_publisher')

        # QoS profile matching the offboard_control subscriber (BEST_EFFORT)
        qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            durability=QoSDurabilityPolicy.VOLATILE,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10
        )
        self.pub = self.create_publisher(String, '/mode_key', qos_profile)

        self.get_logger().info("键盘指令发布节点启动，等待输入字母...")
        self.get_logger().info("支持的命令: t=起飞悬停, p=位置控制, o=offboard控制, l=降落, d=上锁(disarm), m=手动")

    def run(self):
        while rclpy.ok():
            key = input("请输入字母并回车 >>> ").strip()

            if not key:
                continue

            # 发布消息
            msg = String()
            msg.data = key
            self.pub.publish(msg)

            # 打印 info
            self.get_logger().info(f"已发布字母：{key}")

            # 对不同字母打印不同提示
            if key == 't':
                self.get_logger().info("takeoff and hover command sent (自动起飞悬停)")
            elif key == 'm':
                self.get_logger().info("manual control command sent (手动控制)")
            elif key == 'p':
                self.get_logger().info("position hold command sent (位置保持)")
            elif key == 'o':
                self.get_logger().info("offboard control command sent (Offboard控制)")
            elif key == 'l':
                self.get_logger().info("land control command sent (降落)")
            elif key == 'd':
                self.get_logger().info("disarm command sent (上锁)")
            else:
                self.get_logger().warn(f"unknown command: {key}, 支持的按键: t/p/o/l/d/m")


def main(args=None):
    rclpy.init(args=args)
    node = KeyPublisher()

    try:
        node.run()
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

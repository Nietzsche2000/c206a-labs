import sys
import termios
import tty
import select
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

HELP = """
Controls:
  w/s: linear +/-    a/d: angular +/-
  x  : stop          h  : help
  q  : quit
"""

def getch_nonblocking():
    """Return a single char if available (non-blocking), else ''."""
    dr, _, _ = select.select([sys.stdin], [], [], 0.0)
    if dr:
        return sys.stdin.read(1)
    return ''

class TurtleTeleop(Node):
    def __init__(self, turtle_name: str):
        super().__init__('turtle_controller_' + turtle_name)
        topic = f'/{turtle_name}/cmd_vel'
        self.pub = self.create_publisher(Twist, topic, 10)
        self.lin = 0.0
        self.ang = 0.0
        self.get_logger().info(f'Publishing Twist to {topic}')
        self.get_logger().info(HELP)
        # 20 Hz timer to publish continuously
        self.timer = self.create_timer(0.05, self.tick)

    def tick(self):
        ch = getch_nonblocking()
        if ch:
            if ch == 'w':
                self.lin += 0.5
            elif ch == 's':
                self.lin -= 0.5
            elif ch == 'a':
                self.ang += 0.5
            elif ch == 'd':
                self.ang -= 0.5
            elif ch == 'x':
                self.lin = 0.0; self.ang = 0.0
            elif ch == 'h':
                self.get_logger().info(HELP)
            elif ch == 'q':
                rclpy.shutdown()
                return
            self.get_logger().info(f'lin={self.lin:.2f} ang={self.ang:.2f}')

        msg = Twist()
        msg.linear.x = self.lin
        msg.angular.z = self.ang
        self.pub.publish(msg)

def main():
    if len(sys.argv) < 2:
        print("Usage: ros2 run lab2_turtlesim turtle_controller <turtle_name>")
        return
    turtle_name = sys.argv[1]

    # put terminal into raw mode for keypresses
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        rclpy.init()
        node = TurtleTeleop(turtle_name)
        rclpy.spin(node)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

if __name__ == '__main__':
    main()

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist

class TaskDRotateToZero(Node):
    def __init__(self):
        super().__init__('task_d_rotation')
        
        # Listen to Task C
        self.error_sub = self.create_subscription(Float64, '/horizontal_error', self.error_callback, 10)
        # Command the wheels
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Sensitivity (Kp)
        self.kp = 0.001 
        self.last_error = 0.0
        
        self.get_logger().info("Task D Started: Rotating until error is 0...")

    def error_callback(self, msg):
        try:
            error = msg.data
            twist = Twist()
            
            # RULE 1: We are ONLY rotating. No driving forward.
            twist.linear.x = 0.0  
            
            if error == 9999.0:
                # Target lost, spin to find it
                if self.last_error > 0:
                    twist.angular.z = 0.2  
                else:
                    twist.angular.z = -0.2 
                self.get_logger().info("Target lost. Searching...")
                
            else:
                self.last_error = error
                
                # ========================================================
                # RULE 2: ROTATE UNTIL ERROR IS 0
                # We use 2.0 pixels as our "Zero" to prevent the robot 
                # from violently shaking trying to find perfect microscopic 0.
                # ========================================================
                if abs(error) <= 2.0:
                    twist.angular.z = 0.0
                    self.get_logger().info("Error is 0! Robot centered and stopped.")
                
                # If the error is NOT 0, keep rotating!
                else:
                    # Calculate speed: Big error = fast spin. Small error = slow spin.
                    raw_speed = error * self.kp
                    
                    # Safety limit: Never spin faster than 0.25 so we don't overshoot
                    safe_speed = max(-0.25, min(0.25, raw_speed)) 
                    
                    twist.angular.z = safe_speed
                    self.get_logger().info(f"Rotating... Current Error: {error:.1f}")
            
            self.publisher_.publish(twist)
            
        except Exception as e:
            self.get_logger().error(f"Failed to steer robot: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = TaskDRotateToZero()
    rclpy.spin(node)
    node.destroy_node()

if __name__ == '__main__':
    main()

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import math

class TaskELidarController(Node):
    def __init__(self):
        super().__init__('task_e_lidar')
        
        # 1. Listen to Task C for the horizontal error
        self.error_sub = self.create_subscription(Float64, '/horizontal_error', self.error_callback, 10)
        
        # 2. Listen to the LiDAR for collision avoidance
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        
        # 3. Command the wheels
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.kp = 0.001 
        self.last_error = 0.0  
        
        # Distance tracking
        self.front_distance = 999.0  
        self.stop_distance = 0.40    # Stop 40cm away from the object
        
        self.get_logger().info("Task E (LiDAR) Controller Started!")

    def scan_callback(self, msg):
        # Index 0 is the laser pointing exactly straight ahead
        dist = msg.ranges[0]
        
        # Safety check for sensor glitches
        if math.isinf(dist) or math.isnan(dist) or dist <= 0.0:
            self.front_distance = 999.0
        else:
            self.front_distance = dist

    def error_callback(self, msg):
        try:
            error = msg.data
            twist = Twist()
            
            # SEARCH MODE (Target Lost)
            if error == 9999.0:
                twist.linear.x = 0.0
                if self.last_error > 0:
                    twist.angular.z = 0.2  
                else:
                    twist.angular.z = -0.2 
                self.get_logger().info("Target lost. Searching...")
                
            # TARGET FOUND
            else:
                self.last_error = error
                
                # Calculate safe steering speed
                raw_steering = error * self.kp
                safe_steering = max(-0.25, min(0.25, raw_steering))
                twist.angular.z = safe_steering
                
                # ========================================================
                # TASK E LOGIC: COLLISION AVOIDANCE & DRIVING
                # ========================================================
                
                # PRIORITY 1: LiDAR COLLISION AVOIDANCE
                # If we are closer than 40cm, cut all motors immediately.
                if self.front_distance < self.stop_distance:
                    twist.linear.x = 0.0
                    twist.angular.z = 0.0 
                    self.get_logger().info(f"COLLISION AVOIDED! Stopped at distance: {self.front_distance:.2f}m")
                
                # PRIORITY 2: ERROR IS SMALL -> MOVE TOWARDS OBJECT
                # If the sphere is within 20 pixels of the center, hit the gas!
                elif abs(error) < 20.0:
                    twist.linear.x = 0.05   
                    self.get_logger().info(f"Error is small ({error:.1f}). Moving towards object! (LiDAR: {self.front_distance:.2f}m)")
                
                # PRIORITY 3: ERROR IS LARGE -> ROTATE ONLY
                # If it's too far to the side, don't drive yet. Just rotate.
                else:
                    twist.linear.x = 0.0    
                    self.get_logger().info(f"Centering... Error: {error:.1f}")
            
            self.publisher_.publish(twist)
            
        except Exception as e:
            self.get_logger().error(f"Failed to control robot: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = TaskELidarController()
    rclpy.spin(node)
    node.destroy_node()

if __name__ == '__main__':
    main()

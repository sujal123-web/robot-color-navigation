import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import math

class LidarMethod1(Node):
    def __init__(self):
        super().__init__('lidar_method1')
        
        # Subscribe to the Camera for Steering
        self.error_sub = self.create_subscription(Float64, '/horizontal_error', self.error_callback, 10)
        
        # Subscribe to the LiDAR for Distance tracking
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Stabilized Steering Sensitivity
        self.kp = 0.001 
        self.last_error = 0.0  
        
        # LiDAR VARIABLES
        self.front_distance = 999.0
        self.stop_threshold = 0.40  # Stop exactly 40cm away from the sphere
        
        self.get_logger().info("Method 1 (LiDAR) Controller Started!")

    def scan_callback(self, msg):
        # Index 0 is the laser beam pointing exactly straight ahead
        dist = msg.ranges[0]
        
        # Clean the data: If the laser shoots into the sky, it returns 'inf'
        if math.isinf(dist) or math.isnan(dist) or dist <= 0.0:
            self.front_distance = 999.0
        else:
            self.front_distance = dist

    def error_callback(self, msg):
        try:
            error = msg.data
            twist = Twist()
            
            # TASK F: SEARCH MODE (Target Lost)
            if error == 9999.0:
                twist.linear.x = 0.0
                if self.last_error > 0:
                    twist.angular.z = 0.2  
                else:
                    twist.angular.z = -0.2 
                
            # NORMAL TRACKING & STOPPING
            else:
                self.last_error = error
                
                # Stabilized steering calculation
                raw_steering = error * self.kp
                safe_steering = max(-0.25, min(0.25, raw_steering)) # Clamp speed to prevent ping-ponging
                twist.angular.z = safe_steering
                
                # STOPPING LOGIC: True LiDAR Distance
                if self.front_distance < self.stop_threshold:
                    twist.linear.x = 0.0
                    twist.angular.z = 0.0 
                    self.get_logger().info(f"LIDAR STOP! Target reached. (Distance remaining: {self.front_distance:.2f}m)")
                
                # Move forward if centered
                elif abs(error) < 20.0:
                    twist.linear.x = 0.05   
                    self.get_logger().info(f"Approaching... LiDAR distance: {self.front_distance:.2f}m")
                
                # Steer in place if off-center
                else:
                    twist.linear.x = 0.0    
                    self.get_logger().info(f"Aligning to center... Error: {error:.1f}")
            
            self.publisher_.publish(twist)
            
        except Exception as e:
            self.get_logger().error(f"Failed to control robot: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = LidarMethod1()
    rclpy.spin(node)
    node.destroy_node()

if __name__ == '__main__':
    main()

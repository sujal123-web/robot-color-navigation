import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Float64
from cv_bridge import CvBridge
import cv2
import numpy as np

class TaskCVisionNode(Node):
    def __init__(self):
        super().__init__('task_c_vision')
        self.subscription = self.create_subscription(Image, '/camera/image_raw', self.image_callback, 10)
        
        self.error_publisher = self.create_publisher(Float64, '/horizontal_error', 10)
        self.area_publisher = self.create_publisher(Float64, '/blob_area', 10)
        
        self.bridge = CvBridge()
        self.get_logger().info("Task C Vision Node Started! Looking for green...")

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
            
            # Green color limits in HSV
            lower_green = np.array([40, 50, 50])
            upper_green = np.array([80, 255, 255])
            mask = cv2.inRange(hsv_image, lower_green, upper_green)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            error_msg = Float64()
            area_msg = Float64()
            
            if len(contours) > 0:
                largest_contour = max(contours, key=cv2.contourArea)
                
                # Filter out tiny specks of noise
                blob_area = cv2.contourArea(largest_contour)
                if blob_area > 500:  
                    area_msg.data = float(blob_area)
                    self.area_publisher.publish(area_msg)
                    
                    M = cv2.moments(largest_contour)
                    if M["m00"] > 0:
                        cX = int(M["m10"] / M["m00"])
                        image_center_x = cv_image.shape[1] // 2
                        
                        # Calculate the Horizontal Error
                        error = float(image_center_x - cX)
                        
                        error_msg.data = error
                        self.error_publisher.publish(error_msg)
                        
                        # PRINT IT TO THE TERMINAL!
                        self.get_logger().info(f"Target Locked! Error: {error:.1f} | Area: {blob_area:.0f}")
                        
                        cv2.circle(cv_image, (cX, int(M["m01"] / M["m00"])), 5, (0, 0, 255), -1)
            else:
                # Target Lost
                error_msg.data = 9999.0
                self.error_publisher.publish(error_msg)
                area_msg.data = 0.0
                self.area_publisher.publish(area_msg)
                
                # PRINT THAT IT IS BLIND!
                self.get_logger().info("Target LOST! (Error: 9999.0)")
            
            # Show the normal camera view
            cv2.imshow("Task C: Camera View", cv_image)
            # NEW: Show the black-and-white Mask view to prove it sees green!
            cv2.imshow("Task C: Mask View", mask) 
            cv2.waitKey(1)
            
        except Exception as e:
            self.get_logger().error(f"Error: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = TaskCVisionNode()
    rclpy.spin(node)
    node.destroy_node()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

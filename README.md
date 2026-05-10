# robot-color-navigation
This project implements an autonomous navigation stack for a mobile robot in a simulated environment. The system utilizes Computer Vision for object detection and LiDAR-based control for safe navigation. The robot is programmed to track a green sphere and halt automatically when it reaches a safe distance.

**How to Run the Project**:
1) Launch the simulation
   First, set up the TurtleBot3 environment and launch the custom world containing the green sphere:
   export TURTLEBOT3_MODEL=waffle_pi
   ros2 launch color_navigation sim_with_sphere.launch.py
2) Implementation Task:
  Command,Task,Description
i) ros2 run turtlebot3_teleop teleop_keyboard,Task A (Part 1),Keyboard Control: Manually drive the robot to test the physics and motor response.

ii) rqt,Task A (Part 2),RQT Visualization: Open the GUI to view /camera/image_raw and monitor topic frequencies.

iii) ros2 run color_navigation run_task_b,Task B,Camera Interface: Accesses and displays the raw robot camera feed.

iv) ros2 run color_navigation run_task_c,Task C,Vision Processing: Applies HSV masks to isolate the green sphere.

v) ros2 run color_navigation run_task_d,Task D,Basic Motion: Moves the robot toward the detected object.

vi) ros2 run color_navigation run_task_e_lidar,Task E,Autonomous Logic: Integrated tracking with LiDAR safety stopping.

vii) ros2 run color_navigation run_lidar_method1,Safety Node,Collision Avoidance: Direct LiDAR-to-CMD_VEL emergency stop logic.


   **Technical Implementation:**
1) Computer Vision (Tasks B & C)
Library: OpenCV
Method: The robot uses an RGB-D camera to capture frames. We convert the frames from BGR to HSV color space.
Detection: A mask is created to filter the green color of the sphere. The centroid of the mask determines the robot's steering direction.
2) Lidar Safety(Task E and Method 1) 
Sensor: LaserScan (/scan)
Logic: The code monitors the front 10° arc of the robot.
Auto-Stop: If the minimum distance detected by the LiDAR falls below 0.40 meters, the controller overrides the movement and sends a zero-velocity command to prevent a collision.
3) Control Logic (Task D)
Algorithm: Proportional Control (P-Controller).
Behavior: The robot calculates the error between the center of the image and the center of the green sphere to adjust its angular velocity.
4) Task A: Manual Verification 
Teleop: Using the I-J-K-L-M keys, I verified that the robot navigates the hospital environment correctly and that the Gazebo physics engine handles collisions realistically.

rqt_image_view: I used this tool to confirm that the camera plugin is active and publishing data on the correct ROS2 topic before running the OpenCV scripts.

rqt_graph: Used to visualize the node connections, ensuring the /cmd_vel and /scan topics were properly linked between the simulation and my custom nodes.

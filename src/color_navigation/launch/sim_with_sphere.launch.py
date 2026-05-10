import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Start the standard TurtleBot3 empty world
    tb3_gazebo_dir = get_package_share_directory('turtlebot3_gazebo')
    start_gazebo_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(tb3_gazebo_dir, 'launch', 'empty_world.launch.py')
        )
    )

    # 2. Spawn your custom green sphere
    # Make sure this path matches where Gazebo saved your sphere!
    sphere_path = '/home/sujal/model_editor_models/unit_sphere/model.sdf'
    
    spawn_sphere_cmd = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'target_sphere',
            '-file', sphere_path,
            '-x', '2.5',   # 1 meter in front
            '-y', '0.0',   # Centered
            '-z', '0.15'   # Lifted off the ground
        ],
        output='screen'
    )

    # Launch both of them together!
    return LaunchDescription([
        start_gazebo_cmd,
        spawn_sphere_cmd
    ])

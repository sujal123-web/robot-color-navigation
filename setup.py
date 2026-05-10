from setuptools import find_packages, setup
import os 
from glob import glob 

package_name = 'color_navigation'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch','*launch.[pxy][yma]*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sujal',
    maintainer_email='sujal@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': ['run_task_b = color_navigation.task_b_camera:main','run_task_c = color_navigation.task_c_vision:main','run_task_d = color_navigation.task_d_controller:main','run_lidar_method1 = color_navigation.lidar_method1:main','run_task_e_lidar = color_navigation.task_e_lidar:main',
        ],
    },
)

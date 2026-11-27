from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    drone_id = LaunchConfiguration('drone_id', default='0')

    return LaunchDescription([
        DeclareLaunchArgument('drone_id', default_value='0',
                              description='Drone ID (must match ego_planner drone_id)'),
        Node(
            package='px4_ego_agent',
            executable='px4_ego_agent_node',
            namespace='px4_1',
            parameters=[
                {'system_id': 2},
                {'pos_cmd_topic': ['/drone_', drone_id, '_planning/pos_cmd']}
            ]
        )
    ])

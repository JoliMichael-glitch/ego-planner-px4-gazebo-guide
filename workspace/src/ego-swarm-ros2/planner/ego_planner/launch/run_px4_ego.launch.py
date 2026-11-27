import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    """
    一键启动: Gazebo + PX4 + MAVROS + ego-planner
    自动等 PX4/EKF2 初始化完成后启动规划器
    """

    # ── 1. PX4 仿真环境（Gazebo + MAVROS + PX4 SITL + DDS + 深度相机）──
    px4_sitl_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(os.path.expanduser('~'),
                         'PX4-Autopilot/launch/px4_sitl_ros2.launch.py')
        )
    )

    # ── 2. ego-planner（延迟 25 秒，等 EKF2 收敛 + MAVROS 就绪）──
    ego_planner_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ego_planner'),
                         'launch/single_uav_gazebo.launch.py')
        )
    )

    ego_planner_delayed = TimerAction(
        period=25.0,
        actions=[ego_planner_launch]
    )

    return LaunchDescription([
        px4_sitl_launch,
        ego_planner_delayed,
    ])

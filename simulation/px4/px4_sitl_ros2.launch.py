from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node

import os


def generate_launch_description():

    home_dir = os.path.expanduser('~')

    # ================================================================
    # 1. Gazebo Simulation (ego world)
    #    Starts Gazebo Harmonic with the ego obstacle course world.
    #    Runs via simulation-gazebo which sets GZ_SIM_RESOURCE_PATH
    #    and GZ_SIM_SERVER_CONFIG_PATH, then launches gz sim.
    # ================================================================
    gazebo_simulation_cmd = ExecuteProcess(
        cmd=[
            'python3',
            os.path.join(home_dir, 'ros_proj/gazebo_start/simulation-gazebo'),
            '--world', 'ego',
        ],
        output='screen'
    )

    # ================================================================
    # 2. MAVROS
    #    Bridges MAVLink <-> ROS 2 for offboard control / monitoring.
    # ================================================================
    mavros_start_cmd = ExecuteProcess(
        cmd=['ros2', 'launch', 'mavros', 'px4.launch',
             'fcu_url:=udp://:14540@127.0.0.1:14580'],
        output='both',
        shell=True
    )

    # ================================================================
    # 3. PX4 SITL (delayed — waits for Gazebo to be ready)
    #
    #    PX4_GZ_STANDALONE=1  →  PX4 connects to the already-running
    #    Gazebo server and spawns the x500_depth model via gz transport.
    #
    #    Delayed 8 seconds so the ego world has time to fully load
    #    before PX4 attempts to spawn the vehicle.
    # ================================================================
    PX4_DIR = os.path.expanduser('~/PX4-Autopilot')
    PX4_BIN = os.path.join(PX4_DIR, 'build/px4_sitl_default/bin/px4')

    px4_instance0 = ExecuteProcess(
        cmd=[PX4_BIN, '-i', '0'],
        additional_env={
            'PX4_GZ_STANDALONE': '1',
            'PX4_SYS_AUTOSTART': '4002',
            'PX4_GZ_MODEL_POSE': '0,0,0,0,0,0',
            'PX4_SIM_MODEL': 'gz_x500_depth'
        },
        output='screen'
    )

    px4_delayed = TimerAction(
        period=8.0,
        actions=[px4_instance0]
    )

    # ================================================================
    # 4. Micro XRCE DDS Agent (PX4 <-> ROS 2 DDS bridge)
    # ================================================================
    micro_xrce_start_cmd = ExecuteProcess(
        cmd=['MicroXRCEAgent', 'udp4', '-p', '8888'],
        shell=False,
        output='screen'
    )

    # ================================================================
    # 5. Depth camera bridge (Gazebo -> ROS 2)
    # ================================================================
    depth_bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='depth_camera_bridge',
        arguments=[
            '/depth_camera@sensor_msgs/msg/Image@gz.msgs.Image',
        ],
        output='screen'
    )

    # ================================================================
    # 6. Best-effort depth image publisher
    # ================================================================
    best_effort_depth_img_pub = ExecuteProcess(
        cmd=[
            'python3',
            os.path.join(home_dir, 'ros_proj/gazebo_start/depth_gz_bridge.py'),
        ],
        output='screen'
    )

    # ================================================================
    # Launch sequence:
    #   1. Gazebo (ego world)     — starts immediately
    #   2. MAVROS                 — starts immediately
    #   3. PX4 SITL               — starts after 8s (Gazebo ready)
    #   4. Micro XRCE Agent       — starts immediately
    #   5. Depth bridge           — starts immediately
    #   6. Best-effort depth pub  — starts immediately
    # ================================================================
    return LaunchDescription([
        gazebo_simulation_cmd,
        mavros_start_cmd,
        px4_delayed,
        micro_xrce_start_cmd,
        depth_bridge_node,
        best_effort_depth_img_pub,
    ])

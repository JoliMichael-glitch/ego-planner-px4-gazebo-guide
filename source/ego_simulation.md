# ego\_simulation

# ego\-planner\-ros2\-sim 仿真启动流程（PX4 \+ Gazebo Harmonic \+ Ego Planner）

## 环境确认

已安装：

- Ubuntu 22\.04 

- ROS2 Humble 

- PX4 Firmware ≥ 1\.14\.0 

- PX4\-Autopilot 

- Gazebo Harmonic 

- Micro XRCE Agent 

- px4\_msgs 

- px4\_ego 

- ego\-swarm\-ros2 

- ego\-planner\-ros2\-sim 

VMware建议：

```Plain Text
CPU: 6核
RAM: 16GB
3D加速: 关闭（Gazebo Harmonic兼容问题）
```

---

# 启动 Gazebo 仿真环境（舍）

## Terminal 1

启动 Gazebo world：

```Plain Text
cd ~/ros_proj/gazebo_start

python3 simulation-gazebo
```

确认：

```Plain Text
gz model --list
```

应该出现：

```Plain Text
x500_depth_0



```

说明无人机模型加载成功。

---

# 启动 PX4 SITL

## Terminal 2

进入PX4：

```Plain Text
cd ~/PX4-Autopilot

```

启动：

```Plain Text
ros2 launch ./launch/px4_sitl_ros2.launch.py
```

作用：

```Plain Text
PX4 SITL
    ↓
Gazebo
    ↓
x500_depth无人机
```

检查：

```Plain Text
gz model --list
```

应该有：

```Plain Text
x500_depth_0
```

---

# 启动 Micro XRCE Agent（舍）

## Terminal 3

启动PX4 ROS2通信桥：

```Plain Text
micro-xrce-dds-agent udp4 -p 8888
```

正常：

看到：

```Plain Text
查看8888端口占用
执行：
sudo lsof -i :8888
正常运行时：
COMMAND     PID USER   FD   TYPE DEVICE NAME
MicroXRCE  3407 ros2   3u   UDP  *:8888
看到：
MicroXRCE
       *
       ↓
      UDP *:8888
说明：
✅ Micro XRCE Agent正在监听8888端口
```

```Plain Text
Client connected


#Step 1 — 启动 PX4-ROS2 通信桥（MicroXRCEAgent）：

  MicroXRCEAgent udp4 -p 8888

#Step 2 —（新终端） 编译并 source planner workspace：


  cd /home/ros2/planner_ws
  colcon build
  source install/setup.bash

#Step 3 — 启动 Ego Planner 状态机：（px4飞控与ego之间的中间控制层，state machine）

  ros2 run px4_ego_py offboard_control_test

```

作用：

```Plain Text
PX4
 |
uXRCE-DDS
 |
Micro XRCE Agent
 |
ROS2
```

---

# 启动 px4\_ego 控制节点

## Terminal 4

加载工作空间：

```Plain Text
source ~/planner_ws/install/setup.bash
```

启动控制节点：

```Plain Text
ros2 run px4_ego_py offboard_control_test
```

注意：

此时无人机不会自动运动。

当前状态：

```Plain Text
PX4
 ↑
等待外部轨迹
 ↑
px4_ego
```



---

# 键盘控制起飞 \+ Offboard

## Terminal 5

进入：

```Plain Text
cd ~/planner_ws/src/px4_ego
```

运行：

```Plain Text
python3 mode_key.py
```

操作：

### 第一步：起飞

按：

```Plain Text
t
```

效果：

```Plain Text
ARM
↓
Takeoff
↓
悬停
```

---

### 第二步：进入Offboard

等待无人机稳定悬停后：

按：

```Plain Text
o
```

效果：

```Plain Text
PX4
AUTO.LOITER
      ↓
OFFBOARD
```

此时等待规划轨迹。

---

# 启动 Ego Planner（启动px4后约25s启动）

## Terminal 6

加载环境：

```Plain Text
source ~/planner_ws/install/setup.bash
```

启动规划器：

```Plain Text
ros2 launch ego_planner single_uav_gazebo.launch.py


#未知仿真
ros2 launch ego_planner single_run_in_sim.launch.py
```

作用：

启动：

- 地图构建 

- ESDF 

- 局部路径规划 

- 轨迹优化 

---

# 启动 RViz

## Terminal 7

加载环境：

```Plain Text
source ~/planner_ws/install/setup.bash
```

启动：

```Plain Text
ros2 launch ego_planner rviz.launch.py
```

---

# 发布目标点

RViz：

选择：

```Plain Text
2D Goal Pose
```

点击目标位置。

数据流：

```Plain Text
RViz
 ↓
Ego Planner
 ↓
trajectory
 ↓
px4_ego
 ↓
px4_msgs
 ↓
PX4
 ↓
Gazebo
 ↓
无人机运动
```

---

# 完整启动顺序（必须）

```Plain Text
① Gazebo
      ↓
② PX4 SITL
      ↓
③ Micro XRCE Agent
      ↓
④ px4_ego控制状态机
      ↓
⑤ mode_key.py
      ↓
⑥ t 起飞
      ↓
⑦ o 进入Offboard
      ↓
⑧ Ego Planner
      ↓
⑨ RViz发送目标点
```

---

# 常用检查命令

## 查看Gazebo模型

```Plain Text
gz model --list
```

应该：

```Plain Text
x500_depth_0
```

---

## 查看ROS2节点

```Plain Text
ros2 node list
```

---

## 查看PX4 ROS2话题

```Plain Text
ros2 topic list | grep px4
```

应出现：

```Plain Text
/fmu/in/trajectory_setpoint
/fmu/out/vehicle_local_position
```

---

## 查看Offboard状态

PX4终端应显示：

```Plain Text
OFFBOARD
```

---

# 最终目标

实现：

```Plain Text
Gazebo环境
      ↓
PX4 SITL控制无人机
      ↓
Ego Planner规划避障轨迹
      ↓
PX4 Offboard执行
      ↓
x500_depth自主飞行
```

[2026\-07\-23 19\-21\-43\.mp4](../assets/videos/2026-07-23%2019-21-43.mp4)

[2026\-07\-23 19\-26\-37\.mp4](../assets/videos/2026-07-23%2019-26-37.mp4)






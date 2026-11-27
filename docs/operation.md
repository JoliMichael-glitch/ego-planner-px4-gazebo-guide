> 历史手册整理版：实际虚拟机代码已导出，启动顺序与 t/o 行为以 [仓库首页](../README.md) 和 [源码核对记录](vm-source-findings.md) 为准。下文保留原记录供对照。

# 按终端启动流程

本节保留原实操的启动方法，供以后复现。前提是已完成[环境检查](recovery.md)，并确认当前集成入口包含 Gazebo 和 Micro XRCE Agent。文档整理期间没有执行以下启动操作。

## 每个新终端先加载环境

```bash
source /opt/ros/humble/setup.bash
source ~/planner_ws/install/setup.bash
```

不要仅在一个终端 source 后，默认其他终端也具有相同环境。

## 终端 1：集成启动

```bash
cd ~/PX4-Autopilot
ros2 launch ./launch/px4_sitl_ros2.launch.py
```

共享压缩包里的入口包含 MAVROS、Gazebo、PX4 实例 0、MicroXRCEAgent、深度图桥接和 depth_gz_bridge.py。第二个 PX4 实例及雷达相关节点在该版本中未加入实际启动列表。

因此，确认虚拟机使用同一逻辑后，不再另外执行 `python3 simulation-gazebo` 或 `MicroXRCEAgent udp4 -p 8888`。原手册将这两项标注为“舍”，应理解为独立启动步骤省略，而不是系统不再需要这两个组件。

检查模型：

```bash
gz model --list
```

原记录预期出现 `x500_depth_0`。同时启动多个进程并不保证依赖全部就绪，应结合终端日志检查连接与数据。

## 终端 2：控制状态机

加载环境后运行：

```bash
ros2 run px4_ego_py offboard_control_test
```

它负责规划器与 PX4 之间的控制衔接，不等同于规划器本身。原记录描述此阶段等待后续指令和轨迹。

## 终端 3：键盘控制

加载环境后运行：

```bash
cd ~/planner_ws/src/px4_ego
python3 mode_key.py
```

1. 按 `t`，按原记录触发解锁与起飞。
2. 等待无人机稳定悬停。
3. 按 `o`，请求切换 Offboard。
4. 查看飞控反馈确认切换成功。

按键含义以当前 mode_key.py 为准；按下按键不代表飞控一定接受请求。

## 终端 4：EGO Planner

加载环境后运行：

```bash
ros2 launch ego_planner single_uav_gazebo.launch.py
```

原手册记录在 PX4 启动约 25 秒后启动规划器。这是当时的经验等待时间，仍需确认定位、深度图和必要状态已经就绪。

原文另列 `single_run_in_sim.launch.py` 并标注“未知仿真”。这里不将它当作 Gazebo 入口的替代项，也不同时启动两套规划入口。

## 终端 5：RViz 与目标点

加载环境后运行：

```bash
ros2 launch ego_planner rviz.launch.py
```

按原手册，在 RViz 中使用 `2D Goal Pose` 设置目标。确认画面中的轨迹和无人机状态变化；实际工具名称、目标话题和 Fixed Frame 需与现有 RViz 配置一致。

## 顺序速记

```text
集成入口（Gazebo / PX4 / 通信桥）
  → px4_ego 控制状态机
  → mode_key.py：t 起飞 → 稳定悬停 → o 请求 Offboard
  → EGO Planner
  → RViz 设置目标
```

运行后保留日志，便于判断是环境启动、通信、控制状态还是规划数据出现问题。停止仿真时结束各个启动终端中的进程，避免下次重复占用端口。

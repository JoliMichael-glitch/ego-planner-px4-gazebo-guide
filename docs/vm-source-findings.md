# 虚拟磁盘内 EGO Planner 读取记录

读取日期：2026-11-26。来源：`E:/虚拟机new-center/Ubuntu 64 位.vmdk`，由 `center.vmx` 引用。

通过只读文件句柄解析 VMDK、GPT 和 Linux ext 文件系统，没有启动虚拟机、挂载为可写卷、编译或运行仿真。读取前后磁盘文件大小均为 40,126,578,688 字节，最后修改时间均为 2026-11-24 20:54:28（本机文件时间显示）。没有计算整个 40 GB 磁盘的哈希。

共提取 390 个相关源码、启动、配置和说明文件，约 2.29 MB。此目录是筛选后的读取快照，不是完整可部署工作空间；未导出个人配置、认证目录、完整依赖、构建产物或大体积模型资源。各文件来源、修改时间和 SHA-256 见 manifest.json；工作空间软链接见 workspace-links.json。

## 1. 实际工作空间

`/home/ros2/planner_ws/src` 同时包含：

- `ego-swarm-ros2`：规划器、轨迹处理、地图和模拟器代码。
- `px4_ego`：Python 控制状态机和键盘控制脚本。
- `ego-planner-ros2-sim`：仿真集成相关材料。
- `ego_planner_ros_humble-main`：另一套项目目录，本次未完整导出。

`ego_planner` 是指向 `ego-swarm-ros2/planner/ego_planner` 的软链接；`px4_ego_py` 指向 `px4_ego/src/px4_ego_py`。两套原始规划项目目录均有 COLCON_IGNORE，工作空间顶层有拆分出来的包软链接。不能因为原目录有 COLCON_IGNORE，就认定所有包都不会被构建。

安装目录中的 `single_uav_gazebo.launch.py` 也以软链接指向上述源码入口，证实当前安装文件与这份源码有关联；这不等于已验证二进制与全部源码同步。

## 2. 集成启动文件已经修改

实际文件：`/home/ros2/PX4-Autopilot/launch/px4_sitl_ros2.launch.py`。

与此前共享压缩包不同，虚拟机版本明确：

- 通过 `simulation-gazebo --world ego` 加载 ego 世界。
- Gazebo 启动后定时延迟 8 秒再启动 PX4。定时器不是就绪检测。
- `PX4_SYS_AUTOSTART=4002`，模型 `gz_x500_depth`。
- 初始模型位姿 `0,0,0,0,0,0`。
- MAVROS 参数为 `fcu_url:=udp://:14540@127.0.0.1:14580`。
- 同时启动 MicroXRCEAgent（UDP 8888）、深度图桥和深度图转发脚本。

因此不应再按共享压缩包的旧值 4001、初始位置 -6,0 或目标端口 14555 描述这台虚拟机的当前配置。

## 3. 找到了更简化的启动入口

文件：`planner_ws/src/ego-swarm-ros2/planner/ego_planner/launch/run_px4_ego.launch.py`。

它先包含 PX4 的集成启动文件，再通过 TimerAction 在 25 秒后启动 `single_uav_gazebo.launch.py`。它没有启动 Python 控制状态机、mode_key.py 或 RViz。

下面是依据代码整理的候选流程，仅供后续验证，本次没有执行：

每个新终端先加载：

```bash
source /opt/ros/humble/setup.bash
source ~/planner_ws/install/setup.bash
```

终端 1，仿真环境加延时规划器：

```bash
ros2 launch ego_planner run_px4_ego.launch.py
```

终端 2，控制状态机：

```bash
ros2 run px4_ego_py offboard_control_test
```

终端 3，键盘命令：

```bash
cd ~/planner_ws/src/px4_ego
python3 mode_key.py
```

输入 `t` 后按回车，等待并检查起飞状态；需要跟随规划轨迹时输入 `o` 后按回车。脚本使用 input()，不是即时单键监听。

终端 4，显示与目标：

```bash
ros2 launch ego_planner rviz.launch.py
```

这条方案已经包含规划器，不能再同时启动另一份 PX4 集成入口或 `single_uav_gazebo.launch.py`。

## 4. t 和 o 的实际含义

`px4_ego/src/px4_ego_py/px4_ego_py/offboard_control_test.py` 中的定时循环为 0.02 秒（目标 50 Hz）。

`t` 分支按计数推进：发送约 3 秒解锁命令；发送约 1 秒位置目标；主动请求 Offboard；随后发布起飞悬停目标。标准本地定位分支的目标 z 为 -0.9（NED 坐标，约为本地原点上方 0.9 米）。阶段转换按计数推进，日志写出某阶段不等于飞控已经接受全部命令。

`o` 分支检查 MAVROS 的解锁和模式状态；没有规划指令时保持位置，有规划指令且处于 Offboard 时调用 ego_cmd_pub() 跟随规划输出。因此旧说明“t 起飞，o 才首次进入 Offboard”不准确。

键盘脚本还展示 p/l/d/m 命令，其最终控制行为需要以状态机对应分支为准。

## 5. 主要话题与默认参数

| 用途 | 实际读取到的配置 |
|---|---|
| 规划器里程计输入 | /mavros/local_position/odom |
| 深度图输入 | /depth_camera_bestef |
| 深度图转发链路 | /depth_camera → /depth_camera_bestef |
| 规划轨迹控制命令 | /drone_0_planning/pos_cmd |
| 键盘命令 | /mode_key |
| 手动目标 | /goal_pose |
| 规划入口默认地图尺寸 | 10 × 10 × 4 |
| max_vel / max_acc | 0.8 / 1.0 |
| planning_horizon | 7.5 |
| flight_type | 1，对应 MANUAL_TARGET |
| 地图分辨率 | 0.1 |

默认值来自 launch 源码，并非运行时参数转储。single_drone.rviz 设置 Fixed Frame 为 map，目标工具话题为 /goal_pose。

控制状态机同时订阅部分标准与带版本后缀的 PX4 状态话题，并读取 /mavros/state 和 /mavros/local_position/pose。它比“只依赖 DDS 状态”的简化描述更复杂。

深度图转发脚本用传感器 QoS 发布输出，重写时间戳并把 frame_id 设置为 odom；数据按 float32 图像解析。实际图像编码、坐标系与 QoS 的正确性还需运行时核对。

## 6. 另一条仿真入口的用途

`single_run_in_sim.launch.py` 包含随机地图节点、轨迹服务器、RViz 和内部 simulator.launch.py。它属于仓库内部模拟器路线，与 PX4/Gazebo 集成入口不同；不应把它当作同一流程的另一个步骤同时启动。

另有 `/home/ros2/ego_sim_launch.sh`，它设置 `GZ_SIM_RENDER_ENGINE=ogre` 并加载 `ego_ogre2.sdf`，只负责 Gazebo。脚本头部写 Ogre2，实际环境变量却是 ogre，说明注释与配置存在不一致，不能把它直接替代完整集成入口。

## 7. 本次结论的边界

已经读取到真实虚拟磁盘中的源码，而非只依据手册或宿主机 ZIP。现在可以确认工作空间结构、启动文件内容和控制分支逻辑，但不能据此认定完整仿真已恢复成功。

GitHub 和 CSDN 文稿仍是之前按手册整理的版本，本次未改动任何线上内容。后续更新时应优先修正：25 秒定时入口、t/o 含义、键盘回车操作、ego 世界与端口参数，以及另一套仿真入口的区别。

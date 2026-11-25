# 环境与现有项目恢复

本节用于找回已经配置过的虚拟机，不要求从零安装。先检查已有目录，再决定是否编译。

## 1. 打开原虚拟机

原机器记录的 Windows 入口：`E:\虚拟机-center\center.vmx`。

该配置引用 `E:\虚拟机new-center\Ubuntu 64 位.vmdk`。迁移到其他机器后，应以实际磁盘位置为准，保留原盘备份后再处理路径。

配置记录为 Ubuntu 22.04.5 LTS、8 个虚拟 CPU、8 GB 内存。手册建议 6 核、16 GB、关闭 3D 加速；它与实际配置不同，不是已经验证过的最低要求。图形兼容问题需结合实际 VMware 和驱动版本检查。

## 2. 找回目录

在 Ubuntu 终端运行：

```bash
whoami
cat /etc/os-release
ls -ld ~/PX4-Autopilot ~/planner_ws ~/ros_proj/gazebo_start
ls -l ~/PX4-Autopilot/launch/px4_sitl_ros2.launch.py
ls -l ~/PX4-Autopilot/build/px4_sitl_default/bin/px4
ls -l ~/ros_proj/gazebo_start/simulation-gazebo
ls -l ~/ros_proj/gazebo_start/depth_gz_bridge.py
ls -l ~/planner_ws/src/px4_ego/mode_key.py
ls -l ~/planner_ws/install/setup.bash
```

原记录曾使用 `/home/ros2/planner_ws`；`~` 必须对应保存项目的用户主目录。找不到文件时先搜索，不直接覆盖原项目：

```bash
find ~ -maxdepth 6 -type f \
  \( -name px4_sitl_ros2.launch.py -o -name mode_key.py \
     -o -name single_uav_gazebo.launch.py \) 2>/dev/null
```

## 3. 加载环境并确认软件包

```bash
source /opt/ros/humble/setup.bash
source ~/planner_ws/install/setup.bash
ros2 pkg prefix ego_planner
ros2 pkg prefix px4_ego_py
ros2 pkg prefix px4_msgs
command -v MicroXRCEAgent
```

能找到包说明当前终端环境可以解析对应包，不代表仿真已经运行成功。若 overlay 文件不存在，先确认工作空间位置和源码。

## 4. 核对集成入口

```bash
sed -n '1,260p' ~/PX4-Autopilot/launch/px4_sitl_ros2.launch.py
```

本地共享压缩包的对应启动文件包含 MAVROS、Gazebo 启动脚本、PX4、MicroXRCEAgent 和深度图桥接。虚拟机内的实际文件需与此核对；不能仅凭文件名判断它包含哪些进程。

检查脚本引用的 `~/ros_proj/gazebo_start` 和 PX4 二进制路径均存在。原入口使用 `gz_x500_depth`；不要将其他模型的传感器话题直接套用到该入口。

## 5. 必要时才编译

源码修改、编译产物缺失或失效时，按原手册编译：

```bash
source /opt/ros/humble/setup.bash
cd ~/planner_ws
colcon build
source install/setup.bash
```

这是会写入工作空间的操作；保留源码改动，优先依据编译错误补齐具体依赖。日常启动无需每次重新编译。

## 恢复检查表

- [ ] 虚拟机打开的是原磁盘。
- [ ] PX4 二进制、启动入口和 Gazebo 脚本存在。
- [ ] planner_ws 的源码与环境脚本存在。
- [ ] ego_planner、px4_ego_py、px4_msgs 可被当前终端识别。
- [ ] 已核对实际启动文件包含的进程。

完成以上检查表示恢复了启动所需的文件与环境入口；运行验证见下一篇操作流程。

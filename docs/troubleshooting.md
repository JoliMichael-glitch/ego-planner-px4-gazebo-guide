> 历史手册整理版：实际虚拟机代码已导出，启动顺序与 t/o 行为以 [仓库首页](../README.md) 和 [源码核对记录](vm-source-findings.md) 为准。下文保留原记录供对照。

# 问题排查与手册修正

## 包找不到

先在当前终端加载 `/opt/ros/humble/setup.bash` 和正确工作空间的 `install/setup.bash`。确认用户名和目录，不要直接将其他工作空间的同名包混入当前环境。

## 8888 端口被占用

```bash
sudo lsof -i UDP:8888
```

若集成入口已经启动 Agent，不再另开一个。监听端口只说明进程存在；通信还需看客户端连接日志与话题数据。原文混用了 `micro-xrce-dds-agent` 与 `MicroXRCEAgent`，本地启动文件使用后者，以实际安装为准。

## 查不到 PX4 话题

原手册使用 `grep px4`，却期待匹配 `/fmu/...`。修正为：

```bash
ros2 topic list | grep '/fmu/'
ros2 topic echo /fmu/out/vehicle_local_position --once
```

原文示例包括 `/fmu/in/trajectory_setpoint` 和 `/fmu/out/vehicle_local_position`。命令等待消息时可用 Ctrl+C 退出；是否有消息与其内容是否有效是两个检查点。

## 有 Gazebo 窗口但没有模型

检查 PX4 进程及模型加载日志。仅启动 Gazebo world 不能独立证明 PX4 对应模型已经生成。原入口配置 `gz_x500_depth`，手册预期模型名 `x500_depth_0`。

## 有模型但没有规划轨迹

```bash
ros2 node list
ros2 topic list
```

依次确认控制状态、规划器节点、定位和深度图消息、RViz 目标话题。具体重映射、坐标系和 QoS 需读取当前工作空间配置，不能仅依据节点存在就认定链路正常。

## 两个规划入口如何选择

本手册主线使用 `single_uav_gazebo.launch.py`。`single_run_in_sim.launch.py` 在原文中尚未明确用途，核对源码前不加入主线。

## 原记录与当前证据边界

| 项目 | 整理结论 |
|---|---|
| 单独启动 Gazebo / Agent | 若集成入口包含它们，则省略重复步骤 |
| PX4 后等待约 25 秒 | 保留为原实操经验，不替代就绪检查 |
| ESDF 功能描述 | 尚未核对实际规划代码，不作为已启用功能声明 |
| VMware 6 核 / 16 GB 建议 | 与曾读取的 8 vCPU / 8 GB 配置不同 |
| 虚拟机内源码 | 尚未从虚拟磁盘读取，不声称与共享压缩包完全一致 |
| 当前复现状态 | 本次仅整理文件，没有重新运行仿真 |

原始材料在 [source](../source/ego_simulation.md) 中保留，便于对照上述修正。

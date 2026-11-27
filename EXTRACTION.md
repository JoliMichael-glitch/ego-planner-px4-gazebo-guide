# 导出说明

2026-11-27 从 center.vmx 关联的 Ubuntu VMDK 只读提取。

完整导出 planner_ws/src（排除 .git、.claude、.vscode、缓存与 build/install/log 目录），包括另一套 ego_planner_ros_humble-main。附带实际 Gazebo 脚本、worlds、server.config、PX4 launch 和 x500_depth → x500 → x500_base / OakD-Lite 模型依赖。仅将工作空间内部绝对软链接改为相对链接，源码内容不做自动修复。

大模型文件装入 resources/model-assets.tar.xz，恢复后可按 SOURCE_MANIFEST.json 校验 SHA-256。EXCLUDED.json 记录排除的元数据和缓存目录。没有包含个人主目录配置或认证文件。未编译、未运行仿真。

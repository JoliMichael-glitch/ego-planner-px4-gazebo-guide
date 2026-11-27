#!/bin/bash
# ============================================================
# EGO-Planner Gazebo 仿真启动脚本
# 世界: ego_ogre2 (20m x 20m 障碍物场地 + X500 无人机)
# Gazebo 版本: gz-sim 8 (Harmonic) + Ogre2 渲染
# ============================================================

# 使用 OGRE1 渲染引擎 (替代默认的 OGRE2)
# OGRE2 的着色器管线与 VM 虚拟显卡不兼容导致白屏/黑屏，
# OGRE1 使用固定管线，对 VM 兼容性好很多
export GZ_SIM_RENDER_ENGINE=ogre

SIMULATION_DIR="$HOME/.simulation-gazebo"

# 设置 Gazebo 资源路径 (models, worlds, server.config)
export GZ_SIM_RESOURCE_PATH="${SIMULATION_DIR}/models:${GZ_SIM_RESOURCE_PATH}"
export GZ_SIM_SERVER_CONFIG_PATH="${SIMULATION_DIR}/server.config"

echo "============================================"
echo " EGO-Planner Gazebo Simulation"
echo "============================================"
echo " World:   ego_ogre2"
echo " Models:  ${SIMULATION_DIR}/models"
echo " Server:  ${SIMULATION_DIR}/server.config"
echo "============================================"

# 启动 Gazebo
gz sim -r -v 4 "${SIMULATION_DIR}/worlds/ego_ogre2.sdf"

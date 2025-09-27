#!/bin/bash

# NEUSteel Agent 生产环境启动脚本
# 用于在 agent.hamaiqiji.xyz 上启动应用

set -e

echo "🚀 启动 NEUSteel Agent 生产环境..."

# 检查是否在项目根目录
if [ ! -d "backend" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 检查静态文件是否存在
if [ ! -d "backend/static" ] || [ ! -f "backend/static/index.html" ]; then
    echo "⚠️  静态文件不存在，请先运行构建脚本:"
    echo "   ./build.sh"
    exit 1
fi

# 检查环境变量文件
if [ ! -f "backend/.env" ]; then
    echo "❌ 环境变量文件不存在: backend/.env"
    echo "请创建并配置环境变量文件"
    exit 1
fi

# 进入后端目录
cd backend

# 检查Python虚拟环境
if [ -d "../.venv" ]; then
    echo "🐍 激活虚拟环境..."
    source ../.venv/bin/activate
elif [ -d "venv" ]; then
    echo "🐍 激活虚拟环境..."
    source venv/bin/activate
fi

# 检查依赖
echo "📦 检查Python依赖..."
pip install -r requirements.txt

# 启动应用
echo "🌟 启动 NEUSteel Agent..."
echo "📍 域名: https://agent.hamaiqiji.xyz"
echo "🔧 API健康检查: https://agent.hamaiqiji.xyz/health"
echo ""

# 使用生产级配置启动
uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --access-log \
    --log-level info

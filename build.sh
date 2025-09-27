#!/bin/bash

# NEUSteel Agent 构建脚本
# 用于同源部署到 agent.hamaiqiji.xyz

set -e  # 遇到错误立即退出

echo "🚀 开始构建 NEUSteel Agent..."

# 检查是否在项目根目录
if [ ! -f "package.json" ] && [ ! -d "frontend" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 清理之前的构建
echo "🧹 清理之前的构建文件..."
rm -rf backend/static

# 构建前端
echo "📦 构建前端应用..."
cd frontend

# 安装依赖（如果需要）
if [ ! -d "node_modules" ]; then
    echo "📥 安装前端依赖..."
    npm install
fi

# 构建生产版本
echo "🔨 构建生产版本..."
npm run build

cd ..

# 检查构建结果
if [ -d "backend/static" ] && [ -f "backend/static/index.html" ]; then
    echo "✅ 前端构建成功！"
    echo "📁 静态文件已输出到: backend/static/"
    
    # 显示构建文件
    echo "📋 构建文件列表:"
    ls -la backend/static/
else
    echo "❌ 前端构建失败！"
    exit 1
fi

echo ""
echo "🎉 构建完成！"
echo ""
echo "📝 部署说明:"
echo "1. 确保后端依赖已安装: pip install -r backend/requirements.txt"
echo "2. 配置环境变量: backend/.env"
echo "3. 启动应用: cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo "4. 访问地址: https://agent.hamaiqiji.xyz"
echo ""
echo "🔧 开发模式:"
echo "- 前端开发: cd frontend && npm run dev"
echo "- 后端开发: cd backend && uvicorn app.main:app --reload"

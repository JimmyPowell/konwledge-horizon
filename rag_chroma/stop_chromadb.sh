#!/bin/bash

# ChromaDB 停止脚本

CONTAINER_NAME="chromadb-persistent"

echo "🛑 停止 ChromaDB 服务..."

if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    docker stop $CONTAINER_NAME
    echo "✅ ChromaDB 服务已停止"
else
    echo "⚠️  容器 $CONTAINER_NAME 未在运行"
fi

# 显示容器状态
echo ""
echo "容器状态:"
docker ps -a --filter name=$CONTAINER_NAME

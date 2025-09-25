#!/bin/bash

# ChromaDB 持久化启动脚本

CONTAINER_NAME="chromadb-persistent"
DATA_DIR="./chroma_data"
PORT=8002
IMAGE="chromadb/chroma:0.5.23"

echo "🚀 启动 ChromaDB 持久化服务..."

# 检查是否已有同名容器在运行
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "⚠️  容器 $CONTAINER_NAME 已在运行"
    echo "容器状态:"
    docker ps --filter name=$CONTAINER_NAME
    exit 0
fi

# 检查是否有停止的同名容器
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "🔄 发现已停止的容器，正在重启..."
    docker start $CONTAINER_NAME
else
    # 创建数据目录
    echo "📁 创建数据目录: $DATA_DIR"
    mkdir -p $DATA_DIR
    
    # 启动新容器
    echo "🆕 启动新的持久化容器..."
    docker run -d \
        --name $CONTAINER_NAME \
        -p $PORT:8000 \
        -v $(pwd)/$DATA_DIR:/chroma/chroma \
        -e CHROMA_SERVER_NOFILE=65536 \
        --restart unless-stopped \
        $IMAGE
fi

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 3

# 检查服务状态
if curl -s http://localhost:$PORT/api/v2/heartbeat > /dev/null; then
    echo "✅ ChromaDB 服务启动成功!"
    echo "🌐 访问地址: http://localhost:$PORT"
    echo "📊 数据目录: $DATA_DIR"
    echo ""
    echo "现在可以运行 RAG 应用:"
    echo "python run.py"
else
    echo "❌ 服务启动失败，请检查日志:"
    echo "docker logs $CONTAINER_NAME"
fi

#!/usr/bin/env python3
"""
ChromaDB 连接测试脚本
用于诊断连接问题
"""

import os
import sys
from pathlib import Path

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

import chromadb
from chromadb.config import Settings
from rich.console import Console
from rich.panel import Panel

console = Console()

def test_chromadb_connection():
    """测试 ChromaDB 连接"""
    console.print("[bold blue]🔍 测试 ChromaDB 连接...[/bold blue]")
    
    host = "localhost"
    port = 8002
    
    try:
        # 创建客户端
        console.print(f"正在连接到 {host}:{port}...")
        
        settings = Settings(
            anonymized_telemetry=False,
            allow_reset=True,
            is_persistent=False
        )
        
        client = chromadb.HttpClient(
            host=host,
            port=port,
            settings=settings,
        )
        
        # 测试心跳
        console.print("测试心跳...")
        heartbeat = client.heartbeat()
        console.print(f"[green]✅ 心跳成功: {heartbeat}[/green]")
        
        # 列出现有集合
        console.print("获取集合列表...")
        collections = client.list_collections()
        console.print(f"[green]✅ 找到 {len(collections)} 个集合[/green]")
        
        for collection in collections:
            console.print(f"  - {collection.name}")
            
        # 测试创建集合
        test_collection_name = "test_connection"
        console.print(f"测试创建集合: {test_collection_name}")
        
        try:
            # 先尝试删除如果存在
            try:
                client.delete_collection(test_collection_name)
                console.print("删除了已存在的测试集合")
            except:
                pass
                
            # 创建新集合
            collection = client.create_collection(test_collection_name)
            console.print(f"[green]✅ 集合创建成功: {collection.name}[/green]")
            
            # 清理测试集合
            client.delete_collection(test_collection_name)
            console.print("清理测试集合")
            
        except Exception as e:
            console.print(f"[yellow]⚠️  集合操作警告: {str(e)}[/yellow]")
            
        console.print("[bold green]🎉 ChromaDB 连接测试成功！[/bold green]")
        return True
        
    except Exception as e:
        console.print(f"[red]❌ 连接失败: {str(e)}[/red]")
        
        # 提供诊断信息
        console.print("\n[bold yellow]诊断信息:[/bold yellow]")
        console.print("1. 请确保 ChromaDB 服务器正在运行:")
        console.print("   docker run -p 8002:8000 chromadb/chroma:latest")
        console.print("2. 检查端口是否被占用:")
        console.print("   lsof -i :8002")
        console.print("3. 尝试不同的端口或主机地址")
        
        return False

def test_langchain_chroma():
    """测试 LangChain Chroma 集成"""
    console.print("\n[bold blue]🔍 测试 LangChain Chroma 集成...[/bold blue]")
    
    try:
        from langchain_chroma import Chroma
        from embeddings.siliconflow import SiliconFlowEmbeddings
        
        # 检查 API Key
        api_key = os.getenv("SILICONFLOW_API_KEY")
        if not api_key:
            console.print("[yellow]⚠️  未设置 SILICONFLOW_API_KEY 环境变量[/yellow]")
            api_key = "test_key"  # 用于测试连接，不实际调用 API
            
        # 创建嵌入实例
        console.print("创建嵌入模型实例...")
        emb = SiliconFlowEmbeddings(
            api_key=api_key,
            model="Qwen/Qwen3-Embedding-8B",
            dimensions=1024,
            batch_size=32,
        )
        console.print("[green]✅ 嵌入模型创建成功[/green]")
        
        # 测试 Chroma 向量存储创建
        console.print("测试 Chroma 向量存储创建...")
        
        settings = Settings(
            anonymized_telemetry=False,
            allow_reset=True,
            is_persistent=False
        )
        
        client = chromadb.HttpClient(
            host="localhost",
            port=8002,
            settings=settings,
        )
        
        vs = Chroma(
            client=client,
            collection_name="test_langchain",
            embedding_function=emb,
        )
        
        console.print("[green]✅ LangChain Chroma 集成测试成功！[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]❌ LangChain 集成测试失败: {str(e)}[/red]")
        
        if "KeyError: '_type'" in str(e):
            console.print("\n[bold yellow]特定错误诊断:[/bold yellow]")
            console.print("这是一个已知的配置格式问题，可能的解决方案:")
            console.print("1. 重启 ChromaDB 服务器")
            console.print("2. 使用不同的集合名称")
            console.print("3. 清除 ChromaDB 数据目录")
            
        return False

def main():
    """主函数"""
    console.print(Panel("ChromaDB 连接诊断工具", style="bold blue"))
    
    # 显示版本信息
    try:
        import chromadb
        import langchain_chroma
        console.print(f"ChromaDB 版本: {chromadb.__version__}")
        console.print(f"LangChain-Chroma 版本: {langchain_chroma.__version__}")
    except:
        pass
        
    console.print()
    
    # 测试基本连接
    basic_ok = test_chromadb_connection()
    
    # 测试 LangChain 集成
    if basic_ok:
        langchain_ok = test_langchain_chroma()
        
        if langchain_ok:
            console.print("\n[bold green]🎉 所有测试通过！可以正常使用交互式工具。[/bold green]")
        else:
            console.print("\n[bold yellow]⚠️  基本连接正常，但 LangChain 集成有问题。[/bold yellow]")
    else:
        console.print("\n[bold red]❌ 基本连接失败，请先解决连接问题。[/bold red]")

if __name__ == "__main__":
    main()

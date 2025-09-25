#!/usr/bin/env python3
"""
重排序功能演示脚本
展示嵌入模型 vs 重排序模型的效果对比
"""

import os
import sys
from pathlib import Path

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns

console = Console()

def demo_reranking_concept():
    """演示重排序概念"""
    console.print(Panel("🎯 重排序模型 vs 嵌入模型对比演示", style="bold blue"))
    
    # 模拟查询和文档
    query = "苹果的营养价值"
    
    documents = [
        "苹果是一种富含维生素C和纤维的水果，对健康非常有益。",
        "苹果公司是全球知名的科技公司，生产iPhone等产品。",
        "苹果树是蔷薇科植物，春天开花，秋天结果。",
        "吃苹果可以帮助消化，降低胆固醇，预防心脏病。",
        "苹果手机的最新型号配备了先进的摄像头系统。"
    ]
    
    console.print(f"[bold cyan]查询:[/bold cyan] {query}")
    console.print()
    
    # 显示原始文档
    console.print("[bold yellow]候选文档:[/bold yellow]")
    for i, doc in enumerate(documents, 1):
        console.print(f"{i}. {doc}")
    console.print()
    
    # 模拟向量搜索结果 (基于词汇重叠)
    vector_results = [
        (documents[0], 0.75),  # 苹果营养
        (documents[1], 0.65),  # 苹果公司 (词汇匹配但语义不符)
        (documents[4], 0.60),  # 苹果手机 (词汇匹配但语义不符)
        (documents[3], 0.55),  # 健康相关
        (documents[2], 0.50),  # 苹果树
    ]
    
    # 模拟重排序结果 (基于语义理解)
    rerank_results = [
        (documents[0], 0.92),  # 苹果营养 - 最相关
        (documents[3], 0.88),  # 健康相关 - 高度相关
        (documents[2], 0.35),  # 苹果树 - 中等相关
        (documents[1], 0.15),  # 苹果公司 - 低相关
        (documents[4], 0.12),  # 苹果手机 - 低相关
    ]
    
    # 创建对比表格
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("排名", justify="center", style="cyan")
    table.add_column("向量搜索结果", style="white", width=40)
    table.add_column("分数", justify="center", style="green")
    table.add_column("重排序结果", style="white", width=40)
    table.add_column("分数", justify="center", style="green")
    
    for i in range(len(documents)):
        vector_doc, vector_score = vector_results[i]
        rerank_doc, rerank_score = rerank_results[i]
        
        # 截断文档显示
        vector_short = vector_doc[:35] + "..." if len(vector_doc) > 35 else vector_doc
        rerank_short = rerank_doc[:35] + "..." if len(rerank_doc) > 35 else rerank_doc
        
        table.add_row(
            str(i + 1),
            vector_short,
            f"{vector_score:.2f}",
            rerank_short,
            f"{rerank_score:.2f}"
        )
    
    console.print(table)
    console.print()
    
    # 分析结果
    analysis = """
[bold green]✅ 重排序模型的优势:[/bold green]
• 更好的语义理解：正确识别"营养价值"相关内容
• 降低误匹配：苹果公司/手机排名下降
• 提高精确度：真正相关的文档排名靠前

[bold yellow]⚠️ 向量搜索的局限:[/bold yellow]  
• 主要基于词汇匹配：包含"苹果"就认为相关
• 缺乏语义理解：无法区分不同含义的"苹果"
• 容易被干扰：不相关但包含关键词的文档排名较高
    """
    
    console.print(Panel(analysis, title="效果分析"))

def show_reranking_workflow():
    """展示重排序工作流程"""
    console.print(Panel("🔄 两阶段检索工作流程", style="bold blue"))
    
    workflow_steps = [
        "[bold cyan]第一阶段 - 粗排 (向量检索)[/bold cyan]",
        "• 用户查询 → 嵌入模型 → 查询向量",
        "• 在向量数据库中快速搜索",
        "• 返回 Top-50 候选文档",
        "• 优点：速度快，召回率高",
        "",
        "[bold green]第二阶段 - 精排 (重排序)[/bold green]",
        "• 查询 + 候选文档 → 重排序模型",
        "• 深度语义理解和匹配",
        "• 重新排序并返回 Top-5 结果",
        "• 优点：准确度高，精确度高"
    ]
    
    for step in workflow_steps:
        if step:
            console.print(step)
        else:
            console.print()

def show_model_comparison():
    """展示不同重排序模型的特点"""
    console.print(Panel("🤖 重排序模型对比", style="bold blue"))
    
    models_table = Table(show_header=True, header_style="bold magenta")
    models_table.add_column("模型", style="cyan", width=25)
    models_table.add_column("特点", style="white", width=30)
    models_table.add_column("适用场景", style="green", width=25)
    models_table.add_column("推荐指数", justify="center", style="yellow")
    
    models_data = [
        ("BAAI/bge-reranker-v2-m3", "平衡性能和速度", "通用场景", "⭐⭐⭐⭐⭐"),
        ("Pro/BAAI/bge-reranker-v2-m3", "更高精度", "高质量要求", "⭐⭐⭐⭐"),
        ("Qwen/Qwen3-Reranker-8B", "最高精度", "学术研究", "⭐⭐⭐⭐⭐"),
        ("Qwen/Qwen3-Reranker-4B", "中等精度", "平衡场景", "⭐⭐⭐⭐"),
        ("Qwen/Qwen3-Reranker-0.6B", "快速推理", "实时应用", "⭐⭐⭐"),
    ]
    
    for model, feature, scenario, rating in models_data:
        models_table.add_row(model, feature, scenario, rating)
    
    console.print(models_table)

def main():
    """主函数"""
    console.print("[bold blue]🚀 RAG 重排序功能演示[/bold blue]")
    console.print()
    
    # 演示重排序概念
    demo_reranking_concept()
    console.print()
    
    # 展示工作流程
    show_reranking_workflow()
    console.print()
    
    # 展示模型对比
    show_model_comparison()
    console.print()
    
    # 使用建议
    suggestions = """
[bold cyan]💡 使用建议:[/bold cyan]

1. [bold green]何时使用重排序:[/bold green]
   • 对检索准确性要求较高
   • 查询较为复杂或模糊
   • 文档集合较大且多样化

2. [bold yellow]性能考虑:[/bold yellow]
   • 重排序会增加延迟 (通常 100-500ms)
   • 建议初始检索 20-50 个候选文档
   • 最终返回 5-10 个精确结果

3. [bold blue]最佳实践:[/bold blue]
   • 先用向量搜索快速筛选
   • 再用重排序模型精确排序
   • 根据应用场景选择合适的模型
    """
    
    console.print(Panel(suggestions, title="使用指南"))
    
    console.print("\n[bold green]🎉 现在你可以在交互式工具中体验重排序功能了！[/bold green]")
    console.print("[dim]运行: python run.py，然后选择功能4进行智能检索[/dim]")

if __name__ == "__main__":
    main()

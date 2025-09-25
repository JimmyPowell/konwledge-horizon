#!/usr/bin/env python3
"""
Interactive CLI for RAG with ChromaDB
支持数字选择的交互式命令行界面
"""

from __future__ import annotations

import os
import sys
from typing import Optional, List
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text

from embeddings.siliconflow import SiliconFlowEmbeddings
from utils.loader import load_file
from utils.chunk import split_text, build_ids, compute_checksum
from kb.chroma_remote import get_vectorstore, add_chunks, recall as kb_recall, delete_by_source


class InteractiveRAG:
    def __init__(self):
        self.console = Console()
        self.kb_name: Optional[str] = None
        self.host: str = "localhost"
        self.port: int = 8002
        self.api_key: Optional[str] = None
        self.model: str = "Qwen/Qwen3-Embedding-8B"
        self.dimensions: int = 1024
        self.batch_size: int = 32
        self.vectorstore = None
        self.auto_connected = False

        # 从环境变量获取 API key
        self.api_key = os.getenv("SILICONFLOW_API_KEY")
        
    def show_banner(self):
        """显示欢迎横幅"""
        banner = Text("🚀 RAG ChromaDB 交互式命令行工具", style="bold blue")
        self.console.print(Panel(banner, expand=False))
        self.console.print()

    def auto_connect_to_kb(self):
        """自动连接到知识库"""
        self.console.print("[cyan]🔍 正在检测可用的知识库...[/cyan]")

        try:
            # 尝试连接到 ChromaDB 服务器
            import chromadb
            from chromadb.config import Settings

            settings = Settings(
                anonymized_telemetry=False,
                allow_reset=True,
                is_persistent=False
            )

            client = chromadb.HttpClient(
                host=self.host,
                port=self.port,
                settings=settings,
            )

            # 测试连接
            client.heartbeat()

            # 获取所有集合
            collections = client.list_collections()

            if not collections:
                self.console.print("[yellow]📝 未发现现有知识库，将引导您创建新的知识库[/yellow]")
                return False

            # 显示可用的知识库
            self.console.print(f"[green]✅ 发现 {len(collections)} 个知识库:[/green]")

            kb_table = Table(show_header=True, header_style="bold magenta")
            kb_table.add_column("序号", justify="center", style="cyan")
            kb_table.add_column("知识库名称", style="white")
            kb_table.add_column("文档数量", justify="center", style="green")

            for i, collection in enumerate(collections, 1):
                try:
                    count = collection.count()
                    kb_table.add_row(str(i), collection.name, str(count))
                except:
                    kb_table.add_row(str(i), collection.name, "未知")

            self.console.print(kb_table)

            # 自动选择策略
            if len(collections) == 1:
                # 只有一个知识库，自动连接
                selected_kb = collections[0].name
                self.console.print(f"[green]🎯 自动连接到知识库: {selected_kb}[/green]")
            else:
                # 多个知识库，让用户选择
                self.console.print("\n[bold cyan]请选择要连接的知识库:[/bold cyan]")
                choices = [str(i) for i in range(1, len(collections) + 1)]
                choices.append("0")  # 创建新知识库的选项

                self.console.print("0. 创建新的知识库")

                choice = Prompt.ask(
                    "请输入序号",
                    choices=choices,
                    default="1"
                )

                if choice == "0":
                    return False  # 创建新知识库
                else:
                    selected_kb = collections[int(choice) - 1].name

            # 连接到选定的知识库
            self.kb_name = selected_kb
            emb = self.get_embeddings()
            self.vectorstore = get_vectorstore(
                collection=self.kb_name,
                embedding=emb,
                host=self.host,
                port=self.port,
            )

            self.auto_connected = True
            self.console.print(f"[bold green]🎉 成功连接到知识库: {self.kb_name}[/bold green]")

            # 显示知识库基本信息
            try:
                count = self.vectorstore._collection.count()
                self.console.print(f"[dim]📊 当前知识库包含 {count} 个文档块[/dim]")
            except:
                pass

            return True

        except Exception as e:
            self.console.print(f"[red]❌ 自动连接失败: {str(e)}[/red]")
            self.console.print("[yellow]💡 将进入手动连接模式[/yellow]")
            return False
        
    def show_menu(self):
        """显示主菜单"""
        if not self.auto_connected:
            menu_text = """
[bold cyan]请选择操作：[/bold cyan]

[bold green]1.[/bold green] 连接/创建知识库 (Connect to Knowledge Base)
[bold green]2.[/bold green] 添加文档 - 文件路径 (Add Document from File)
[bold green]3.[/bold green] 添加文档 - 直接输入文本 (Add Document from Text Input)
[bold green]4.[/bold green] 智能检索/召回 (Smart Search with Reranking) [bold yellow]⭐ 新功能[/bold yellow]
[bold green]5.[/bold green] 查看知识库状态 (View KB Status)
[bold green]6.[/bold green] 删除文档 (Delete Document)
[bold green]7.[/bold green] 配置设置 (Configuration Settings)
[bold green]8.[/bold green] 退出 (Exit)

[dim]💡 请先连接到知识库 (选择1)，然后使用其他功能[/dim]
            """
        else:
            menu_text = f"""
[bold cyan]当前知识库: [bold white]{self.kb_name}[/bold white] | 请选择操作：[/bold cyan]

[bold green]1.[/bold green] 切换知识库 (Switch Knowledge Base)
[bold green]2.[/bold green] 添加文档 - 文件路径 (Add Document from File)
[bold green]3.[/bold green] 添加文档 - 直接输入文本 (Add Document from Text Input)
[bold green]4.[/bold green] 智能检索/召回 (Smart Search with Reranking) [bold yellow]⭐ 新功能[/bold yellow]
[bold green]5.[/bold green] 查看知识库状态 (View KB Status)
[bold green]6.[/bold green] 删除文档 (Delete Document)
[bold green]7.[/bold green] 配置设置 (Configuration Settings)
[bold green]8.[/bold green] 退出 (Exit)

[dim]💡 功能4支持两阶段检索：向量搜索 + 重排序模型，显著提高检索准确性[/dim]
            """
        self.console.print(Panel(menu_text, title="主菜单", expand=False))
        
    def get_embeddings(self) -> SiliconFlowEmbeddings:
        """获取嵌入模型实例"""
        if not self.api_key:
            self.console.print("[red]错误: 未设置 SILICONFLOW_API_KEY 环境变量[/red]")
            self.api_key = Prompt.ask("请输入 SiliconFlow API Key")
            
        return SiliconFlowEmbeddings(
            api_key=self.api_key,
            model=self.model,
            dimensions=self.dimensions,
            batch_size=self.batch_size,
        )
        
    def connect_or_create_kb(self):
        """连接到现有知识库或创建新知识库"""
        if self.auto_connected:
            self.console.print("[bold blue]🔄 切换知识库[/bold blue]")
        else:
            self.console.print("[bold blue]🔗 连接到知识库[/bold blue]")

        # 重置连接状态
        self.auto_connected = False
        self.vectorstore = None

        # 尝试自动连接
        if self.auto_connect_to_kb():
            return

        # 手动连接/创建
        self.console.print("\n[bold cyan]手动连接模式:[/bold cyan]")
        kb_name = Prompt.ask("请输入知识库名称", default=self.kb_name or "my_kb")

        try:
            emb = self.get_embeddings()
            self.vectorstore = get_vectorstore(
                collection=kb_name,
                embedding=emb,
                host=self.host,
                port=self.port,
            )

            self.kb_name = kb_name
            self.auto_connected = True

            # 检查是否是新创建的知识库
            try:
                count = self.vectorstore._collection.count()
                if count == 0:
                    self.console.print(f"[green]✅ 新知识库创建成功:[/green] {self.kb_name}")
                    self.console.print("[dim]💡 知识库为空，请添加文档后开始使用[/dim]")
                else:
                    self.console.print(f"[green]✅ 连接到现有知识库:[/green] {self.kb_name}")
                    self.console.print(f"[dim]📊 包含 {count} 个文档块[/dim]")
            except:
                self.console.print(f"[green]✅ 知识库连接成功:[/green] {self.kb_name}")

        except Exception as e:
            self.console.print(f"[red]❌ 连接失败: {str(e)}[/red]")
            
    def add_document_from_file(self):
        """从文件添加文档"""
        self.console.print("[bold blue]📄 添加文档 - 从文件[/bold blue]")
        
        if not self.vectorstore:
            self.console.print("[yellow]⚠️  请先连接到知识库 (选择菜单选项1)[/yellow]")
            return
            
        file_path = Prompt.ask("请输入文件路径")
        
        if not Path(file_path).exists():
            self.console.print(f"[red]❌ 文件不存在: {file_path}[/red]")
            return
            
        try:
            # 询问是否替换已存在的文档
            replace = Confirm.ask("是否替换已存在的同名文档?", default=False)
            
            # 加载文件
            text, meta = load_file(file_path)
            
            if replace:
                delete_by_source(self.vectorstore, meta["source"])
                
            # 分块
            chunk_size = int(Prompt.ask("分块大小", default="1000"))
            chunk_overlap = int(Prompt.ask("分块重叠", default="100"))
            
            chunks = split_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            ids = build_ids(meta["source"], chunks)
            
            # 构建元数据
            metadatas = []
            base_checksum = compute_checksum(text)
            for i, c in enumerate(chunks):
                m = dict(meta)
                m.update({
                    "chunk_id": i,
                    "checksum": base_checksum,
                })
                metadatas.append(m)
                
            self.console.print(f"正在嵌入并添加 {len(chunks)} 个文本块...")
            add_chunks(self.vectorstore, texts=chunks, metadatas=metadatas, ids=ids)
            self.console.print(f"[green]✅ 文档添加成功:[/green] {meta['source']}")
            
        except Exception as e:
            self.console.print(f"[red]❌ 添加文档失败: {str(e)}[/red]")
            
    def add_document_from_text(self):
        """从直接输入的文本添加文档"""
        self.console.print("[bold blue]✏️  添加文档 - 直接输入文本[/bold blue]")
        
        if not self.vectorstore:
            self.console.print("[yellow]⚠️  请先连接到知识库 (选择菜单选项1)[/yellow]")
            return
            
        self.console.print("请输入文本内容 (输入 'END' 结束输入):")
        
        lines = []
        while True:
            line = input()
            if line.strip() == 'END':
                break
            lines.append(line)
            
        text = '\n'.join(lines)
        
        if not text.strip():
            self.console.print("[yellow]⚠️  文本内容为空[/yellow]")
            return
            
        try:
            # 创建元数据
            source_name = Prompt.ask("请输入文档名称", default="text_input")
            meta = {"source": source_name, "type": "text"}
            
            # 分块
            chunk_size = int(Prompt.ask("分块大小", default="1000"))
            chunk_overlap = int(Prompt.ask("分块重叠", default="100"))
            
            chunks = split_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            ids = build_ids(meta["source"], chunks)
            
            # 构建元数据
            metadatas = []
            base_checksum = compute_checksum(text)
            for i, c in enumerate(chunks):
                m = dict(meta)
                m.update({
                    "chunk_id": i,
                    "checksum": base_checksum,
                })
                metadatas.append(m)
                
            self.console.print(f"正在嵌入并添加 {len(chunks)} 个文本块...")
            add_chunks(self.vectorstore, texts=chunks, metadatas=metadatas, ids=ids)
            self.console.print(f"[green]✅ 文本添加成功:[/green] {meta['source']}")
            
        except Exception as e:
            self.console.print(f"[red]❌ 添加文本失败: {str(e)}[/red]")
            
    def search_documents(self):
        """向量检索/召回"""
        self.console.print("[bold blue]🔍 向量检索/召回[/bold blue]")

        if not self.vectorstore:
            self.console.print("[yellow]⚠️  请先连接到知识库 (选择菜单选项1)[/yellow]")
            return

        query = Prompt.ask("请输入查询文本")
        top_k = int(Prompt.ask("返回结果数量", default="5"))
        score_threshold = Prompt.ask("相似度阈值 (可选，直接回车跳过)", default="")

        # 询问是否使用重排序
        use_reranker = Confirm.ask("是否使用重排序模型提高准确性？", default=False)

        reranker_model = "BAAI/bge-reranker-v2-m3"
        retrieval_k = None

        if use_reranker:
            self.console.print("\n[bold cyan]重排序模型选项:[/bold cyan]")
            self.console.print("1. BAAI/bge-reranker-v2-m3 (推荐，平衡性能)")
            self.console.print("2. Pro/BAAI/bge-reranker-v2-m3 (高精度)")
            self.console.print("3. Qwen/Qwen3-Reranker-8B (最高精度)")
            self.console.print("4. Qwen/Qwen3-Reranker-4B (中等精度)")
            self.console.print("5. Qwen/Qwen3-Reranker-0.6B (快速推理)")

            model_choice = Prompt.ask("选择重排序模型", choices=["1", "2", "3", "4", "5"], default="1")

            model_map = {
                "1": "BAAI/bge-reranker-v2-m3",
                "2": "Pro/BAAI/bge-reranker-v2-m3",
                "3": "Qwen/Qwen3-Reranker-8B",
                "4": "Qwen/Qwen3-Reranker-4B",
                "5": "Qwen/Qwen3-Reranker-0.6B"
            }
            reranker_model = model_map[model_choice]

            # 设置候选文档数量
            retrieval_k = int(Prompt.ask("初始检索文档数量 (用于重排序)", default=str(top_k * 3)))

        try:
            self.console.print(f"[cyan]正在{'使用重排序模型' if use_reranker else '进行向量'}检索...[/cyan]")

            results = kb_recall(
                self.vectorstore,
                query=query,
                top_k=top_k,
                use_reranker=use_reranker,
                reranker_model=reranker_model,
                retrieval_k=retrieval_k
            )

            if not results:
                self.console.print("[yellow]⚠️  未找到相关文档[/yellow]")
                return

            table = Table(show_lines=True)
            table.add_column("排名", justify="right", style="cyan")
            table.add_column("分数", style="green")
            table.add_column("来源", style="blue")
            table.add_column("块ID", justify="right")
            table.add_column("文本内容", style="white")

            for i, (doc, score) in enumerate(results, start=1):
                source = doc.metadata.get("source", "")
                chunk_id = str(doc.metadata.get("chunk_id", ""))

                # 处理分数显示
                if use_reranker:
                    # 重排序分数通常是相关性分数 (0-1)
                    display_score = float(score)
                    score_label = f"{display_score:.4f}"
                else:
                    # 向量相似度分数 (距离转换为相似度)
                    try:
                        sim = 1.0 - float(score)
                        display_score = sim
                        score_label = f"{sim:.4f}"
                    except Exception:
                        display_score = float(score)
                        score_label = f"{display_score:.4f}"

                # 应用阈值过滤
                if score_threshold and display_score < float(score_threshold):
                    continue

                # 截断文本显示
                snippet = (doc.page_content[:200] + "...") if len(doc.page_content) > 200 else doc.page_content

                table.add_row(
                    str(i),
                    score_label,
                    source,
                    chunk_id,
                    snippet
                )

            # 显示检索方法信息
            method_info = f"[dim]检索方法: {'重排序 (' + reranker_model + ')' if use_reranker else '向量相似度'}[/dim]"
            self.console.print(method_info)
            self.console.print(table)

        except Exception as e:
            self.console.print(f"[red]❌ 检索失败: {str(e)}[/red]")
            if use_reranker and "API" in str(e):
                self.console.print("[yellow]💡 提示: 重排序失败可能是API问题，已自动回退到向量搜索[/yellow]")

    def view_kb_status(self):
        """查看知识库状态"""
        self.console.print("[bold blue]📊 知识库状态[/bold blue]")

        if not self.vectorstore:
            self.console.print("[yellow]⚠️  请先连接到知识库 (选择菜单选项1)[/yellow]")
            return

        try:
            # 显示基本信息
            info_table = Table(show_header=False)
            info_table.add_column("属性", style="cyan")
            info_table.add_column("值", style="white")

            info_table.add_row("知识库名称", self.kb_name or "未设置")
            info_table.add_row("服务器地址", f"{self.host}:{self.port}")
            info_table.add_row("嵌入模型", self.model)
            info_table.add_row("向量维度", str(self.dimensions))

            self.console.print(Panel(info_table, title="知识库配置信息"))

            # 尝试获取集合统计信息
            try:
                collection = self.vectorstore._collection
                count = collection.count()
                self.console.print(f"[green]📈 文档块数量: {count}[/green]")
            except Exception as e:
                self.console.print(f"[yellow]⚠️  无法获取统计信息: {str(e)}[/yellow]")

        except Exception as e:
            self.console.print(f"[red]❌ 获取状态失败: {str(e)}[/red]")

    def delete_document(self):
        """删除文档"""
        self.console.print("[bold blue]🗑️  删除文档[/bold blue]")

        if not self.vectorstore:
            self.console.print("[yellow]⚠️  请先连接到知识库 (选择菜单选项1)[/yellow]")
            return

        source = Prompt.ask("请输入要删除的文档来源名称")

        if not source:
            self.console.print("[yellow]⚠️  文档来源不能为空[/yellow]")
            return

        try:
            if Confirm.ask(f"确定要删除文档 '{source}' 吗？此操作不可撤销"):
                delete_by_source(self.vectorstore, source)
                self.console.print(f"[green]✅ 文档删除成功:[/green] {source}")
            else:
                self.console.print("[yellow]操作已取消[/yellow]")

        except Exception as e:
            self.console.print(f"[red]❌ 删除失败: {str(e)}[/red]")

    def configure_settings(self):
        """配置设置"""
        self.console.print("[bold blue]⚙️  配置设置[/bold blue]")

        settings_table = Table(show_header=False)
        settings_table.add_column("设置项", style="cyan")
        settings_table.add_column("当前值", style="white")

        settings_table.add_row("1. 知识库名称", self.kb_name or "未设置")
        settings_table.add_row("2. 服务器地址", self.host)
        settings_table.add_row("3. 服务器端口", str(self.port))
        settings_table.add_row("4. 嵌入模型", self.model)
        settings_table.add_row("5. 向量维度", str(self.dimensions))
        settings_table.add_row("6. 批处理大小", str(self.batch_size))
        settings_table.add_row("7. API Key", "已设置" if self.api_key else "未设置")

        self.console.print(Panel(settings_table, title="当前配置"))

        choice = Prompt.ask("请选择要修改的设置 (1-7，直接回车跳过)", default="")

        if choice == "1":
            self.kb_name = Prompt.ask("知识库名称", default=self.kb_name or "my_kb")
        elif choice == "2":
            self.host = Prompt.ask("服务器地址", default=self.host)
        elif choice == "3":
            self.port = int(Prompt.ask("服务器端口", default=str(self.port)))
        elif choice == "4":
            self.model = Prompt.ask("嵌入模型", default=self.model)
        elif choice == "5":
            self.dimensions = int(Prompt.ask("向量维度", default=str(self.dimensions)))
        elif choice == "6":
            self.batch_size = int(Prompt.ask("批处理大小", default=str(self.batch_size)))
        elif choice == "7":
            self.api_key = Prompt.ask("API Key", password=True)

        if choice:
            self.console.print("[green]✅ 设置已更新[/green]")
            # 如果修改了关键配置，需要重新初始化
            if choice in ["1", "2", "3", "4", "5", "7"]:
                self.vectorstore = None
                self.console.print("[yellow]⚠️  配置已更改，请重新初始化知识库[/yellow]")

    def run(self):
        """运行交互式界面"""
        self.show_banner()

        # 尝试自动连接到知识库
        self.auto_connect_to_kb()

        while True:
            try:
                self.show_menu()
                choice = Prompt.ask("请选择操作", choices=["1", "2", "3", "4", "5", "6", "7", "8"])

                self.console.print()  # 空行分隔

                if choice == "1":
                    self.connect_or_create_kb()
                elif choice == "2":
                    self.add_document_from_file()
                elif choice == "3":
                    self.add_document_from_text()
                elif choice == "4":
                    self.search_documents()
                elif choice == "5":
                    self.view_kb_status()
                elif choice == "6":
                    self.delete_document()
                elif choice == "7":
                    self.configure_settings()
                elif choice == "8":
                    self.console.print("[bold blue]👋 再见！[/bold blue]")
                    break

                self.console.print()  # 空行分隔
                input("按回车键继续...")
                self.console.clear()

            except KeyboardInterrupt:
                self.console.print("\n[yellow]操作已取消[/yellow]")
                if Confirm.ask("确定要退出吗？"):
                    break
            except Exception as e:
                self.console.print(f"[red]❌ 发生错误: {str(e)}[/red]")
                input("按回车键继续...")


def main():
    """主函数"""
    app = InteractiveRAG()
    app.run()


if __name__ == "__main__":
    main()

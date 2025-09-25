from __future__ import annotations

from typing import Iterable, List, Optional, Tuple

import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document


def connect_chroma(
    host: str = "localhost",
    port: int = 8002,
):
    # 禁用遥测以避免遥测错误
    settings = Settings(
        anonymized_telemetry=False,
        allow_reset=True,
        is_persistent=False
    )

    return chromadb.HttpClient(
        host=host,
        port=port,
        settings=settings,
    )


def get_vectorstore(
    collection: str,
    embedding: Embeddings,
    host: str = "localhost",
    port: int = 8002,
) -> Chroma:
    try:
        client = connect_chroma(host=host, port=port)

        # 测试连接
        try:
            client.heartbeat()
        except Exception as e:
            raise ConnectionError(f"无法连接到 ChromaDB 服务器 {host}:{port}. 请确保服务器正在运行。错误: {str(e)}")

        # 尝试创建向量存储，使用重试机制处理 _type 错误
        max_retries = 3
        for attempt in range(max_retries):
            try:
                vs = Chroma(
                    client=client,
                    collection_name=collection,
                    embedding_function=embedding,
                )

                # 测试向量存储是否正常工作
                try:
                    # 尝试获取集合信息
                    vs._collection.count()
                except Exception as e:
                    if attempt < max_retries - 1:
                        # 如果不是最后一次尝试，等待后重试
                        import time
                        time.sleep(1)
                        continue
                    raise

                return vs

            except Exception as e:
                if "_type" in str(e) and attempt < max_retries - 1:
                    # 尝试删除可能损坏的集合
                    try:
                        client.delete_collection(collection)
                    except:
                        pass
                    import time
                    time.sleep(1)
                    continue
                elif attempt == max_retries - 1:
                    # 最后一次尝试失败
                    if "_type" in str(e):
                        raise ValueError(
                            f"ChromaDB 集合 '{collection}' 配置格式错误。\n"
                            "这通常是由于客户端和服务器版本不匹配造成的。\n"
                            "建议解决方案:\n"
                            "1. 重启 ChromaDB 服务器: docker restart <container_id>\n"
                            "2. 使用不同的集合名称\n"
                            "3. 清除 ChromaDB 数据并重新启动服务器"
                        )
                    raise

        return vs

    except Exception as e:
        raise


def add_chunks(
    vs: Chroma,
    texts: List[str],
    metadatas: Optional[List[dict]] = None,
    ids: Optional[List[str]] = None,
):
    vs.add_texts(texts=texts, metadatas=metadatas, ids=ids)


def delete_by_source(vs: Chroma, source: str) -> None:
    vs.delete(where={"source": source})


def recall(
    vs: Chroma,
    query: str,
    top_k: int = 5,
    use_reranker: bool = False,
    reranker_model: str = "BAAI/bge-reranker-v2-m3",
    retrieval_k: Optional[int] = None,
) -> List[Tuple[Document, float]]:
    """
    文档召回函数，支持重排序

    Args:
        vs: Chroma 向量存储
        query: 查询文本
        top_k: 最终返回的文档数量
        use_reranker: 是否使用重排序模型
        reranker_model: 重排序模型名称
        retrieval_k: 初始检索的文档数量 (用于重排序)

    Returns:
        List of (Document, score) tuples
    """
    if not use_reranker:
        # 传统的向量相似度搜索
        results = vs.similarity_search_with_score(query=query, k=top_k)
        return results

    # 使用重排序的两阶段检索
    try:
        from reranker import create_reranker

        # 第一阶段: 向量检索获取候选文档
        # 检索更多候选文档用于重排序
        retrieval_k = retrieval_k or max(top_k * 3, 20)  # 默认检索3倍数量的候选文档

        initial_results = vs.similarity_search_with_score(query=query, k=retrieval_k)

        if not initial_results:
            return []

        # 提取文档文本和元数据
        documents = []
        doc_objects = []

        for doc, score in initial_results:
            documents.append(doc.page_content)
            doc_objects.append((doc, score))

        # 第二阶段: 重排序
        reranker = create_reranker(model=reranker_model)
        reranked_results = reranker.rerank_documents_with_scores(
            query=query,
            documents=documents,
            top_n=top_k
        )

        # 构建最终结果
        final_results = []
        for reranked_doc, rerank_score, original_index in reranked_results:
            if original_index < len(doc_objects):
                original_doc, _ = doc_objects[original_index]
                # 使用重排序分数 (注意: 重排序分数通常是相关性分数，不是距离)
                final_results.append((original_doc, rerank_score))

        return final_results

    except ImportError:
        # 如果重排序模块不可用，回退到传统搜索
        print("Warning: Reranker module not available, falling back to vector search")
        results = vs.similarity_search_with_score(query=query, k=top_k)
        return results
    except Exception as e:
        # 如果重排序失败，回退到传统搜索
        print(f"Warning: Reranking failed ({str(e)}), falling back to vector search")
        results = vs.similarity_search_with_score(query=query, k=top_k)
        return results

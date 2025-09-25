from __future__ import annotations

import os
import time
from typing import List, Dict, Any, Optional, Tuple

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class SiliconFlowReranker:
    """
    SiliconFlow 重排序模型客户端
    
    支持的模型:
    - BAAI/bge-reranker-v2-m3 (推荐)
    - Pro/BAAI/bge-reranker-v2-m3 (高级版)
    - Qwen/Qwen3-Reranker-8B
    - Qwen/Qwen3-Reranker-4B
    - Qwen/Qwen3-Reranker-0.6B
    - netease-youdao/bce-reranker-base_v1
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "BAAI/bge-reranker-v2-m3",
        base_url: str = "https://api.siliconflow.cn/v1/rerank",
        timeout: int = 60,
    ) -> None:
        self.api_key = api_key or os.getenv("SILICONFLOW_API_KEY")
        if not self.api_key:
            raise ValueError("SILICONFLOW_API_KEY not provided. Set env var or pass api_key.")
        
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((requests.RequestException, ValueError)),
    )
    def rerank(
        self,
        query: str,
        documents: List[str],
        top_n: Optional[int] = None,
        return_documents: bool = True,
        instruction: Optional[str] = None,
        max_chunks_per_doc: Optional[int] = None,
        overlap_tokens: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        对文档进行重排序
        
        Args:
            query: 查询文本
            documents: 候选文档列表
            top_n: 返回前N个最相关的文档
            return_documents: 是否在结果中包含文档文本
            instruction: 重排序指令 (仅支持 Qwen 系列模型)
            max_chunks_per_doc: 每个文档的最大分块数 (仅支持 BGE 系列模型)
            overlap_tokens: 分块间重叠的token数 (仅支持 BGE 系列模型)
            
        Returns:
            重排序结果列表，每个元素包含:
            - index: 原始文档索引
            - relevance_score: 相关性分数
            - document: 文档内容 (如果 return_documents=True)
        """
        if not documents:
            return []
            
        payload = {
            "model": self.model,
            "query": query,
            "documents": documents,
            "return_documents": return_documents,
        }
        
        # 添加可选参数
        if top_n is not None:
            payload["top_n"] = min(top_n, len(documents))
            
        if instruction and "Qwen" in self.model:
            payload["instruction"] = instruction
            
        if max_chunks_per_doc and "bge-reranker" in self.model:
            payload["max_chunks_per_doc"] = max_chunks_per_doc
            
        if overlap_tokens and "bge-reranker" in self.model:
            payload["overlap_tokens"] = min(overlap_tokens, 80)

        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self._request_headers(),
                timeout=self.timeout,
            )
            
            if response.status_code == 429:
                raise requests.RequestException("429 Too Many Requests from SiliconFlow API")
                
            if not response.ok:
                raise requests.RequestException(
                    f"SiliconFlow Reranker API error: {response.status_code} {response.text[:200]}"
                )
                
            data = response.json()
            
            if "results" not in data:
                raise ValueError("Invalid response: missing 'results'")
                
            return data["results"]
            
        except Exception as e:
            raise ValueError(f"Reranker API call failed: {str(e)}")

    def rerank_documents_with_scores(
        self,
        query: str,
        documents: List[str],
        top_n: Optional[int] = None,
    ) -> List[Tuple[str, float, int]]:
        """
        重排序文档并返回 (文档, 分数, 原始索引) 的元组列表
        
        Returns:
            List of (document_text, relevance_score, original_index)
        """
        results = self.rerank(
            query=query,
            documents=documents,
            top_n=top_n,
            return_documents=True
        )
        
        reranked = []
        for result in results:
            doc_text = result.get("document", {}).get("text", "")
            score = result.get("relevance_score", 0.0)
            index = result.get("index", 0)
            reranked.append((doc_text, score, index))
            
        return reranked

    def get_model_info(self) -> Dict[str, Any]:
        """获取当前模型信息"""
        model_info = {
            "model": self.model,
            "supports_instruction": "Qwen" in self.model,
            "supports_chunking": "bge-reranker" in self.model,
            "recommended_for": "general purpose",
        }
        
        if "Pro/" in self.model:
            model_info["recommended_for"] = "high accuracy tasks"
        elif "0.6B" in self.model:
            model_info["recommended_for"] = "fast inference"
        elif "8B" in self.model:
            model_info["recommended_for"] = "best accuracy"
            
        return model_info


# 便捷函数
def create_reranker(
    model: str = "BAAI/bge-reranker-v2-m3",
    api_key: Optional[str] = None
) -> SiliconFlowReranker:
    """创建重排序器实例"""
    return SiliconFlowReranker(api_key=api_key, model=model)


def quick_rerank(
    query: str,
    documents: List[str],
    top_n: int = 5,
    model: str = "BAAI/bge-reranker-v2-m3",
    api_key: Optional[str] = None
) -> List[Tuple[str, float]]:
    """
    快速重排序函数
    
    Returns:
        List of (document_text, relevance_score)
    """
    reranker = create_reranker(model=model, api_key=api_key)
    results = reranker.rerank_documents_with_scores(query, documents, top_n)
    return [(doc, score) for doc, score, _ in results]

from __future__ import annotations

import os
import time
from typing import Iterable, List, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from langchain_core.embeddings import Embeddings


class SiliconFlowEmbeddings(Embeddings):
    """
    LangChain-compatible Embeddings via SiliconFlow API.

    - API: POST https://api.siliconflow.cn/v1/embeddings
    - Auth: Authorization: Bearer <SILICONFLOW_API_KEY>
    - Default model: Qwen/Qwen3-Embedding-8B
    - dimensions: Optional[int], supported by Qwen3 series
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "Qwen/Qwen3-Embedding-8B",
        base_url: str = "https://api.siliconflow.cn/v1/embeddings",
        dimensions: Optional[int] = 1024,
        timeout: int = 60,
        batch_size: int = 32,
    ) -> None:
        self.api_key = api_key or os.getenv("SILICONFLOW_API_KEY")
        if not self.api_key:
            raise ValueError("SILICONFLOW_API_KEY not provided. Set env var or pass api_key.")
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.dimensions = dimensions
        self.timeout = timeout
        self.batch_size = max(1, batch_size)

    def _request_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    @retry(
        reraise=True,
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((requests.RequestException, ValueError)),
    )
    def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        payload: dict = {
            "model": self.model,
            "input": texts,
            "encoding_format": "float",
        }
        if self.dimensions is not None:
            payload["dimensions"] = self.dimensions

        resp = requests.post(
            self.base_url,
            json=payload,
            headers=self._request_headers(),
            timeout=self.timeout,
        )
        if resp.status_code == 429:
            # surface for retry
            raise requests.RequestException("429 Too Many Requests from SiliconFlow API")
        if not resp.ok:
            raise requests.RequestException(
                f"SiliconFlow API error: {resp.status_code} {resp.text[:200]}"
            )
        data = resp.json()
        if "data" not in data:
            raise ValueError("Invalid response: missing 'data'")
        # Expect list aligned with input order
        embeddings = []
        for item in data["data"]:
            emb = item.get("embedding")
            if not isinstance(emb, list):
                raise ValueError("Invalid embedding format in response")
            embeddings.append(emb)
        if len(embeddings) != len(texts):
            raise ValueError("Mismatched embeddings count vs inputs")
        return embeddings

    def _iter_batches(self, iterable: Iterable[str], batch_size: int) -> Iterable[List[str]]:
        batch: List[str] = []
        for item in iterable:
            batch.append(item)
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # SiliconFlow expects non-empty strings; coerce None -> ""
        clean_texts = [t if isinstance(t, str) else "" for t in texts]
        results: List[List[float]] = []
        for chunk in self._iter_batches(clean_texts, self.batch_size):
            embeddings = self._embed_batch(chunk)
            results.extend(embeddings)
            # small pause to be gentle on rate limits
            time.sleep(0.01)
        return results

    def embed_query(self, text: str) -> List[float]:
        return self._embed_batch([text])[0]


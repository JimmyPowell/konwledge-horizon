from __future__ import annotations

import logging
from typing import List, Tuple

import httpx

from app.config.settings import settings

logger = logging.getLogger(__name__)


def rerank(query: str, documents: List[str], top_n: int | None = None, model: str | None = None) -> List[Tuple[str, float, int]]:
    """Call SiliconFlow rerank API and return list of (document, score, original_index).

    The API expects inputs: { model, query, documents }. Returns list with indexes and scores.
    """
    if not documents:
        return []
    api_key = settings.SILICONFLOW_API_KEY
    if not api_key:
        raise ValueError("SILICONFLOW_API_KEY not configured for rerank")
    url = "https://api.siliconflow.cn/v1/rerank"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model or settings.RERANK_MODEL,
        "query": query,
        "documents": documents,
    }
    if top_n is not None:
        payload["top_n"] = min(top_n, len(documents))

    logger.info("[rerank] request model=%s docs=%s", payload["model"], len(documents))
    with httpx.Client(timeout=120.0) as client:
        resp = client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    results = []
    for item in data.get("results", []):
        idx = int(item.get("index"))
        score = float(item.get("relevance_score", 0.0))
        results.append((documents[idx], score, idx))
    # Desc by score
    results.sort(key=lambda x: x[1], reverse=True)
    if top_n is not None:
        results = results[:top_n]
    return results


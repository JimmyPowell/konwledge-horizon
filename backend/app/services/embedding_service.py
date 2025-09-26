from __future__ import annotations

import logging
from typing import List

import httpx

from app.config.settings import settings

logger = logging.getLogger(__name__)


def embed_texts(texts: List[str], model: str | None = None) -> List[List[float]]:
    """Call SiliconFlow embeddings API to generate vectors for a batch of texts.

    Returns a list of embedding vectors aligned with input order.
    """
    if not texts:
        return []
    api_key = settings.SILICONFLOW_API_KEY
    if not api_key:
        raise ValueError("SILICONFLOW_API_KEY not configured for embeddings")

    model_name = model or settings.EMBEDDING_MODEL_DEFAULT
    url = f"https://api.siliconflow.cn/v1/embeddings"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model_name, "input": texts}

    logger.info("[embedding] request model=%s batch=%s", model_name, len(texts))
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    # SiliconFlow compatibility: { data: [ { embedding: [...] }, ... ] }
    items = data.get("data") or []
    embeddings: List[List[float]] = []
    for it in items:
        vec = it.get("embedding") or []
        embeddings.append(vec)
    if len(embeddings) != len(texts):
        logger.warning("[embedding] size_mismatch in=%s out=%s", len(texts), len(embeddings))
    return embeddings


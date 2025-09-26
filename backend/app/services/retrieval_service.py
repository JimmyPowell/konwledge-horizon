from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.services import chroma_client
from app.services.embedding_service import embed_texts
from app.services.rerank_service import rerank as _rerank

logger = logging.getLogger(__name__)


def retrieve_collections(
    *,
    query_text: str,
    collections: List[Dict[str, Any]],  # [{"kb_id": int, "collection": str}]
    top_k: int,
    per_kb_k: Optional[int] = None,
    use_rerank: bool = False,
    rerank_top_n: Optional[int] = None,
) -> List[Dict[str, Any]]:
    if not query_text or not collections:
        return []
    qvec = embed_texts([query_text])[0]
    candidates: List[Dict[str, Any]] = []

    per_k = per_kb_k or top_k
    for c in collections:
        kb_id = int(c.get("kb_id"))
        name = c.get("collection")
        if not name:
            continue
        try:
            col = chroma_client.get_collection(name)
            resp = col.query(query_embeddings=[qvec], n_results=per_k, include=["documents", "metadatas", "distances"])
            docs_list = (resp.get("documents") or [[]])[0]
            metas_list = (resp.get("metadatas") or [[]])[0]
            dists_list = (resp.get("distances") or [[]])[0]
            for doc_text, meta, dist in zip(docs_list, metas_list, dists_list):
                if not isinstance(meta, dict):
                    meta = {}
                candidates.append({
                    "text": doc_text or "",
                    "kb_id": kb_id,
                    "doc_id": meta.get("doc_id"),
                    "doc_uid": meta.get("doc_uid"),
                    "chunk_index": meta.get("chunk_index"),
                    "filename": meta.get("filename"),
                    "distance": float(dist) if dist is not None else None,
                })
        except Exception:
            logger.exception("[retrieval] query_failed collection=%s", name)
            continue

    if not candidates:
        return []

    # rerank optionally
    if use_rerank:
        texts = [c["text"] for c in candidates]
        reranked = _rerank(query_text, texts, top_n=(rerank_top_n or top_k))
        # map back by original index
        results: List[Dict[str, Any]] = []
        for _text, score, idx in reranked:
            base = candidates[idx]
            enriched = dict(base)
            enriched["score"] = float(score)
            results.append(enriched)
        return results[:top_k]

    # no rerank: sort by distance asc
    candidates.sort(key=lambda x: x.get("distance") or 0.0)
    return candidates[:top_k]

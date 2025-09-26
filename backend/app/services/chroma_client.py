from __future__ import annotations

import logging
from typing import List, Optional, Dict, Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config.settings import settings

logger = logging.getLogger(__name__)

_client: Optional[chromadb.HttpClient] = None


def get_client() -> chromadb.HttpClient:
    global _client
    if _client is None:
        logger.info(
            "[chroma_client] connecting host=%s port=%s",
            settings.CHROMA_HOST,
            settings.CHROMA_PORT,
        )
        cfg = ChromaSettings(
            anonymized_telemetry=False,
            allow_reset=True,
            is_persistent=False,
        )
        _client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT, settings=cfg)
        try:
            _client.heartbeat()
        except Exception:
            logger.warning("[chroma_client] heartbeat failed host=%s port=%s", settings.CHROMA_HOST, settings.CHROMA_PORT)
    return _client


def get_collection(name: str):
    return get_client().get_or_create_collection(name)


def upsert_texts(
    collection_name: str,
    *,
    ids: List[str],
    texts: List[str],
    metadatas: Optional[List[Dict[str, Any]]] = None,
    embeddings: Optional[List[List[float]]] = None,
):
    if not ids:
        return
    col = get_collection(collection_name)
    col.upsert(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)
    logger.info("[chroma_client] upsert collection=%s ids=%s", collection_name, len(ids))


def delete_by_doc_uid(collection_name: str, doc_uid: str) -> int:
    col = get_collection(collection_name)
    # we persist doc_uid in metadatas for each chunk, so we can bulk delete by where filter
    before = col.count()
    col.delete(where={"doc_uid": doc_uid})
    after = col.count()
    deleted = max(0, before - after)
    logger.info("[chroma_client] delete_by_doc_uid collection=%s uid=%s approx_deleted=%s", collection_name, doc_uid, deleted)
    return deleted

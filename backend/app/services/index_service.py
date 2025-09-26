from __future__ import annotations

import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from sqlalchemy.orm import Session

from app.config.mysql_config import SessionLocal
from app.config.settings import settings
from app.crud import crud_kb, crud_kb_document
from app.services import chroma_client
from app.services.doc_parse_service import parse_file
from app.services.text_chunker import chunk_text
from app.services.embedding_service import embed_texts

logger = logging.getLogger(__name__)


def _json_load(s: Optional[str]) -> Dict[str, Any]:
    try:
        return json.loads(s or "{}")
    except Exception:
        return {}


def index_document(
    db: Session,
    kb_id: int,
    doc_id: int,
    owner_id: int,
) -> None:
    kb = crud_kb.get_kb(db, kb_id, owner_id)
    if not kb:
        logger.warning("[index] kb_not_found kb=%s owner=%s", kb_id, owner_id)
        return
    doc = crud_kb_document.get_document(db, kb_id, doc_id, owner_id)
    if not doc:
        logger.warning("[index] doc_not_found kb=%s doc=%s", kb_id, doc_id)
        return

    ingest = _json_load(getattr(doc, "ingest_params", None))
    chunk_size = int(ingest.get("chunk_size") or settings.CHUNK_SIZE_DEFAULT)
    chunk_overlap = int(ingest.get("overlap") or settings.CHUNK_OVERLAP_DEFAULT)
    parse_strategy = (ingest.get("parse_strategy") or settings.PARSE_STRATEGY_DEFAULT)
    embedding_model = ingest.get("embedding_model") or kb.embedding_model or settings.EMBEDDING_MODEL_DEFAULT

    # Resolve file path
    path = doc.storage_uri or ""
    try:
        # parse
        text = parse_file(path, ext=(doc.file_ext or None), strategy=parse_strategy)
        chunks = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        if not chunks:
            raise ValueError("No content after parsing and chunking")

        # embed
        vectors = embed_texts(chunks, model=embedding_model)
        if not vectors or len(vectors) != len(chunks):
            raise ValueError("Embedding failed or size mismatch")

        # upsert to chroma
        ids = [f"{doc.uid}_{i}" for i in range(len(chunks))]
        metas: List[Dict[str, Any]] = [
            {
                "kb_id": kb_id,
                "doc_id": doc.id,
                "doc_uid": doc.uid,
                "chunk_index": i,
                "filename": doc.filename,
            }
            for i in range(len(chunks))
        ]
        chroma_client.upsert_texts(kb.chroma_collection, ids=ids, texts=chunks, metadatas=metas, embeddings=vectors)

        # update db
        crud_kb_document.update_document_status(
            db,
            doc_id=doc.id,
            status="processed",
            error=None,
            chunk_count=len(chunks),
            processed_at=datetime.utcnow(),
        )
        logger.info("[index] done kb=%s doc=%s chunks=%s", kb_id, doc_id, len(chunks))
    except Exception as e:
        logger.exception("[index] failed kb=%s doc=%s", kb_id, doc_id)
        crud_kb_document.update_document_status(
            db,
            doc_id=doc_id,
            status="failed",
            error=str(e),
        )


def index_document_background(kb_id: int, doc_id: int, owner_id: int) -> None:
    try:
        with SessionLocal() as db:
            index_document(db, kb_id=kb_id, doc_id=doc_id, owner_id=owner_id)
    except Exception:
        logger.exception("[index] background_crashed kb=%s doc=%s", kb_id, doc_id)


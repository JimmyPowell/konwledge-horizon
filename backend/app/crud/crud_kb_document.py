from __future__ import annotations

import uuid as uuidlib
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.knowledge import KnowledgeBase, KnowledgeDocument


def _ext_from_filename(filename: str) -> Optional[str]:
    if not filename or '.' not in filename:
        return None
    ext = filename.rsplit('.', 1)[-1].lower()
    return ext[:10]


def _get_owned_kb(db: Session, kb_id: int, owner_id: int) -> Optional[KnowledgeBase]:
    return (
        db.query(KnowledgeBase)
        .filter(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.owner_id == owner_id,
            KnowledgeBase.deleted_at.is_(None),
        )
        .first()
    )


def list_documents(
    db: Session,
    kb_id: int,
    owner_id: int,
    *,
    q: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> Tuple[List[KnowledgeDocument], int]:
    # ownership via KB join
    query = (
        db.query(KnowledgeDocument)
        .join(KnowledgeBase, KnowledgeBase.id == KnowledgeDocument.kb_id)
        .filter(
            KnowledgeDocument.kb_id == kb_id,
            KnowledgeBase.owner_id == owner_id,
            KnowledgeDocument.deleted_at.is_(None),
        )
    )
    if q:
        like = f"%{q}%"
        query = query.filter(KnowledgeDocument.filename.like(like))
    if status:
        query = query.filter(KnowledgeDocument.status == status)
    total = query.count()
    rows = (
        query.order_by(desc(KnowledgeDocument.id)).limit(limit).offset(offset).all()
    )
    return rows, total


def get_document(
    db: Session,
    kb_id: int,
    doc_id: int,
    owner_id: int,
) -> Optional[KnowledgeDocument]:
    return (
        db.query(KnowledgeDocument)
        .join(KnowledgeBase, KnowledgeBase.id == KnowledgeDocument.kb_id)
        .filter(
            KnowledgeDocument.id == doc_id,
            KnowledgeDocument.kb_id == kb_id,
            KnowledgeBase.owner_id == owner_id,
            KnowledgeDocument.deleted_at.is_(None),
        )
        .first()
    )


def _recompute_kb_aggregates(db: Session, kb: KnowledgeBase) -> None:
    q = (
        db.query(
            func.count(KnowledgeDocument.id),
            func.coalesce(func.sum(KnowledgeDocument.size_bytes), 0),
        )
        .filter(
            KnowledgeDocument.kb_id == kb.id,
            KnowledgeDocument.deleted_at.is_(None),
        )
    )
    cnt, size_sum = q.first()
    kb.doc_count = int(cnt or 0)
    kb.total_size_bytes = int(size_sum or 0)
    db.add(kb)


def create_document(
    db: Session,
    kb_id: int,
    owner_id: int,
    *,
    uid: Optional[str] = None,
    filename: str,
    mime_type: Optional[str] = None,
    size_bytes: Optional[int] = None,
    storage_uri: Optional[str] = None,
    vector_source: Optional[str] = None,
    uploaded_by: Optional[int] = None,
) -> KnowledgeDocument:
    kb = _get_owned_kb(db, kb_id, owner_id)
    if not kb:
        raise ValueError("Knowledge base not found or not owned")

    uid = uid or str(uuidlib.uuid4())
    file_ext = _ext_from_filename(filename)
    if not vector_source:
        vector_source = f"doc:{uid}"

    doc = KnowledgeDocument(
        uid=uid,
        kb_id=kb.id,
        filename=filename,
        file_ext=file_ext,
        mime_type=mime_type,
        storage_uri=storage_uri,
        size_bytes=size_bytes,
        status="uploaded",
        vector_source=vector_source,
        chunk_count=0,
        uploaded_by=uploaded_by,
    )
    db.add(doc)
    db.flush()

    # update aggregates
    _recompute_kb_aggregates(db, kb)
    db.commit()
    db.refresh(doc)
    return doc


def soft_delete_document(
    db: Session,
    kb_id: int,
    doc_id: int,
    owner_id: int,
) -> bool:
    kb = _get_owned_kb(db, kb_id, owner_id)
    if not kb:
        return False
    doc = (
        db.query(KnowledgeDocument)
        .filter(
            KnowledgeDocument.id == doc_id,
            KnowledgeDocument.kb_id == kb_id,
            KnowledgeDocument.deleted_at.is_(None),
        )
        .first()
    )
    if not doc:
        return False
    from sqlalchemy.sql import func as sqlfunc
    doc.deleted_at = sqlfunc.now()
    db.add(doc)
    # Ensure the deleted_at update is flushed before recomputing aggregates
    db.flush()
    _recompute_kb_aggregates(db, kb)
    db.commit()
    return True

from __future__ import annotations

import logging
import uuid as uuidlib
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.knowledge import KnowledgeBase

logger = logging.getLogger(__name__)


def _default_collection_name(uid: str) -> str:
    return f"kb_{uid}"


def create_kb(
    db: Session,
    *,
    owner_id: int,
    name: str,
    description: Optional[str] = None,
    visibility: str = "private",
    embedding_model: Optional[str] = None,
    reranker_model: Optional[str] = None,
    use_reranker: bool = False,
) -> KnowledgeBase:
    uid = str(uuidlib.uuid4())
    chroma_collection = _default_collection_name(uid)
    kb = KnowledgeBase(
        uid=uid,
        name=name,
        description=description,
        owner_id=owner_id,
        visibility=visibility,
        chroma_collection=chroma_collection,
        embedding_model=embedding_model,
        reranker_model=reranker_model,
        use_reranker=use_reranker,
    )
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return kb


def get_kb(db: Session, kb_id: int, owner_id: int) -> Optional[KnowledgeBase]:
    return (
        db.query(KnowledgeBase)
        .filter(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.owner_id == owner_id,
            KnowledgeBase.deleted_at.is_(None),
        )
        .first()
    )


def list_kbs(
    db: Session,
    owner_id: int,
    *,
    q: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> Tuple[List[KnowledgeBase], int]:
    query = db.query(KnowledgeBase).filter(
        KnowledgeBase.owner_id == owner_id,
        KnowledgeBase.deleted_at.is_(None),
    )
    if q:
        like = f"%{q}%"
        query = query.filter(
            (KnowledgeBase.name.like(like)) | (KnowledgeBase.description.like(like))
        )
    total = query.count()
    rows = (
        query.order_by(desc(KnowledgeBase.updated_at)).limit(limit).offset(offset).all()
    )
    return rows, total


def update_kb(
    db: Session,
    kb: KnowledgeBase,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    visibility: Optional[str] = None,
    embedding_model: Optional[str] = None,
    reranker_model: Optional[str] = None,
    use_reranker: Optional[bool] = None,
) -> KnowledgeBase:
    if name is not None:
        kb.name = name
    if description is not None:
        kb.description = description
    if visibility is not None:
        kb.visibility = visibility
    if embedding_model is not None:
        kb.embedding_model = embedding_model
    if reranker_model is not None:
        kb.reranker_model = reranker_model
    if use_reranker is not None:
        kb.use_reranker = bool(use_reranker)
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return kb


def soft_delete_kb(db: Session, kb: KnowledgeBase) -> None:
    from sqlalchemy.sql import func as sqlfunc

    kb.is_active = False
    kb.deleted_at = sqlfunc.now()
    db.add(kb)
    db.commit()


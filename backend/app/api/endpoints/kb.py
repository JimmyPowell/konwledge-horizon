from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.config.mysql_config import get_mysql_db
from app import models
from app.schemas.kb import KBCreate, KBUpdate, KBOut, KBListOut
from app.crud import crud_kb
from app.utils.response import Success, BadRequest, NotFound, Created


router = APIRouter()


@router.post("/bases")
def create_kb(
    body: KBCreate,
    db: Session = Depends(get_mysql_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    # name 唯一约束在 (owner_id, name)
    # 若希望提前友好提示，可先行检查
    rows, _ = crud_kb.list_kbs(db, current_user.id, q=body.name, limit=1, offset=0)
    if rows and rows[0].name == body.name:
        return BadRequest(message="Knowledge base with same name already exists")

    kb = crud_kb.create_kb(
        db,
        owner_id=current_user.id,
        name=body.name,
        description=body.description,
        visibility=body.visibility or "private",
        embedding_model=body.embedding_model,
        reranker_model=body.reranker_model,
        use_reranker=bool(body.use_reranker),
    )
    data = KBOut.model_validate(kb).model_dump()
    return Created(data=data, message="Knowledge base created")


@router.get("/bases")
def list_kbs(
    q: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_mysql_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    rows, total = crud_kb.list_kbs(db, current_user.id, q=q, limit=limit, offset=offset)
    items = [KBOut.model_validate(r).model_dump() for r in rows]
    return Success(data={"items": items, "total": total})


@router.get("/bases/{kb_id}")
def get_kb(
    kb_id: int,
    db: Session = Depends(get_mysql_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    kb = crud_kb.get_kb(db, kb_id, current_user.id)
    if not kb:
        return NotFound(message="Knowledge base not found")
    return Success(data=KBOut.model_validate(kb).model_dump())


@router.patch("/bases/{kb_id}")
def update_kb(
    kb_id: int,
    body: KBUpdate,
    db: Session = Depends(get_mysql_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    kb = crud_kb.get_kb(db, kb_id, current_user.id)
    if not kb:
        return NotFound(message="Knowledge base not found")
    kb = crud_kb.update_kb(
        db,
        kb,
        name=body.name,
        description=body.description,
        visibility=body.visibility,
        embedding_model=body.embedding_model,
        reranker_model=body.reranker_model,
        use_reranker=body.use_reranker,
    )
    return Success(data=KBOut.model_validate(kb).model_dump(), message="Updated")


@router.delete("/bases/{kb_id}")
def delete_kb(
    kb_id: int,
    db: Session = Depends(get_mysql_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    kb = crud_kb.get_kb(db, kb_id, current_user.id)
    if not kb:
        return NotFound(message="Knowledge base not found")
    crud_kb.soft_delete_kb(db, kb)
    return Success(message="Deleted")

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File
import os
import pathlib
import uuid as uuidlib
from sqlalchemy.orm import Session

from app.api import deps
from app.config.mysql_config import get_mysql_db
from app import models
from app.schemas.kb import KBCreate, KBUpdate, KBOut, KBListOut
from app.schemas.kb_document import DocumentCreate, DocumentOut, DocumentListOut
from app.crud import crud_kb, crud_kb_document
from app.utils.response import Success, BadRequest, NotFound, Created
from app.config.settings import settings


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
    data = KBOut.model_validate(kb).model_dump(mode='json')
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
    items = [KBOut.model_validate(r).model_dump(mode='json') for r in rows]
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
    return Success(data=KBOut.model_validate(kb).model_dump(mode='json'))


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
    return Success(data=KBOut.model_validate(kb).model_dump(mode='json'), message="Updated")


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


# ------------------ Documents under a KB ------------------

@router.get("/bases/{kb_id}/documents")
def list_documents(
    kb_id: int,
    q: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_mysql_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    rows, total = crud_kb_document.list_documents(
        db, kb_id, current_user.id, q=q, status=status, limit=limit, offset=offset
    )
    items = [DocumentOut.model_validate(r).model_dump(mode='json') for r in rows]
    return Success(data={"items": items, "total": total})


@router.get("/bases/{kb_id}/documents/{doc_id}")
def get_document(
    kb_id: int,
    doc_id: int,
    db: Session = Depends(get_mysql_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    doc = crud_kb_document.get_document(db, kb_id, doc_id, current_user.id)
    if not doc:
        return NotFound(message="Document not found")
    return Success(data=DocumentOut.model_validate(doc).model_dump(mode='json'))


@router.post("/bases/{kb_id}/documents")
def create_document(
    kb_id: int,
    body: DocumentCreate,
    db: Session = Depends(get_mysql_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    try:
        doc = crud_kb_document.create_document(
            db,
            kb_id,
            current_user.id,
            filename=body.filename,
            mime_type=body.mime_type,
            size_bytes=body.size_bytes,
            storage_uri=body.storage_uri,
            vector_source=body.vector_source,
            uploaded_by=current_user.id,
        )
    except ValueError:
        return NotFound(message="Knowledge base not found")
    return Created(data=DocumentOut.model_validate(doc).model_dump(mode='json'))


@router.delete("/bases/{kb_id}/documents/{doc_id}")
def delete_document(
    kb_id: int,
    doc_id: int,
    db: Session = Depends(get_mysql_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    ok = crud_kb_document.soft_delete_document(db, kb_id, doc_id, current_user.id)
    if not ok:
        return NotFound(message="Document not found")
    return Success(message="Deleted")


def _sanitize_filename(name: str) -> str:
    base = os.path.basename(name)
    # allow letters, digits, dot, dash, underscore, space
    safe = []
    for ch in base:
        if ch.isalnum() or ch in ('.', '-', '_', ' '):
            safe.append(ch)
        else:
            safe.append('_')
    out = ''.join(safe).strip()
    return out or 'file'


@router.post("/bases/{kb_id}/documents/upload")
def upload_document(
    kb_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_mysql_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    # Validate extension and size while streaming to disk
    orig_name = file.filename or 'file'
    filename = _sanitize_filename(orig_name)
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    allowed_exts = { 'pdf', 'doc', 'docx', 'txt', 'md' }
    if ext not in allowed_exts:
        return BadRequest(message=f"Unsupported file type: .{ext}")

    uid = str(uuidlib.uuid4())
    rel_dir = os.path.join('kb', str(kb_id), uid)
    storage_dir = os.path.join(settings.STORAGE_ROOT, rel_dir)
    try:
        os.makedirs(storage_dir, exist_ok=True)
    except Exception:
        return BadRequest(message="Failed to prepare storage path")

    abs_path = os.path.join(storage_dir, filename)
    bytes_written = 0
    try:
        with open(abs_path, 'wb') as f:
            while True:
                chunk = file.file.read(1024 * 1024)
                if not chunk:
                    break
                bytes_written += len(chunk)
                if bytes_written > settings.MAX_UPLOAD_BYTES:
                    try:
                        f.close()
                        os.remove(abs_path)
                    except Exception:
                        pass
                    return BadRequest(message="File too large")
                f.write(chunk)
    except Exception:
        try:
            if os.path.exists(abs_path):
                os.remove(abs_path)
        except Exception:
            pass
        return BadRequest(message="Failed to save file")
    finally:
        try:
            file.file.close()
        except Exception:
            pass

    storage_uri = f"{settings.STORAGE_ROOT}/{rel_dir}/{filename}"
    mime = file.content_type or None

    try:
        doc = crud_kb_document.create_document(
            db,
            kb_id,
            current_user.id,
            uid=uid,
            filename=filename,
            mime_type=mime,
            size_bytes=bytes_written,
            storage_uri=storage_uri,
            vector_source=f"doc:{uid}",
            uploaded_by=current_user.id,
        )
    except ValueError:
        # Clean up file if KB not found/owned
        try:
            os.remove(abs_path)
        except Exception:
            pass
        return NotFound(message="Knowledge base not found")

    return Created(data=DocumentOut.model_validate(doc).model_dump(mode='json'))

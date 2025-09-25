from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
import logging
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api import deps
from app.config.mysql_config import get_mysql_db
from app import models, schemas
from app.schemas.chat import ConversationCreate, ConversationOut, MessageCreate, MessageOut, SendMessageResponse
from app.utils.response import Success, BadRequest, NotFound
from app.crud import crud_chat
from app.services import chat_service


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/conversations")
def create_conversation(
    body: ConversationCreate,
    db: Session = Depends(get_mysql_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    conv = crud_chat.create_conversation(
        db,
        user_id=current_user.id,
        title=body.title,
        kb_ids=body.kb_ids or [],
        model=body.model,
    )
    kb_ids = crud_chat.list_conversation_kb_ids(db, conv.id)
    data = {
        "id": conv.id,
        "uid": conv.uid,
        "title": conv.title,
        "kb_ids": kb_ids,
        "model": conv.model,
    }
    return Success(data=data, message="Conversation created")


@router.get("/conversations")
def list_conversations(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_mysql_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    rows = crud_chat.list_user_conversations(db, current_user.id, limit=limit, offset=offset)
    out = []
    for c in rows:
        kb_ids = crud_chat.list_conversation_kb_ids(db, c.id)
        out.append({
            "id": c.id,
            "uid": c.uid,
            "title": c.title,
            "kb_ids": kb_ids,
            "model": c.model,
            "last_message_at": c.last_message_at.isoformat() if c.last_message_at else None,
        })
    return Success(data=out)


@router.get("/conversations/{conversation_id}/messages")
def list_messages(
    conversation_id: int,
    limit: int = 50,
    before: Optional[int] = None,
    db: Session = Depends(get_mysql_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    rows = crud_chat.list_messages(db, conversation_id, current_user.id, limit=limit, before_id=before, asc=True)
    data = [{
        "id": m.id,
        "role": m.role,
        "content": m.content,
        "model": m.model,
        "created_at": m.created_at.isoformat() if m.created_at else None,
    } for m in rows]
    return Success(data=data)


@router.post("/conversations/{conversation_id}/messages")
def send_message(
    conversation_id: int,
    body: MessageCreate,
    db: Session = Depends(get_mysql_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    conv = crud_chat.get_conversation(db, conversation_id, current_user.id)
    if not conv:
        return NotFound(message="Conversation not found")

    user_msg, asst_msg = chat_service.non_stream_chat(
        db,
        conversation_id=conversation_id,
        user_id=current_user.id,
        content=body.content,
        model=body.model or conv.model,
        temperature=body.temperature,
        top_p=body.top_p,
        max_tokens=body.max_tokens,
    )

    user_dict = {
        "id": user_msg.id,
        "role": user_msg.role,
        "content": user_msg.content,
        "created_at": user_msg.created_at.isoformat() if user_msg.created_at else None,
    }
    assistant_dict = {
        "id": asst_msg.id,
        "role": asst_msg.role,
        "content": asst_msg.content,
        "model": asst_msg.model,
        "tokens_prompt": asst_msg.tokens_prompt,
        "tokens_completion": asst_msg.tokens_completion,
        "latency_ms": asst_msg.latency_ms,
        "created_at": asst_msg.created_at.isoformat() if asst_msg.created_at else None,
    }

    # 为前端更易用的结构提供别名与数组，便于直接 append 渲染
    data = {
        "conversation_id": conversation_id,
        "user_message": user_dict,
        "assistant_message": assistant_dict,
        # 别名（兼容不同前端消费习惯）
        "user": user_dict,
        "assistant": assistant_dict,
        # 顺序消息数组，直接用于前端渲染
        "messages": [user_dict, assistant_dict],
    }
    try:
        logger.info(
            "[api.chat] reply_ready conv=%s user_msg=%s asst_msg=%s asst_len=%s",
            conversation_id,
            user_msg.id,
            asst_msg.id,
            len(assistant_dict.get("content") or ""),
        )
    except Exception:
        pass
    return Success(data=data)


@router.post("/conversations/{conversation_id}/messages/stream")
def send_message_stream(
    conversation_id: int,
    body: MessageCreate,
    db: Session = Depends(get_mysql_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    conv = crud_chat.get_conversation(db, conversation_id, current_user.id)
    if not conv:
        return NotFound(message="Conversation not found")

    gen = chat_service.stream_chat_generator(
        db,
        conversation_id=conversation_id,
        user_id=current_user.id,
        content=body.content,
        model=body.model or conv.model,
        temperature=body.temperature,
        top_p=body.top_p,
        max_tokens=body.max_tokens,
    )
    logger.info("[api.chat] stream_begin conv=%s", conversation_id)
    resp = StreamingResponse(gen, media_type="text/event-stream")
    resp.headers["Cache-Control"] = "no-cache"
    resp.headers["Connection"] = "keep-alive"
    resp.headers["X-Accel-Buffering"] = "no"
    return resp

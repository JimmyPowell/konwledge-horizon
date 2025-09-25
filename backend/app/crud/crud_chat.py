from __future__ import annotations

import uuid as uuidlib
import logging
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.chat import Conversation, ConversationKB, Message

logger = logging.getLogger(__name__)


def create_conversation(db: Session, user_id: int, title: Optional[str], kb_ids: Optional[List[int]], model: Optional[str]) -> Conversation:
    conv = Conversation(
        uid=str(uuidlib.uuid4()),
        user_id=user_id,
        title=title,
        model=model,
    )
    db.add(conv)
    db.flush()
    if kb_ids:
        for kb_id in kb_ids:
            db.add(ConversationKB(conversation_id=conv.id, kb_id=kb_id))
    db.commit()
    db.refresh(conv)
    return conv


def list_user_conversations(db: Session, user_id: int, limit: int = 20, offset: int = 0) -> List[Conversation]:
    q = (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id, Conversation.deleted_at.is_(None))
        .order_by(desc(Conversation.last_message_at.nullslast()), desc(Conversation.id))
        .limit(limit)
        .offset(offset)
    )
    return q.all()


def get_conversation(db: Session, conversation_id: int, user_id: int) -> Optional[Conversation]:
    return (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == user_id, Conversation.deleted_at.is_(None))
        .first()
    )


def list_conversation_kb_ids(db: Session, conversation_id: int) -> List[int]:
    rows = db.query(ConversationKB).filter(ConversationKB.conversation_id == conversation_id).all()
    return [r.kb_id for r in rows]


def add_message(db: Session, conversation_id: int, role: str, content: Optional[str], model: Optional[str] = None,
                tokens_prompt: Optional[int] = None, tokens_completion: Optional[int] = None,
                latency_ms: Optional[int] = None, error: Optional[str] = None) -> Message:
    msg = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        model=model,
        tokens_prompt=tokens_prompt,
        tokens_completion=tokens_completion,
        latency_ms=latency_ms,
        error=error,
    )
    db.add(msg)

    # update conversation timestamps
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conv:
        from sqlalchemy.sql import func as sqlfunc
        if conv.first_message_at is None:
            conv.first_message_at = sqlfunc.now()
        conv.last_message_at = sqlfunc.now()

    db.commit()
    db.refresh(msg)
    try:
        preview = (content or error or "")[:120]
        logger.info(
            "[crud_chat] message_persisted conv=%s id=%s role=%s model=%s len=%s preview=%r",
            conversation_id,
            msg.id,
            role,
            model,
            len(content or ""),
            preview,
        )
    except Exception:
        pass
    return msg


def list_messages(db: Session, conversation_id: int, user_id: int, limit: int = 50, before_id: Optional[int] = None,
                  asc: bool = True) -> List[Message]:
    # ownership check via join on conversation
    q = db.query(Message).join(Conversation, Conversation.id == Message.conversation_id).\
        filter(Conversation.id == conversation_id, Conversation.user_id == user_id, Conversation.deleted_at.is_(None))
    if before_id:
        q = q.filter(Message.id < before_id)
    order = Message.id.asc() if asc else Message.id.desc()
    q = q.order_by(order).limit(limit)
    rows = q.all()
    return rows


def get_recent_messages_for_context(db: Session, conversation_id: int, user_id: int, max_turns: int) -> List[Message]:
    # Fetch last 2*max_turns messages ordered desc then reverse
    q = db.query(Message).join(Conversation, Conversation.id == Message.conversation_id).\
        filter(Conversation.id == conversation_id, Conversation.user_id == user_id, Conversation.deleted_at.is_(None)).\
        order_by(desc(Message.id)).limit(max_turns * 2)
    rows = q.all()
    rows.reverse()
    return rows

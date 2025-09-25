from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    title: Optional[str] = None
    kb_ids: Optional[List[int]] = None
    model: Optional[str] = None


class ConversationOut(BaseModel):
    id: int
    uid: str
    title: Optional[str]
    kb_ids: List[int] = []
    model: Optional[str] = None

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    content: str
    # generation params (optional)
    temperature: Optional[float] = Field(default=None, ge=0, le=2)
    top_p: Optional[float] = Field(default=None, ge=0, le=1)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    model: Optional[str] = None
    idempotency_key: Optional[str] = None


class MessageOut(BaseModel):
    id: int
    role: str
    content: Optional[str]
    model: Optional[str] = None
    tokens_prompt: Optional[int] = None
    tokens_completion: Optional[int] = None
    latency_ms: Optional[int] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class SendMessageResponse(BaseModel):
    user_message: MessageOut
    assistant_message: MessageOut
    conversation_id: int


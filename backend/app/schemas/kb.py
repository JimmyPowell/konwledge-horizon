from __future__ import annotations

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class KBBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    visibility: Optional[str] = Field(default="private")
    embedding_model: Optional[str] = None
    reranker_model: Optional[str] = None
    use_reranker: Optional[bool] = False


class KBCreate(KBBase):
    pass


class KBUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = None
    visibility: Optional[str] = None
    embedding_model: Optional[str] = None
    reranker_model: Optional[str] = None
    use_reranker: Optional[bool] = None


class KBOut(BaseModel):
    id: int
    uid: str
    name: str
    description: Optional[str] = None
    visibility: str
    is_active: bool
    chroma_collection: str
    embedding_model: Optional[str] = None
    reranker_model: Optional[str] = None
    use_reranker: bool
    doc_count: int
    total_size_bytes: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class KBListOut(BaseModel):
    items: List[KBOut]
    total: int

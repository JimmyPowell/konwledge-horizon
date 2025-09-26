from __future__ import annotations

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    filename: str = Field(..., max_length=255)
    mime_type: Optional[str] = None
    size_bytes: Optional[int] = None
    storage_uri: Optional[str] = None
    vector_source: Optional[str] = None  # if omitted, will be auto-generated


class DocumentOut(BaseModel):
    id: int
    uid: str
    kb_id: int
    filename: str
    file_ext: Optional[str] = None
    mime_type: Optional[str] = None
    storage_uri: Optional[str] = None
    size_bytes: Optional[int] = None
    page_count: Optional[int] = None
    status: str
    error: Optional[str] = None
    processed_at: Optional[datetime] = None
    vector_source: str
    chunk_count: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentListOut(BaseModel):
    items: List[DocumentOut]
    total: int


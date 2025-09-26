from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    TIMESTAMP,
    BigInteger,
)
from sqlalchemy.sql import func

from app.config.database import Base


class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(36), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    visibility = Column(String(16), nullable=False, default="private")
    is_active = Column(Boolean, default=True)

    chroma_collection = Column(String(128), nullable=False, unique=True)
    embedding_model = Column(String(128), nullable=True)
    reranker_model = Column(String(128), nullable=True)
    use_reranker = Column(Boolean, default=False)

    doc_count = Column(Integer, nullable=False, default=0)
    total_size_bytes = Column(BigInteger, nullable=False, default=0)
    last_indexed_at = Column(TIMESTAMP, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True, index=True)


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(36), unique=True, index=True, nullable=False)
    kb_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False, index=True)

    filename = Column(String(255), nullable=False)
    file_ext = Column(String(10), nullable=True)
    mime_type = Column(String(100), nullable=True)
    storage_uri = Column(String(255), nullable=True)
    size_bytes = Column(BigInteger, nullable=True)
    page_count = Column(Integer, nullable=True)

    status = Column(String(16), nullable=False, default="uploaded")
    error = Column(Text, nullable=True)
    processed_at = Column(TIMESTAMP, nullable=True)

    vector_source = Column(String(255), nullable=False)
    chunk_count = Column(Integer, nullable=False, default=0)
    embedding_model = Column(String(128), nullable=True)
    ingest_params = Column(Text, nullable=True)

    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True, index=True)


class KBSharedUser(Base):
    __tablename__ = "kb_shared_users"

    id = Column(Integer, primary_key=True, index=True)
    kb_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String(16), nullable=False, default="viewer")
    created_at = Column(TIMESTAMP, server_default=func.now())


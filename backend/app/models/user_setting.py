from __future__ import annotations

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Float
from sqlalchemy import JSON
from sqlalchemy.sql import func

from app.config.database import Base


class UserSetting(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False, unique=True)

    # core chat preferences
    streaming = Column(Boolean, default=True, nullable=False)
    web_search = Column(Boolean, default=False, nullable=False)
    default_kb_id = Column(Integer, nullable=True, index=True)
    model = Column(String(128), nullable=True)
    temperature = Column(Float, nullable=True)
    top_p = Column(Float, nullable=True)
    max_tokens = Column(Integer, nullable=True)

    # flexible buckets
    tools = Column(JSON, nullable=True)
    extra = Column(JSON, nullable=True)

    # optimistic locking + audit
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


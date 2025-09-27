from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class SettingsBase(BaseModel):
    streaming: Optional[bool] = None
    web_search: Optional[bool] = None
    default_kb_id: Optional[int] = Field(default=None, ge=1)
    model: Optional[str] = None
    temperature: Optional[float] = Field(default=None, ge=0, le=2)
    top_p: Optional[float] = Field(default=None, ge=0, le=1)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    tools: Optional[Dict[str, Any]] = None
    extra: Optional[Dict[str, Any]] = None


class SettingsRead(SettingsBase):
    version: int = 1
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class SettingsUpdate(SettingsBase):
    # required for optimistic locking
    version: int = Field(..., ge=1)


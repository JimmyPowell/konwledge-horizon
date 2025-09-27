from __future__ import annotations

import json
from typing import Any, Dict, Optional, Tuple

from redis import Redis
from sqlalchemy.orm import Session

from app.config.settings import settings as app_settings
from app.crud import crud_user_setting
from app.models.user_setting import UserSetting


def _default_user_settings() -> Dict[str, Any]:
    """System-level defaults derived from environment configuration."""
    return {
        "streaming": True,
        "web_search": False,
        "default_kb_id": None,
        "model": app_settings.LLM_DEFAULT_MODEL,
        "temperature": 0.3,
        "top_p": 1.0,
        "max_tokens": app_settings.LLM_MAX_TOKENS,
        "tools": {"mcp": False},
        "extra": {},
        "version": 1,
    }


def _cache_key(user_id: int) -> str:
    return f"settings:user:{user_id}"


def get_effective_settings(
    db: Session,
    user_id: int,
    redis_client: Optional[Redis] = None,
) -> Dict[str, Any]:
    """Return merged settings: system defaults overlaid by user's persisted settings.

    Optionally uses Redis for read caching.
    """
    key = _cache_key(user_id)
    if redis_client is not None:
        try:
            cached = redis_client.get(key)
            if cached:
                return json.loads(cached.decode("utf-8"))
        except Exception:
            pass

    defaults = _default_user_settings()
    row = crud_user_setting.get_by_user(db, user_id)
    if row is None:
        # lazily create with defaults so version starts at 1
        row = crud_user_setting.create_default(
            db, user_id, {k: v for k, v in defaults.items() if k in {
                "streaming", "web_search", "default_kb_id", "model", "temperature", "top_p", "max_tokens", "tools", "extra"
            }}
        )

    out = {
        **defaults,
        "streaming": row.streaming,
        "web_search": row.web_search,
        "default_kb_id": row.default_kb_id,
        "model": row.model or defaults["model"],
        "temperature": row.temperature if row.temperature is not None else defaults["temperature"],
        "top_p": row.top_p if row.top_p is not None else defaults["top_p"],
        "max_tokens": row.max_tokens if row.max_tokens is not None else defaults["max_tokens"],
        "tools": row.tools or defaults["tools"],
        "extra": row.extra or defaults["extra"],
        "version": row.version,
        "updated_at": row.updated_at.isoformat() if getattr(row, "updated_at", None) else None,
    }

    if redis_client is not None:
        try:
            redis_client.setex(key, 300, json.dumps(out, ensure_ascii=False))
        except Exception:
            pass
    return out


def update_settings(
    db: Session,
    user_id: int,
    partial: Dict[str, Any],
    expected_version: int,
    redis_client: Optional[Redis] = None,
) -> Tuple[Dict[str, Any], Optional[str]]:
    """Update user settings using optimistic locking.

    Returns (settings_dict, error). If conflict occurs, error is "version_conflict".
    """
    row: Optional[UserSetting] = crud_user_setting.get_by_user(db, user_id)
    if row is None:
        # allow creating a new row if no settings exist yet; expect version==1
        if expected_version != 1:
            return {}, "version_conflict"
        row = crud_user_setting.create_default(db, user_id, {})

    if row.version != expected_version:
        return get_effective_settings(db, user_id, redis_client), "version_conflict"

    allowed_fields = {
        "streaming", "web_search", "default_kb_id", "model", "temperature", "top_p", "max_tokens", "tools", "extra"
    }
    # Only apply keys that are explicitly provided and not None
    updates = {k: v for k, v in partial.items() if k in allowed_fields and v is not None}
    # bump version on every successful update
    updates["version"] = row.version + 1

    row = crud_user_setting.update_partial(db, row, updates)

    # invalidate cache
    if redis_client is not None:
        try:
            redis_client.delete(_cache_key(user_id))
        except Exception:
            pass

    return get_effective_settings(db, user_id, redis_client), None

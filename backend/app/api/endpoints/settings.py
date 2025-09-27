from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from redis import Redis

from app import models
from app.api import deps
from app.config.mysql_config import get_mysql_db
from app.config.redis_config import get_redis_client
from app.utils.response import Success, BadRequest
from app.schemas.settings import SettingsRead, SettingsUpdate
from app.services import settings_service
from app.crud import crud_kb


router = APIRouter()


@router.get("/me")
def get_my_settings(
    db: Session = Depends(get_mysql_db),
    redis_client: Redis = Depends(get_redis_client),
    current_user: models.User = Depends(deps.get_current_user),
):
    data = settings_service.get_effective_settings(db, current_user.id, redis_client)
    return Success(data=SettingsRead(**data).dict())


@router.patch("/me")
def update_my_settings(
    body: SettingsUpdate,
    db: Session = Depends(get_mysql_db),
    redis_client: Redis = Depends(get_redis_client),
    current_user: models.User = Depends(deps.get_current_user),
):
    # Only include fields explicitly provided and not None to honor PATCH semantics
    try:
        payload = body.dict(exclude_none=True, exclude_unset=True)  # pydantic v1/compat
    except TypeError:
        # fallback in case of pydantic version differences
        payload = body.dict()

    # Optional validation: ensure default_kb_id belongs to user if provided
    kb_id = payload.get("default_kb_id")
    if kb_id is not None:
        kb = crud_kb.get_kb(db, int(kb_id), current_user.id)
        if not kb:
            return BadRequest(message="Invalid knowledge base id")

    version = payload.pop("version")
    data, err = settings_service.update_settings(db, current_user.id, payload, version, redis_client)
    if err == "version_conflict":
        return BadRequest(message="Version conflict. Refresh settings and retry.")
    return Success(data=SettingsRead(**data).dict())

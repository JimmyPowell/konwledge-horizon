from __future__ import annotations

from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user_setting import UserSetting


def get_by_user(db: Session, user_id: int) -> Optional[UserSetting]:
    return db.execute(
        select(UserSetting).where(UserSetting.user_id == user_id)
    ).scalars().first()


def create_default(db: Session, user_id: int, defaults: Dict[str, Any]) -> UserSetting:
    row = UserSetting(user_id=user_id, **defaults)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_partial(
    db: Session,
    row: UserSetting,
    updates: Dict[str, Any],
) -> UserSetting:
    for k, v in updates.items():
        setattr(row, k, v)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


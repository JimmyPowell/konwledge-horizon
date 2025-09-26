from __future__ import annotations

import logging
import re
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.config.settings import settings
from app.config.mysql_config import SessionLocal
from app.crud import crud_chat
from app.models.chat import Message
from app.services.llm_service import llm_client

logger = logging.getLogger(__name__)


def _collapse_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def sanitize_title(raw: Optional[str]) -> str:
    if not raw:
        return ""
    s = str(raw).strip()
    # remove surrounding quotes and similar marks
    quotes = "\"'“”‘’「」『』‹›«»`"
    s = s.strip(quotes)
    # collapse whitespace/newlines
    s = _collapse_spaces(s)
    # trim trailing punctuation
    s = s.rstrip("。.!?？：:;，, …")
    # enforce length
    max_len = int(getattr(settings, "TITLE_MAX_LENGTH_CHARS", 40) or 40)
    if len(s) > max_len:
        s = s[:max_len].rstrip()
    return s


def build_title_prompt(seed_messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    system_prompt = (
        "请基于这段对话生成一个简洁、具体的标题。"
        "只输出标题本身，不要添加引号或标点。"
        "不超过12个汉字或8个英文单词，尽量贴合用户语言。"
        "避免使用泛化词（如：帮助、聊天、问答等）。"
    )
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": system_prompt}
    ]
    messages.extend(seed_messages)
    return messages


def _pick_seed_messages(msgs: List[Message]) -> List[Dict[str, str]]:
    # Prioritize first user and first assistant; fallback to first single message
    user_content: Optional[str] = None
    asst_content: Optional[str] = None
    for m in msgs:
        if not user_content and m.role == "user" and m.content:
            user_content = m.content
        if not asst_content and m.role == "assistant" and m.content:
            asst_content = m.content
        if user_content and asst_content:
            break
    seed: List[Dict[str, str]] = []
    if user_content:
        seed.append({"role": "user", "content": user_content})
    if asst_content:
        seed.append({"role": "assistant", "content": asst_content})
    if not seed and msgs:
        # fallback to the first message regardless of role
        m0 = msgs[0]
        if m0.content:
            seed.append({"role": m0.role, "content": m0.content})
    return seed


def generate_title_from_messages(seed: List[Dict[str, str]]) -> Optional[str]:
    if not seed:
        return None
    try:
        resp = llm_client.chat_completion(
            messages=build_title_prompt(seed),
            model=(settings.LLM_TITLE_MODEL or settings.LLM_DEFAULT_MODEL),
            temperature=0.3,
            max_tokens=getattr(settings, "TITLE_MAX_TOKENS", 32) or 32,
            top_p=1.0,
        )
    except Exception:
        logger.exception("[title_service] llm_chat_failed")
        return None

    try:
        choice = (resp.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        content_out = message.get("content") or choice.get("text")
        return sanitize_title(content_out)
    except Exception:
        logger.debug("[title_service] parse_llm_response_failed")
        return None


def _fallback_title(seed: List[Dict[str, str]]) -> str:
    # Prefer first user content
    for item in seed:
        if item.get("role") == "user" and item.get("content"):
            return sanitize_title(item["content"]) or "新对话"
    # Else any content
    for item in seed:
        if item.get("content"):
            return sanitize_title(item["content"]) or "新对话"
    return "新对话"


def generate_and_save_if_needed(db: Session, conversation_id: int, user_id: int, *, force: bool = False) -> Optional[str]:
    conv = crud_chat.get_conversation(db, conversation_id, user_id)
    if not conv:
        logger.info("[title_service] conv_not_found conv=%s user=%s", conversation_id, user_id)
        return None
    if conv.title and not force:
        return conv.title

    msgs = crud_chat.get_first_messages_for_title(db, conversation_id, max_fetch=6)
    seed = _pick_seed_messages(msgs)
    title = generate_title_from_messages(seed)
    if not title:
        title = _fallback_title(seed)

    updated = crud_chat.update_conversation_title(db, conversation_id, title)
    return updated.title if updated else None


def generate_and_save_if_needed_background(conversation_id: int, user_id: int, *, force: bool = False) -> None:
    """Background-friendly wrapper that manages its own DB session."""
    try:
        with SessionLocal() as db:
            title = generate_and_save_if_needed(db, conversation_id, user_id, force=force)
            logger.info("[title_service] background_title_done conv=%s title=%r", conversation_id, title)
    except Exception:
        logger.exception("[title_service] background_failed conv=%s", conversation_id)


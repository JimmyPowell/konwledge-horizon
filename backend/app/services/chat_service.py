from __future__ import annotations

import time
import logging
from typing import Dict, Iterable, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.config.settings import settings
from app.crud import crud_chat
from app.models.chat import Message
from app.services.llm_service import llm_client

logger = logging.getLogger(__name__)


def build_context_messages(db: Session, conversation_id: int, user_id: int, new_content: str,
                           model: Optional[str] = None) -> List[Dict[str, str]]:
    # Fetch recent messages (last N turns)
    history: List[Message] = crud_chat.get_recent_messages_for_context(
        db, conversation_id=conversation_id, user_id=user_id, max_turns=settings.LLM_MAX_TURNS
    )
    msgs: List[Dict[str, str]] = []
    # Optional system prompt could be added here
    # msgs.append({"role": "system", "content": "You are a helpful assistant."})

    for m in history:
        if m.role not in ("user", "assistant", "system"):
            continue
        if m.content:
            msgs.append({"role": m.role, "content": m.content})

    # Append the new user message
    msgs.append({"role": "user", "content": new_content})
    return msgs


def non_stream_chat(
    db: Session,
    conversation_id: int,
    user_id: int,
    content: str,
    *,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> Tuple[Message, Message]:
    # persist user message
    logger.info(
        "[non_stream_chat] start conv=%s user=%s model=%s content_len=%s",
        conversation_id,
        user_id,
        (settings.LLM_DEFAULT_MODEL if model is None else model),
        len(content) if content is not None else 0,
    )
    user_msg = crud_chat.add_message(db, conversation_id, role="user", content=content)

    # build context
    msgs = build_context_messages(db, conversation_id, user_id, new_content=content, model=model)
    logger.info(
        "[non_stream_chat] context_built conv=%s turns=%s",
        conversation_id,
        len(msgs),
    )

    t0 = time.time()
    try:
        resp = llm_client.chat_completion(
            messages=msgs,
            model=model or settings.LLM_DEFAULT_MODEL,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens or settings.LLM_MAX_TOKENS,
        )
    except Exception:
        logger.exception("[non_stream_chat] llm_chat_completion_failed conv=%s", conversation_id)
        raise
    latency_ms = int((time.time() - t0) * 1000)

    # parse response
    choice = (resp.get("choices") or [{}])[0]
    message = choice.get("message") or {}
    content_out: Optional[str] = message.get("content")
    if not content_out:
        # Fallback for providers that return plain text at choices[0].text
        content_out = choice.get("text")
    usage = resp.get("usage") or {}
    tokens_prompt = usage.get("prompt_tokens")
    tokens_completion = usage.get("completion_tokens")
    logger.info(
        "[non_stream_chat] llm_done conv=%s latency_ms=%s out_len=%s prompt_tokens=%s completion_tokens=%s",
        conversation_id,
        latency_ms,
        (len(content_out) if content_out else 0),
        tokens_prompt,
        tokens_completion,
    )
    try:
        preview = (content_out or "")[:200]
        logger.info("[non_stream_chat] llm_output_preview conv=%s preview=%r", conversation_id, preview)
    except Exception:
        pass

    asst_msg = crud_chat.add_message(
        db,
        conversation_id,
        role="assistant",
        content=content_out,
        model=(resp.get("model") or model or settings.LLM_DEFAULT_MODEL),
        tokens_prompt=tokens_prompt,
        tokens_completion=tokens_completion,
        latency_ms=latency_ms,
    )
    return user_msg, asst_msg


def stream_chat_generator(
    db: Session,
    conversation_id: int,
    user_id: int,
    content: str,
    *,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> Iterable[str]:
    # persist user message first
    logger.info(
        "[stream_chat] start conv=%s user=%s model=%s content_len=%s",
        conversation_id,
        user_id,
        (settings.LLM_DEFAULT_MODEL if model is None else model),
        len(content) if content is not None else 0,
    )
    user_msg = crud_chat.add_message(db, conversation_id, role="user", content=content)
    logger.info(
        "[stream_chat] user_message_persisted conv=%s msg_id=%s",
        conversation_id,
        user_msg.id,
    )

    msgs = build_context_messages(db, conversation_id, user_id, new_content=content, model=model)

    t0 = time.time()
    accumulated: List[str] = []

    def yield_sse(data: str) -> str:
        return f"data: {data}\n\n"

    # forward provider SSE lines
    try:
        logger.info("[stream_chat] llm_stream_begin conv=%s", conversation_id)
        chunk_idx = 0
        for raw in llm_client.chat_completion_stream(
            messages=msgs,
            model=model or settings.LLM_DEFAULT_MODEL,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens or settings.LLM_MAX_TOKENS,
        ):
            line = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else str(raw)
            if not line:
                continue

            # Provider usually sends lines starting with 'data:' and ends an event with a blank line.
            # We normalize to our own SSE frame to guarantee '\n\n' separation.
            if line.startswith("data:"):
                payload_str = line[len("data:"):].strip()
                logger.debug(
                    "[stream_chat] recv_chunk conv=%s idx=%s bytes=%s preview=%r",
                    conversation_id,
                    chunk_idx,
                    len(payload_str),
                    payload_str[:120],
                )
                # Forward normalized SSE frame to client
                yield yield_sse(payload_str)
                chunk_idx += 1

                # Accumulate text from JSON payload
                try:
                    import json as _json
                    if payload_str == "[DONE]":
                        continue
                    payload = _json.loads(payload_str)
                    choice = (payload.get("choices") or [{}])[0]
                    msg = choice.get("message") or {}
                    delta = choice.get("delta") or {}
                    piece = msg.get("content") or delta.get("content")
                    if piece:
                        accumulated.append(piece)
                except Exception:
                    # parsing errors are ignored but logged at debug
                    logger.debug("[stream_chat] chunk_parse_failed conv=%s", conversation_id)
            else:
                # Ignore non-data lines but keep a debug trace
                logger.debug("[stream_chat] ignore_line conv=%s line=%r", conversation_id, line[:80])

        logger.info("[stream_chat] llm_stream_end conv=%s chunks=%s", conversation_id, chunk_idx)
    finally:
        # persist assistant message
        latency_ms = int((time.time() - t0) * 1000)
        content_out = "".join(accumulated) if accumulated else None
        asst = crud_chat.add_message(
            db,
            conversation_id,
            role="assistant",
            content=content_out,
            model=model or settings.LLM_DEFAULT_MODEL,
            latency_ms=latency_ms,
        )
        logger.info(
            "[stream_chat] assistant_persisted conv=%s msg_id=%s latency_ms=%s out_len=%s",
            conversation_id,
            asst.id if asst else None,
            latency_ms,
            len(content_out) if content_out else 0,
        )

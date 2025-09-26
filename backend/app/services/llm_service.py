from __future__ import annotations

import time
import logging
from typing import Dict, Iterable, List, Optional

import httpx

from app.config.settings import settings

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or settings.SILICONFLOW_API_KEY
        self.base_url = (base_url or settings.LLM_API_BASE).rstrip("/")
        if not self.api_key:
            raise ValueError("SILICONFLOW_API_KEY not configured")

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        *,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict:
        """Non-streaming chat completion. Returns parsed JSON dict."""
        url = f"{self.base_url}/chat/completions"
        payload: Dict = {
            "model": model or settings.LLM_DEFAULT_MODEL,
            "messages": messages,
        }
        if temperature is not None:
            payload["temperature"] = temperature
        if top_p is not None:
            payload["top_p"] = top_p
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        logger.info(
            "[llm.chat_completion] request model=%s msgs=%s temperature=%s top_p=%s max_tokens=%s",
            payload.get("model"),
            len(messages),
            payload.get("temperature"),
            payload.get("top_p"),
            payload.get("max_tokens"),
        )
        t0 = time.time()
        try:
            with httpx.Client(timeout=60.0) as client:
                resp = client.post(url, json=payload, headers=self._headers())
                resp.raise_for_status()
                data = resp.json()
        except Exception:
            logger.exception("[llm.chat_completion] request_failed model=%s", payload.get("model"))
            raise
        finally:
            elapsed_ms = int((time.time() - t0) * 1000)
            logger.info("[llm.chat_completion] elapsed_ms=%s", elapsed_ms)

        try:
            choices = (data.get("choices") or [])
            msg = (choices[0].get("message") or {}) if choices else {}
            content = msg.get("content") or ""
            usage = data.get("usage") or {}
            logger.info(
                "[llm.chat_completion] status=%s out_len=%s prompt_tokens=%s completion_tokens=%s",
                resp.status_code,
                len(content),
                usage.get("prompt_tokens"),
                usage.get("completion_tokens"),
            )
            if content:
                logger.info("[llm.chat_completion] output_preview=%r", content[:200])
        except Exception:
            # best-effort logging; do not fail
            logger.debug("[llm.chat_completion] post_log_parse_failed")
        return data

    def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        *,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        """Streaming chat completion. Yields raw SSE lines (bytes/str)."""
        url = f"{self.base_url}/chat/completions"
        payload: Dict = {
            "model": model or settings.LLM_DEFAULT_MODEL,
            "messages": messages,
            "stream": True,
        }
        if temperature is not None:
            payload["temperature"] = temperature
        if top_p is not None:
            payload["top_p"] = top_p
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        logger.info("[llm.chat_completion_stream] starting stream model=%s", payload.get("model"))
        with httpx.Client(timeout=None) as client:
            with client.stream("POST", url, json=payload, headers=self._headers()) as r:
                r.raise_for_status()
                logger.info("[llm.chat_completion_stream] stream connected status=%s", r.status_code)
                line_count = 0
                for line in r.iter_lines():
                    if not line:
                        continue
                    line_count += 1
                    if line_count <= 5 or line_count % 10 == 0:  # 记录前5行和每10行
                        logger.info("[llm.chat_completion_stream] line_%s: %r", line_count, line[:100])
                    yield line
                logger.info("[llm.chat_completion_stream] stream ended total_lines=%s", line_count)


llm_client = LLMClient()

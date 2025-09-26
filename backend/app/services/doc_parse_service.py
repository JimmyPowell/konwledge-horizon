from __future__ import annotations

import os
from typing import Optional

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader


def _load_pdf(path: str) -> str:
    docs = PyPDFLoader(path).load()
    return "\n".join(d.page_content or "" for d in docs)


def _load_docx(path: str) -> str:
    docs = Docx2txtLoader(path).load()
    return "\n".join(d.page_content or "" for d in docs)


def _load_text(path: str) -> str:
    # LangChain TextLoader handles encoding detection; fallback to utf-8
    docs = TextLoader(path, autodetect_encoding=True).load()
    return "\n".join(d.page_content or "" for d in docs)


def parse_file(path: str, *, mime: Optional[str] = None, ext: Optional[str] = None, strategy: str = "auto") -> str:
    """Parse a file to plain text using lightweight loaders.

    strategy is reserved for future use; for now we auto-route by extension.
    """
    if ext is None:
        ext = os.path.splitext(path)[1].lstrip(".").lower()

    if ext == "pdf":
        return _load_pdf(path)
    if ext in ("docx",):
        return _load_docx(path)
    if ext in ("txt", "md"):
        return _load_text(path)

    raise ValueError(f"Unsupported file extension: .{ext}")


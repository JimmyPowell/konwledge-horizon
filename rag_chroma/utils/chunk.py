from __future__ import annotations

import hashlib
from typing import List, Tuple

from langchain_text_splitters import RecursiveCharacterTextSplitter


def compute_checksum(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def split_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
    separators: List[str] | None = None,
) -> List[str]:
    if separators is None:
        separators = ["\n\n", "\n", "。", "！", "？", ".", "!", "?", " "]
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators,
    )
    return splitter.split_text(text)


def build_ids(source: str, chunks: List[str]) -> List[str]:
    ids: List[str] = []
    base = hashlib.md5(source.encode("utf-8", errors="ignore")).hexdigest()[:12]
    for i, c in enumerate(chunks):
        ids.append(f"{base}-{i}")
    return ids


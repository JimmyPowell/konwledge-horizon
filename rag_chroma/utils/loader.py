from __future__ import annotations

from pathlib import Path
from typing import Tuple

from pypdf import PdfReader


def load_file(path: str | Path) -> Tuple[str, dict]:
    """
    Load text content from supported files.
    Supports: .pdf, .txt (and .md as plain text).

    Returns (text, metadata)
    metadata includes: source (str), file_ext (str)
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    ext = p.suffix.lower()

    if ext == ".pdf":
        reader = PdfReader(str(p))
        texts = []
        for page in reader.pages:
            t = page.extract_text() or ""
            texts.append(t)
        content = "\n".join(texts)
    elif ext in {".txt", ".md"}:
        content = p.read_text(encoding="utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: {ext}. Use PDF/TXT/MD.")

    metadata = {
        "source": str(p),
        "file_ext": ext,
    }
    return content, metadata


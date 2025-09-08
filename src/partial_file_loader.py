from __future__ import annotations

from typing import Iterable, List, Dict


EXCLUDE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg",
    ".pdf", ".zip", ".tar", ".gz", ".7z", ".rar",
    ".so", ".dll", ".dylib", ".bin",
}

TEST_SUFFIXES = ("_test.py", ".spec.ts", ".test.ts", ".test.js")


def should_skip(path: str) -> bool:
    lower = path.lower()
    if any(lower.endswith(ext) for ext in EXCLUDE_EXTENSIONS):
        return True
    if any(lower.endswith(sfx) for sfx in TEST_SUFFIXES):
        return True
    if "/tests/" in lower or lower.startswith("tests/"):
        return True
    return False


def chunk_text(text: str, max_tokens: int = 1000, token_chars: int = 4) -> List[str]:
    # Approximate token length by characters; default ~4 chars per token
    max_chars = max_tokens * token_chars
    if len(text) <= max_chars:
        return [text]
    paragraphs = text.split("\n\n")
    chunks: List[str] = []
    current: List[str] = []
    current_len = 0
    for para in paragraphs:
        para_len = len(para) + 2  # account for the two newlines we will re-insert
        if current_len + para_len > max_chars and current:
            chunks.append("\n\n".join(current))
            current = [para]
            current_len = para_len
        else:
            current.append(para)
            current_len += para_len
    if current:
        chunks.append("\n\n".join(current))
    # If still too large (very long contiguous text), hard-split by chars
    final: List[str] = []
    for c in chunks:
        if len(c) <= max_chars:
            final.append(c)
        else:
            for i in range(0, len(c), max_chars):
                final.append(c[i : i + max_chars])
    return final


def prepare_documents(files: Iterable[Dict[str, str]], max_tokens: int = 1000) -> List[Dict[str, str]]:
    docs: List[Dict[str, str]] = []
    for f in files:
        path = f.get("path", "")
        if should_skip(path):
            continue
        content = f.get("content", "")
        for idx, chunk in enumerate(chunk_text(content, max_tokens=max_tokens)):
            docs.append({"path": path, "chunk_id": str(idx), "text": chunk})
    return docs


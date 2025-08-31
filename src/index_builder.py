from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Tuple

import faiss

from .config import settings
from .utils import setup_logger
from .vectorizer import embed_texts


logger = setup_logger(__name__, settings.log_level)


class FaissIndex:
    def __init__(self, index_path: str) -> None:
        self.index_path = Path(index_path)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.id_to_meta: List[Dict[str, str]] = []
        self._index: faiss.IndexFlatIP | None = None
        self._meta_path = self.index_path.with_suffix(".meta.json")

    def _load_or_create(self, dim: int) -> faiss.IndexFlatIP:
        if self.index_path.exists():
            logger.info("Loading FAISS index from %s", self.index_path)
            return faiss.read_index(str(self.index_path))  # type: ignore[return-value]
        logger.info("Creating new FAISS index with dim=%d", dim)
        return faiss.IndexFlatIP(dim)

    def build(self, docs: List[Dict[str, str]]) -> None:
        texts = [d["text"] for d in docs]
        vectors = embed_texts(texts)
        if not vectors:
            logger.warning("No vectors to index")
            return
        dim = len(vectors[0])
        index = self._load_or_create(dim)
        import numpy as np

        mat = np.array(vectors, dtype="float32")
        faiss.normalize_L2(mat)
        index.add(mat)
        import json
        self.id_to_meta = [
            {"path": d["path"], "chunk_id": d["chunk_id"], "text": d["text"]}
            for d in docs
        ]
        faiss.write_index(index, str(self.index_path))
        with self._meta_path.open("w", encoding="utf-8") as f:
            json.dump(self.id_to_meta, f, ensure_ascii=False)
        self._index = index
        logger.info("Indexed %d vectors", len(vectors))

    def search(self, query: str, k: int = 5) -> List[Tuple[int, float]]:
        if self._index is None:
            if self.index_path.exists():
                self._index = faiss.read_index(str(self.index_path))
            else:
                raise RuntimeError("Index not built")
        from .vectorizer import embed_texts
        import numpy as np

        vec = embed_texts([query])[0]
        mat = np.array([vec], dtype="float32")
        faiss.normalize_L2(mat)
        scores, idxs = self._index.search(mat, k)
        result: List[Tuple[int, float]] = []
        for i, score in zip(idxs[0], scores[0]):
            if i == -1:
                continue
            result.append((int(i), float(score)))
        return result

    def get_chunk_text(self, chunk_id: int) -> str:
        import json
        if not self._meta_path.exists():
            return ""
        try:
            with self._meta_path.open("r", encoding="utf-8") as f:
                meta = json.load(f)
            if 0 <= chunk_id < len(meta):
                return meta[chunk_id].get("text", "")
        except Exception:
            return ""
        return ""


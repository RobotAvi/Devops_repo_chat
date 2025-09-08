from __future__ import annotations

from typing import Dict, List

from .config import settings
from .gitlab_api_handler import GitLabAPI
from .structure_parser import parse_tree
from .index_builder import FaissIndex
from .langchain_chain import generate_answer
from .utils import setup_logger


logger = setup_logger(__name__, settings.log_level)


def _collect_context_from_index(project_id: str, question: str, k: int = 6) -> List[str]:
    index_path = f"{settings.index_dir}/{project_id.replace('/', '_')}.faiss"
    idx = FaissIndex(index_path)
    hits = idx.search(question, k=k)
    chunks: List[str] = []
    for i, score in hits:
        text = idx.get_chunk_text(i)
        if text:
            chunks.append(text)
    return chunks


def answer_question(project_id: str, question: str, ref: str = "HEAD") -> Dict[str, str]:
    api = GitLabAPI()
    tree = api.get_repository_tree(project_id, ref=ref)
    parsed = parse_tree(tree)

    # Heuristic quick hits from structure
    structure_hits: List[str] = []
    if "readme" in question.lower():
        structure_hits.extend(parsed.get("key_files", []))
    if "конфигурац" in question.lower() or "config" in question.lower():
        structure_hits.extend(parsed.get("configs", []))

    # Vector index search
    index_context = []
    try:
        index_context = _collect_context_from_index(project_id, question)
    except Exception as e:
        logger.warning("Index search failed: %s", e)

    context_chunks = [*(f"STRUCT: {p}" for p in structure_hits[:10]), *index_context]
    answer = generate_answer(question, context_chunks)
    return {"answer": answer}


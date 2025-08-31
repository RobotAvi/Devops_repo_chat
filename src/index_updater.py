from __future__ import annotations

from typing import Dict, List

from .gitlab_api_handler import GitLabAPI
from .structure_parser import parse_tree
from .partial_file_loader import prepare_documents
from .index_builder import FaissIndex
from .utils import setup_logger
from .config import settings


logger = setup_logger(__name__, settings.log_level)


def rebuild_index_for_project(project_id: str, ref: str = "HEAD") -> None:
    api = GitLabAPI()
    tree = api.get_repository_tree(project_id, ref=ref)
    parsed = parse_tree(tree)
    key_paths = set(parsed["key_files"]) | set(parsed["configs"]) | set(parsed["modules"])  # prioritize

    files: List[Dict[str, str]] = []
    for p in key_paths:
        try:
            content = api.get_file_raw(project_id, p, ref=ref)
        except Exception as e:
            logger.warning("Failed to fetch %s: %s", p, e)
            continue
        files.append({"path": p, "content": content})

    docs = prepare_documents(files)
    index_path = f"{settings.index_dir}/{project_id.replace('/', '_')}.faiss"
    FaissIndex(index_path).build(docs)


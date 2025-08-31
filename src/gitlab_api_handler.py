from __future__ import annotations

import base64
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import httpx

from .config import settings
from .utils import TTLFileCache, retryable, setup_logger


logger = setup_logger(__name__, settings.log_level)
cache = TTLFileCache(settings.cache_dir, settings.cache_ttl_seconds)


def _cache_key(prefix: str, *parts: str) -> str:
    return ":".join([prefix, *parts])


class GitLabAPI:
    def __init__(self, base_url: str | None = None, token: str | None = None, timeout: float = 15.0) -> None:
        self.base_url = (base_url or settings.gitlab_base_url).rstrip("/")
        self.token = token or settings.gitlab_token
        self.timeout = timeout
        self._client = httpx.Client(timeout=self.timeout, headers=self._headers())

    def _headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["PRIVATE-TOKEN"] = self.token
        return headers

    @retryable()
    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> httpx.Response:
        url = f"{self.base_url}{path}"
        logger.debug("GET %s params=%s", url, params)
        resp = self._client.get(url, params=params)
        resp.raise_for_status()
        return resp

    def get_repository_tree(self, project_id: str, ref: str = "HEAD") -> List[Dict[str, Any]]:
        key = _cache_key("repo_tree", project_id, ref)
        cached = cache.get(key)
        if cached is not None:
            return cached
        items: List[Dict[str, Any]] = []
        page = 1
        per_page = 100
        while True:
            resp = self._get(
                f"/projects/{quote(project_id, safe='')}/repository/tree",
                params={"ref": ref, "per_page": per_page, "page": page, "recursive": True},
            )
            chunk = resp.json()
            if not chunk:
                break
            items.extend(chunk)
            if len(chunk) < per_page:
                break
            page += 1
        cache.set(key, items)
        return items

    def get_file_raw(self, project_id: str, file_path: str, ref: str = "HEAD") -> str:
        key = _cache_key("file_raw", project_id, ref, file_path)
        cached = cache.get(key)
        if cached is not None:
            return cached
        resp = self._get(
            f"/projects/{quote(project_id, safe='')}/repository/files/{quote(file_path, safe='')}",
            params={"ref": ref},
        )
        data = resp.json()
        content_b64 = data.get("content", "")
        encoding = data.get("encoding", "base64")
        if encoding != "base64":
            logger.warning("Unexpected encoding %s for file %s", encoding, file_path)
        try:
            content = base64.b64decode(content_b64).decode("utf-8", errors="replace")
        except Exception as e:
            logger.error("Failed to decode content for %s: %s", file_path, e)
            content = ""
        cache.set(key, content)
        return content


from __future__ import annotations

from typing import Set

from .config import settings
from .utils import setup_logger


logger = setup_logger(__name__, settings.log_level)


def _parse_csv(value: str) -> Set[str]:
    return {v.strip() for v in value.split(",") if v.strip()} if value else set()


ALLOWED_PROJECTS: Set[str] = _parse_csv(settings.allowed_projects)
ADMIN_TOKENS: Set[str] = _parse_csv(settings.admin_tokens)


def is_admin(token: str | None) -> bool:
    if not token:
        return False
    allowed = token in ADMIN_TOKENS
    if not allowed:
        logger.warning("Admin token rejected")
    return allowed


def can_access_project(project: str, token: str | None) -> bool:
    # If there is no allowlist configured, allow all by default.
    if not ALLOWED_PROJECTS:
        return True
    allowed = project in ALLOWED_PROJECTS or is_admin(token)
    if not allowed:
        logger.warning("Access denied to project=%s", project)
    return allowed


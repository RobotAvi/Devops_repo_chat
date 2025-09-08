import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Callable, Optional

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        logger.setLevel(level)
        return logger
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


class TTLFileCache:
    def __init__(self, base_dir: str, default_ttl_seconds: int = 86400) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl_seconds = default_ttl_seconds

    def _key_to_path(self, key: str) -> Path:
        hashed = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.base_dir / f"{hashed}.json"

    def get(self, key: str) -> Optional[Any]:
        path = self._key_to_path(key)
        if not path.exists():
            return None
        try:
            with path.open("r", encoding="utf-8") as f:
                payload = json.load(f)
            expires_at = payload.get("expires_at", 0)
            if time.time() > expires_at:
                # expired
                try:
                    path.unlink(missing_ok=True)
                except Exception:
                    pass
                return None
            return payload.get("value")
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl_seconds
        path = self._key_to_path(key)
        payload = {"value": value, "expires_at": time.time() + ttl}
        tmp_path = path.with_suffix(".tmp")
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f)
        os.replace(tmp_path, path)


def json_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True)


def retryable(
    exceptions: tuple[type[BaseException], ...] = (Exception,),
    attempts: int = 3,
    min_wait: float = 0.5,
    max_wait: float = 4.0,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    return retry(
        reraise=True,
        stop=stop_after_attempt(attempts),
        wait=wait_exponential(multiplier=min_wait, max=max_wait),
        retry=retry_if_exception_type(exceptions),
    )


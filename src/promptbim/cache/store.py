"""Local file-based cache store for generation results."""

from __future__ import annotations

import fcntl
import json
import time
from pathlib import Path

from promptbim.constants import CACHE_MAX_ENTRIES, CACHE_TTL_DAYS
from promptbim.debug import get_logger

logger = get_logger("cache.store")


class CacheStore:
    """File-based cache store using ~/.promptbim/cache/."""

    def __init__(self, cache_dir: Path | None = None) -> None:
        if cache_dir is None:
            cache_dir = Path.home() / ".promptbim" / "cache"
        self._cache_dir = cache_dir
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, key: str) -> dict | None:
        """Get a cached entry by key. Returns None if not found or expired."""
        path = self._key_path(key)
        if not path.exists():
            return None

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            logger.warning("Corrupt cache entry: %s", key[:12])
            path.unlink(missing_ok=True)
            return None

        # Check TTL
        created = data.get("_cache_created", 0)
        ttl_seconds = CACHE_TTL_DAYS * 86400
        if time.time() - created > ttl_seconds:
            logger.debug("Cache entry expired: %s", key[:12])
            path.unlink(missing_ok=True)
            return None

        # Check version
        from promptbim import __version__

        if data.get("_cache_version") != __version__:
            logger.debug("Cache version mismatch: %s", key[:12])
            path.unlink(missing_ok=True)
            return None

        logger.debug("Cache hit: %s", key[:12])
        return data.get("_cache_payload")

    def put(self, key: str, payload: dict) -> None:
        """Store a payload in the cache (file-locked to prevent race conditions)."""
        from promptbim import __version__

        self._evict_if_needed()

        data = {
            "_cache_key": key,
            "_cache_created": time.time(),
            "_cache_version": __version__,
            "_cache_payload": payload,
        }
        path = self._key_path(key)
        content = json.dumps(data, ensure_ascii=False, default=str)
        # Use exclusive file lock to prevent concurrent write corruption
        with open(path, "w", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                f.write(content)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
        logger.debug("Cached: %s", key[:12])

    def invalidate(self, key: str) -> bool:
        """Remove a specific cache entry. Returns True if it existed."""
        path = self._key_path(key)
        if path.exists():
            path.unlink()
            return True
        return False

    def clear_all(self) -> int:
        """Remove all cache entries. Returns count of entries removed."""
        count = 0
        for f in self._cache_dir.glob("*.json"):
            f.unlink()
            count += 1
        logger.info("Cleared %d cache entries", count)
        return count

    def list_entries(self) -> list[dict]:
        """List all cache entries with metadata."""
        entries = []
        for f in sorted(self._cache_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                entries.append({
                    "key": data.get("_cache_key", f.stem),
                    "created": data.get("_cache_created", 0),
                    "version": data.get("_cache_version", "?"),
                })
            except (json.JSONDecodeError, OSError):
                pass
        return entries

    def _key_path(self, key: str) -> Path:
        return self._cache_dir / f"{key[:64]}.json"

    def _evict_if_needed(self) -> None:
        """LRU eviction when cache exceeds max entries."""
        files = sorted(self._cache_dir.glob("*.json"), key=lambda p: p.stat().st_mtime)
        while len(files) >= CACHE_MAX_ENTRIES:
            oldest = files.pop(0)
            oldest.unlink()
            logger.debug("Evicted cache entry: %s", oldest.stem[:12])

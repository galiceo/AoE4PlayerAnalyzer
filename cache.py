import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any


APP_NAME = "AoE4PlayerAnalyzer"


def default_cache_path() -> Path:
    explicit = os.environ.get("AOE4_ANALYZER_CACHE_PATH")
    if explicit:
        return Path(explicit)

    base = os.environ.get("LOCALAPPDATA")
    if base:
        root = Path(base)
    else:
        root = Path.home() / ".cache"
    return root / APP_NAME / "cache.sqlite3"


class ApiCache:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_cache_path()
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._init_db()
        except OSError:
            if path is not None or os.environ.get("AOE4_ANALYZER_CACHE_PATH"):
                raise
            self.path = Path.cwd() / ".aoe4_cache" / "cache.sqlite3"
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS api_cache (
                    cache_key TEXT PRIMARY KEY,
                    response_json TEXT NOT NULL,
                    created_at INTEGER NOT NULL
                )
                """
            )
            conn.commit()

    def get(self, cache_key: str, ttl_seconds: int) -> Any | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT response_json, created_at FROM api_cache WHERE cache_key = ?",
                (cache_key,),
            ).fetchone()

        if row is None:
            return None

        response_json, created_at = row
        if int(time.time()) - int(created_at) > ttl_seconds:
            return None

        return json.loads(response_json)

    def set(self, cache_key: str, value: Any) -> None:
        payload = json.dumps(value, ensure_ascii=False)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO api_cache (cache_key, response_json, created_at)
                VALUES (?, ?, ?)
                ON CONFLICT(cache_key) DO UPDATE SET
                    response_json = excluded.response_json,
                    created_at = excluded.created_at
                """,
                (cache_key, payload, int(time.time())),
            )
            conn.commit()

    def clear(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM api_cache")
            conn.commit()

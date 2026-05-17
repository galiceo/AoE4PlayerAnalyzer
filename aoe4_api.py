import os
from typing import Any
from urllib.parse import urlencode

import requests

from cache import ApiCache


BASE_URL = "https://aoe4world.com/api/v0"
DEFAULT_USER_AGENT = "AoE4PlayerAnalyzer/0.1 contact: github.com/galiceo/AOE4-Performance-Analysis"


class Aoe4ApiError(RuntimeError):
    pass


class Aoe4WorldClient:
    def __init__(self, cache: ApiCache | None = None) -> None:
        self.cache = cache or ApiCache()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": os.environ.get(
                    "AOE4_ANALYZER_USER_AGENT",
                    DEFAULT_USER_AGENT,
                ),
            }
        )

    def _get_json(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        ttl_seconds: int = 300,
    ) -> dict[str, Any]:
        params = {k: v for k, v in (params or {}).items() if v is not None}
        query = urlencode(sorted(params.items()))
        cache_key = f"GET:{path}?{query}"

        cached = self.cache.get(cache_key, ttl_seconds)
        if cached is not None:
            return cached

        url = f"{BASE_URL}{path}"
        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise Aoe4ApiError(f"AOE4 World API request failed: {exc}") from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise Aoe4ApiError("AOE4 World API returned non-JSON data.") from exc

        self.cache.set(cache_key, data)
        return data

    def search_players(
        self,
        query: str,
        page: int = 1,
        exact: bool | None = None,
    ) -> dict[str, Any]:
        query = query.strip()
        if not query:
            raise ValueError("Player name cannot be empty.")

        if exact is None:
            exact = len(query) < 3

        params: dict[str, Any] = {"query": query, "page": page}
        if exact:
            params["exact"] = "true"

        return self._get_json(
            "/players/search",
            params,
            ttl_seconds=600,
        )

    def autocomplete_players(
        self,
        query: str,
        leaderboard: str = "rm_solo",
        limit: int = 8,
    ) -> dict[str, Any]:
        query = query.strip()
        if len(query) < 3:
            raise ValueError("Player name must be at least 3 characters.")

        limit = max(1, min(int(limit), 20))
        return self._get_json(
            "/players/autocomplete",
            {"query": query, "leaderboard": leaderboard, "limit": limit},
            ttl_seconds=300,
        )

    def get_player_profile(self, profile_id: int) -> dict[str, Any]:
        return self._get_json(
            f"/players/{profile_id}",
            ttl_seconds=1800,
        )

    def get_player_games(
        self,
        profile_id: int,
        leaderboard: str = "rm_solo",
        limit: int = 50,
    ) -> dict[str, Any]:
        limit = max(1, min(int(limit), 100))
        return self._get_json(
            f"/players/{profile_id}/games",
            {"leaderboard": leaderboard, "limit": limit},
            ttl_seconds=600,
        )

    def get_leaderboard_entry(
        self,
        profile_id: int,
        leaderboard: str = "rm_solo",
    ) -> dict[str, Any]:
        return self._get_json(
            f"/leaderboards/{leaderboard}",
            {"profile_id": profile_id},
            ttl_seconds=600,
        )

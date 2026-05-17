import unittest
from typing import Any

from aoe4_api import Aoe4WorldClient


class RecordingClient(Aoe4WorldClient):
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any] | None, int]] = []

    def _get_json(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        ttl_seconds: int = 300,
    ) -> dict[str, Any]:
        self.calls.append((path, params, ttl_seconds))
        return {"players": []}


class Aoe4WorldClientTests(unittest.TestCase):
    def test_short_player_search_uses_exact_mode(self):
        client = RecordingClient()

        client.search_players("ML")

        self.assertEqual(
            client.calls,
            [
                (
                    "/players/search",
                    {"query": "ML", "page": 1, "exact": "true"},
                    600,
                )
            ],
        )

    def test_long_player_search_keeps_fuzzy_mode(self):
        client = RecordingClient()

        client.search_players("Beasty")

        self.assertEqual(
            client.calls,
            [
                (
                    "/players/search",
                    {"query": "Beasty", "page": 1},
                    600,
                )
            ],
        )

    def test_player_search_rejects_empty_query(self):
        client = RecordingClient()

        with self.assertRaises(ValueError):
            client.search_players("  ")

        self.assertEqual(client.calls, [])


if __name__ == "__main__":
    unittest.main()

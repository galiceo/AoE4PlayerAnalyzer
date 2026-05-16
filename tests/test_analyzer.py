import unittest

from analyzer import analyze_player_style, translate_term


class AnalyzerTests(unittest.TestCase):
    def test_analyze_player_style_from_team_games(self):
        games = {
            "games": [
                {
                    "duration": 1200,
                    "map": "Dry Arabia",
                    "teams": [
                        [{"player": {"profile_id": 1, "result": "win", "civilization": "english"}}],
                        [{"player": {"profile_id": 2, "result": "loss", "civilization": "french"}}],
                    ],
                },
                {
                    "duration": 1500,
                    "map": "Dry Arabia",
                    "teams": [
                        [{"player": {"profile_id": 1, "result": "loss", "civilization": "english"}}],
                        [{"player": {"profile_id": 3, "result": "win", "civilization": "mongols"}}],
                    ],
                },
            ]
        }

        result = analyze_player_style(1, games)

        self.assertEqual(result["recent_games"], 2)
        self.assertEqual(result["recent_win_rate"], 50.0)
        self.assertEqual(result["avg_duration"], 22.5)
        self.assertEqual(result["main_civs"][0]["civ"], "英格兰")
        self.assertIn("文明专精型", result["tags"])
        self.assertIn("style_profile", result)

    def test_translates_jin_dynasty(self):
        self.assertEqual(translate_term("jin_dynasty", "civilizations"), "金朝")

    def test_filters_games_by_selected_leaderboard(self):
        games = {
            "games": [
                {
                    "leaderboard": "rm_solo",
                    "duration": 1200,
                    "map": "Dry Arabia",
                    "teams": [
                        [{"player": {"profile_id": 1, "result": "win", "civilization": "english"}}],
                        [{"player": {"profile_id": 2, "result": "loss", "civilization": "french"}}],
                    ],
                },
                {
                    "leaderboard": "rm_team",
                    "duration": 1800,
                    "map": "Gorge",
                    "teams": [
                        [
                            {"player": {"profile_id": 1, "result": "loss", "civilization": "jin_dynasty"}},
                            {"player": {"profile_id": 3, "result": "loss", "civilization": "ottomans"}},
                        ],
                        [
                            {"player": {"profile_id": 4, "result": "win", "civilization": "english"}},
                            {"player": {"profile_id": 5, "result": "win", "civilization": "french"}},
                        ],
                    ],
                },
            ]
        }

        solo = analyze_player_style(1, games, leaderboard="rm_solo")
        team = analyze_player_style(1, games, leaderboard="rm_team")

        self.assertEqual(solo["recent_games"], 1)
        self.assertEqual(solo["recent_win_rate"], 100.0)
        self.assertEqual(solo["filtered_out_games"], 1)
        self.assertEqual(team["recent_games"], 1)
        self.assertEqual(team["recent_win_rate"], 0.0)
        self.assertEqual(team["filtered_out_games"], 1)

    def test_excludes_games_under_three_minutes_from_analysis(self):
        games = {
            "games": [
                {
                    "duration": 120,
                    "map": "Dry Arabia",
                    "teams": [
                        [{"player": {"profile_id": 1, "result": "loss", "civilization": "english"}}],
                        [{"player": {"profile_id": 2, "result": "win", "civilization": "french"}}],
                    ],
                },
                {
                    "duration": 600,
                    "map": "Gorge",
                    "teams": [
                        [{"player": {"profile_id": 1, "result": "win", "civilization": "jin_dynasty"}}],
                        [{"player": {"profile_id": 3, "result": "loss", "civilization": "ottomans"}}],
                    ],
                },
            ]
        }

        result = analyze_player_style(1, games)

        self.assertEqual(result["source_games"], 2)
        self.assertEqual(result["excluded_short_games"], 1)
        self.assertEqual(result["recent_games"], 1)
        self.assertEqual(result["recent_win_rate"], 100.0)
        self.assertEqual(result["main_civs"][0]["civ"], "金朝")
        self.assertEqual(result["behavior_risk"]["short_loss_count"], 1)

    def test_detects_fixed_partner_serious_game_pattern(self):
        games = {"games": []}
        for index in range(5):
            games["games"].append(
                {
                    "leaderboard": "rm_team",
                    "duration": 1500,
                    "map": "Gorge",
                    "teams": [
                        [
                            {"player": {"profile_id": 1, "name": "Target", "result": "win", "civilization": "jin_dynasty"}},
                            {"player": {"profile_id": 10, "name": "Boom", "result": "win", "civilization": "english"}},
                        ],
                        [
                            {"player": {"profile_id": 20 + index, "name": f"Opponent {index}", "result": "loss", "civilization": "french"}},
                            {"player": {"profile_id": 30 + index, "name": f"Opponent B {index}", "result": "loss", "civilization": "ottomans"}},
                        ],
                    ],
                }
            )
        for index in range(5):
            games["games"].append(
                {
                    "leaderboard": "rm_team",
                    "duration": 60,
                    "map": "Dry Arabia",
                    "teams": [
                        [
                            {"player": {"profile_id": 1, "name": "Target", "result": "loss", "civilization": "jin_dynasty"}},
                            {"player": {"profile_id": 11, "name": "Drop Partner", "result": "loss", "civilization": "english"}},
                        ],
                        [
                            {"player": {"profile_id": 40 + index, "name": f"Winner {index}", "result": "win", "civilization": "french"}},
                            {"player": {"profile_id": 50 + index, "name": f"Winner B {index}", "result": "win", "civilization": "ottomans"}},
                        ],
                    ],
                }
            )

        result = analyze_player_style(1, games, leaderboard="rm_team")

        self.assertEqual(result["excluded_short_games"], 5)
        self.assertEqual(result["recent_games"], 5)
        self.assertEqual(result["recent_win_rate"], 100.0)
        self.assertEqual(result["behavior_risk"]["short_loss_count"], 5)
        self.assertIn("疑似炸鱼", result["behavior_risk"]["label"])
        self.assertIn("上分/掉分搭档分化", result["relation_pattern"]["label"])
        self.assertTrue(result["relation_pattern"]["is_fixed_serious_pattern"])
        self.assertEqual(result["relation_pattern"]["rank_up_partners"][0]["name"], "Boom")
        self.assertEqual(result["relation_pattern"]["rank_down_partners"][0]["name"], "Drop Partner")
        self.assertIn("上分/掉分搭档分化", result["tags"])

    def test_requires_at_least_five_games_to_classify_partner(self):
        games = {"games": []}
        for index in range(4):
            games["games"].append(
                {
                    "leaderboard": "rm_team",
                    "duration": 1500,
                    "map": "Gorge",
                    "teams": [
                        [
                            {"player": {"profile_id": 1, "name": "Target", "result": "win", "civilization": "jin_dynasty"}},
                            {"player": {"profile_id": 10, "name": "Boom", "result": "win", "civilization": "english"}},
                        ],
                        [
                            {"player": {"profile_id": 20 + index, "name": f"Opponent {index}", "result": "loss", "civilization": "french"}},
                            {"player": {"profile_id": 30 + index, "name": f"Opponent B {index}", "result": "loss", "civilization": "ottomans"}},
                        ],
                    ],
                }
            )
        for index in range(4):
            games["games"].append(
                {
                    "leaderboard": "rm_team",
                    "duration": 60,
                    "map": "Dry Arabia",
                    "teams": [
                        [
                            {"player": {"profile_id": 1, "name": "Target", "result": "loss", "civilization": "jin_dynasty"}},
                            {"player": {"profile_id": 11, "name": "Drop Partner", "result": "loss", "civilization": "english"}},
                        ],
                        [
                            {"player": {"profile_id": 40 + index, "name": f"Winner {index}", "result": "win", "civilization": "french"}},
                            {"player": {"profile_id": 50 + index, "name": f"Winner B {index}", "result": "win", "civilization": "ottomans"}},
                        ],
                    ],
                }
            )

        result = analyze_player_style(1, games, leaderboard="rm_team")

        self.assertEqual(result["relation_pattern"]["rank_up_partners"], [])
        self.assertEqual(result["relation_pattern"]["rank_down_partners"], [])
        self.assertFalse(result["relation_pattern"]["is_fixed_serious_pattern"])
        self.assertNotIn("上分/掉分搭档分化", result["tags"])

    def test_flags_repeated_very_short_losses(self):
        games = {"games": []}
        for index in range(4):
            games["games"].append(
                {
                    "game_id": 1000 + index,
                    "duration": 240,
                    "map": "Dry Arabia",
                    "teams": [
                        [{"player": {"profile_id": 1, "result": "loss", "civilization": "jin_dynasty"}}],
                        [{"player": {"profile_id": 2, "result": "win", "civilization": "english"}}],
                    ],
                }
            )
        games["games"].append(
            {
                "game_id": 2000,
                "duration": 1800,
                "map": "Gorge",
                "teams": [
                    [{"player": {"profile_id": 1, "result": "win", "civilization": "jin_dynasty"}}],
                    [{"player": {"profile_id": 3, "result": "loss", "civilization": "french"}}],
                ],
            }
        )

        result = analyze_player_style(1, games)

        self.assertEqual(result["behavior_risk"]["short_loss_count"], 4)
        self.assertEqual(result["effective_games"], 1)
        self.assertEqual(result["effective_win_rate"], 100.0)
        self.assertEqual(result["account_profile"]["effective_games"], 1)
        self.assertEqual(result["account_profile"]["effective_win_rate"], 100.0)
        self.assertIn("疑似炸鱼风险", result["behavior_risk"]["label"])
        self.assertIn("疑似炸鱼", result["tags"])

    def test_flags_high_winrate_low_games_as_possible_smurf(self):
        games = {"games": []}
        for index in range(10):
            games["games"].append(
                {
                    "game_id": 3000 + index,
                    "duration": 1500,
                    "map": "Dry Arabia",
                    "teams": [
                        [{"player": {"profile_id": 1, "result": "win", "civilization": "jin_dynasty"}}],
                        [{"player": {"profile_id": 2, "result": "loss", "civilization": "english"}}],
                    ],
                }
            )
        leaderboard = {
            "players": [
                {
                    "rating": 1250,
                    "rank": 1000,
                    "rank_level": "platinum_2",
                    "games_count": 12,
                    "win_rate": 83.3,
                }
            ]
        }

        result = analyze_player_style(1, games, leaderboard)

        self.assertIn("疑似高手小号", result["account_profile"]["label"])
        self.assertIn("疑似高手小号", result["tags"])

    def test_flags_many_average_games_as_local_account(self):
        games = {"games": []}
        for index in range(20):
            result = "win" if index % 2 == 0 else "loss"
            opponent_result = "loss" if result == "win" else "win"
            games["games"].append(
                {
                    "game_id": 4000 + index,
                    "duration": 1800,
                    "map": "Gorge",
                    "teams": [
                        [{"player": {"profile_id": 1, "result": result, "civilization": "jin_dynasty"}}],
                        [{"player": {"profile_id": 2, "result": opponent_result, "civilization": "english"}}],
                    ],
                }
            )
        leaderboard = {
            "players": [
                {
                    "rating": 1180,
                    "rank": 3000,
                    "rank_level": "gold_3",
                    "games_count": 240,
                    "win_rate": 52.1,
                }
            ]
        }

        result = analyze_player_style(1, games, leaderboard)

        self.assertEqual(result["account_profile"]["label"], "本地人/正常长期玩家")
        self.assertIn("本地人", result["tags"])


if __name__ == "__main__":
    unittest.main()

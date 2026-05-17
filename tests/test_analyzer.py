import unittest

from analyzer import CIV_STYLE_PROFILES, TRANSLATIONS, analyze_player_style, english_term, translate_term


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

    def test_translates_all_aoe4_civilizations_from_reference_table(self):
        expected = {
            "chinese": ("Chinese", "中国"),
            "abbasid_dynasty": ("Abbasid Dynasty", "黑衣大食王朝"),
            "delhi_sultanate": ("Delhi Sultanate", "德里苏丹国"),
            "mongols": ("Mongols", "蒙古"),
            "french": ("French", "法兰西"),
            "holy_roman_empire": ("Holy Roman Empire", "神圣罗马帝国"),
            "english": ("English", "英格兰"),
            "rus": ("Rus", "罗斯"),
            "japanese": ("Japanese", "日本"),
            "byzantines": ("Byzantines", "拜占庭"),
            "ottomans": ("Ottomans", "奥斯曼"),
            "malians": ("Malians", "马里"),
            "vikings": ("Vikings", "维京"),
            "knights_templar": ("Knights Templar", "圣殿骑士团"),
            "jin_dynasty": ("Jin Dynasty", "金朝"),
            "zhu_xis_legacy": ("Zhu Xi's Legacy", "朱子遗训"),
            "ayyubids": ("Ayyubids", "阿尤布"),
            "tughlaq_dynasty": ("Tughlaq Dynasty", "图格鲁克王朝"),
            "golden_horde": ("Golden Horde", "金帐汗国"),
            "jeanne_darc": ("Jeanne d'Arc", "圣女贞德"),
            "order_of_the_dragon": ("Order of the Dragon", "龙之骑士团"),
            "house_of_lancaster": ("House of Lancaster", "兰开斯特王朝"),
            "sengoku_daimyo": ("Sengoku Daimyo", "战国大名"),
            "macedonian_dynasty": ("Macedonian Dynasty", "马其顿王朝"),
        }

        self.assertEqual(TRANSLATIONS["civilizations"], {key: value[1] for key, value in expected.items()})
        self.assertEqual(
            TRANSLATIONS["civilizations_english"],
            {key: value[0] for key, value in expected.items()},
        )
        self.assertTrue(set(expected).issubset(CIV_STYLE_PROFILES))

    def test_translates_civilization_names_with_apostrophes(self):
        self.assertEqual(translate_term("Zhu Xi's Legacy", "civilizations"), "朱子遗训")
        self.assertEqual(english_term("Jeanne d'Arc", "civilizations"), "Jeanne d'Arc")

    def test_translates_aoe4_maps_from_reference_table(self):
        expected = {
            "altai": ("Altai", "阿尔泰"),
            "ancient_spires": ("Ancient Spires", "古代尖山"),
            "archipelago": ("Archipelago", "群岛"),
            "atacama": ("Atacama", "阿塔卡马"),
            "baltic": ("Baltic", "波罗的海"),
            "black_forest": ("Black Forest", "黑森林"),
            "boulder_bay": ("Boulder Bay", "巨石湾"),
            "canal": ("Canal", "运河"),
            "confluence": ("Confluence", "汇流处"),
            "continental": ("Continental", "大陆"),
            "danube_river": ("Danube River", "多瑙河"),
            "dry_arabia": ("Dry Arabia", "干燥阿拉伯"),
            "forest_ponds": ("Forest Ponds", "森林与池塘"),
            "four_lakes": ("Four Lakes", "四个湖"),
            "french_pass": ("French Pass", "法兰西隘口"),
            "golden_heights": ("Golden Heights", "黄金高地"),
            "gorge": ("Gorge", "峡谷"),
            "hideout": ("Hideout", "藏身处"),
            "highview": ("Highview", "高视野区"),
            "hill_and_dale": ("Hill and Dale", "高山深谷"),
            "king_of_the_hill": ("King of the Hill", "占山为王"),
            "lakeside": ("Lakeside", "湖畔"),
            "lipany": ("Lipany", "利帕尼"),
            "marshland": ("Marshland", "沼泽地"),
            "migration": ("Migration", "迁移"),
            "mongolian_heights": ("Mongolian Heights", "蒙古高原"),
            "mountain_clearing": ("Mountain Clearing", "山中空地"),
            "mountain_pass": ("Mountain Pass", "隘口"),
            "nagari": ("Nagari", "那格利"),
            "oasis": ("Oasis", "绿洲"),
            "prairie": ("Prairie", "草原"),
            "dry_river": ("Dry River", "岩石河"),
            "socotra": ("Socotra", "索科特拉岛"),
            "pit": ("Pit", "深坑"),
            "volcanic_island": ("Volcanic Island", "火山岛"),
            "warring_islands": ("Warring Islands", "敌对岛屿"),
            "waterholes": ("Waterholes", "水洼"),
            "ponds": ("Ponds", "湿地"),
            "carmel": ("Carmel", "卡梅尔"),
            "african_waters": ("African Waters", "非洲海域"),
            "cliff_side": ("Cliff Side", "悬崖边"),
            "forts": ("Forts", "堡垒"),
            "glade": ("Glade", "林间空地"),
            "golden_pits": ("Golden Pits", "黄金之坑"),
            "haywire": ("Haywire", "失控"),
            "hidden_valley": ("Hidden Valley", "隐秘山谷"),
            "himeyama": ("Himeyama", "姬山"),
            "highland": ("Highland", "灌木丛"),
            "turtle_ridge": ("Turtle Ridge", "海龟山脊"),
            "enlightened_horizon": ("Enlightened Horizon", "启蒙眼界"),
            "flankwoods": ("Flankwoods", "弗兰克伍兹森林"),
            "hedgemaze": ("Hedgemaze", "树篱迷宫"),
            "highwoods": ("Highwoods", "茂密树林"),
            "mountain_lakes": ("Mountain Lakes", "山间湖泊"),
            "relic_river": ("Relic River", "遗迹河"),
            "rugged": ("Rugged", "崎岖之地"),
            "shadow_lake": ("Shadow Lake", "影子湖"),
            "sunkenlands": ("Sunkenlands", "沉没之地"),
            "wasteland": ("Wasteland", "荒地"),
            "waterlanes": ("Waterlanes", "水道"),
            "canyon": ("Canyon", "大峡谷"),
            "cliffsanity": ("Cliffsanity", "悬崖疯狂"),
            "craters": ("Craters", "陨石坑"),
            "dungeon": ("Dungeon", "地牢"),
            "michi": ("Michi", "开道"),
            "nomadic_ridges": ("Nomadic Ridges", "游牧山脊"),
            "nomadic_tarns": ("Nomadic Tarns", "游牧湖群"),
            "ocean_gateway": ("Ocean Gateway", "海之门户"),
            "fangs": ("Fangs", "尖牙"),
            "ascension": ("Ascension", "飞升"),
            "snake_river": ("Snake River", "蛇河"),
            "west_lake": ("West Lake", "西湖"),
            "acropolis": ("Acropolis", "卫城"),
            "channel": ("Channel", "海峡"),
            "haunted_gulch": ("Haunted Gulch", "阴森幽谷"),
            "narrows": ("Narrows", "狭窄区域"),
            "peagee": ("Peagee", "佩艾吉"),
            "plains": ("Plains", "平原"),
            "rhinelands": ("Rhinelands", "莱茵兰"),
            "river_kingdom": ("River Kingdom", "河流王国"),
            "rolling_rivers": ("Rolling Rivers", "奔流"),
            "wadden_sea": ("Wadden Sea", "瓦登海"),
        }

        for key, (english, chinese) in expected.items():
            self.assertEqual(english_term(key, "maps"), english)
            self.assertEqual(translate_term(key, "maps"), chinese)

    def test_translates_map_aliases_used_by_api(self):
        self.assertEqual(translate_term("high_view", "maps"), "高视野区")
        self.assertEqual(english_term("rocky_river", "maps"), "Dry River")
        self.assertEqual(translate_term("wetlands", "maps"), "湿地")

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

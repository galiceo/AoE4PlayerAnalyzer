from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any


LEADERBOARD_LABELS = {
    "rm_solo": "天梯单排",
    "rm_team": "天梯组队",
    "qm_1v1": "快速 1v1",
    "qm_2v2": "快速 2v2",
    "qm_3v3": "快速 3v3",
    "qm_4v4": "快速 4v4",
}


TRANSLATIONS = {
    "civilizations": {
        "abbasid_dynasty": "黑衣大食王朝",
        "ayyubids": "阿尤布",
        "byzantines": "拜占庭",
        "chinese": "中国",
        "delhi_sultanate": "德里苏丹国",
        "english": "英格兰",
        "french": "法兰西",
        "golden_horde": "金帐汗国",
        "holy_roman_empire": "神圣罗马帝国",
        "house_of_lancaster": "兰开斯特王朝",
        "japanese": "日本",
        "jeanne_darc": "圣女贞德",
        "jin_dynasty": "金朝",
        "knights_templar": "圣殿骑士团",
        "macedonian_dynasty": "马其顿王朝",
        "malians": "马里",
        "mongols": "蒙古",
        "order_of_the_dragon": "龙之骑士团",
        "ottomans": "奥斯曼",
        "rus": "罗斯",
        "sengoku_daimyo": "战国大名",
        "tughlaq_dynasty": "图格鲁克王朝",
        "vikings": "维京",
        "zhu_xis_legacy": "朱子遗训",
    },
    "civilizations_english": {
        "abbasid_dynasty": "Abbasid Dynasty",
        "ayyubids": "Ayyubids",
        "byzantines": "Byzantines",
        "chinese": "Chinese",
        "delhi_sultanate": "Delhi Sultanate",
        "english": "English",
        "french": "French",
        "golden_horde": "Golden Horde",
        "holy_roman_empire": "Holy Roman Empire",
        "house_of_lancaster": "House of Lancaster",
        "japanese": "Japanese",
        "jeanne_darc": "Jeanne d'Arc",
        "jin_dynasty": "Jin Dynasty",
        "knights_templar": "Knights Templar",
        "macedonian_dynasty": "Macedonian Dynasty",
        "malians": "Malians",
        "mongols": "Mongols",
        "order_of_the_dragon": "Order of the Dragon",
        "ottomans": "Ottomans",
        "rus": "Rus",
        "sengoku_daimyo": "Sengoku Daimyo",
        "tughlaq_dynasty": "Tughlaq Dynasty",
        "vikings": "Vikings",
        "zhu_xis_legacy": "Zhu Xi's Legacy",
    },
    "maps": {
        "altai": "阿尔泰",
        "acropolis": "卫城",
        "african_waters": "非洲海域",
        "ancient_spires": "古代尖山",
        "archipelago": "群岛",
        "ascension": "飞升",
        "atacama": "阿塔卡马",
        "baltic": "波罗的海",
        "black_forest": "黑森林",
        "arabia": "阿拉伯",
        "boulder_bay": "巨石湾",
        "canal": "运河",
        "canyon": "大峡谷",
        "carmel": "卡梅尔",
        "channel": "海峡",
        "cliffsanity": "悬崖疯狂",
        "cliff_side": "悬崖边",
        "cliffside": "悬崖边",
        "confluence": "汇流处",
        "continental": "大陆",
        "craters": "陨石坑",
        "danube_river": "多瑙河",
        "dry_arabia": "干燥阿拉伯",
        "dry_river": "岩石河",
        "dungeon": "地牢",
        "enlightened_horizon": "启蒙眼界",
        "fangs": "尖牙",
        "flankwoods": "弗兰克伍兹森林",
        "forest_ponds": "森林与池塘",
        "forts": "堡垒",
        "four_lakes": "四个湖",
        "french_pass": "法兰西隘口",
        "glade": "林间空地",
        "golden_heights": "黄金高地",
        "golden_pits": "黄金之坑",
        "gorge": "峡谷",
        "haunted_gulch": "阴森幽谷",
        "haywire": "失控",
        "hedgemaze": "树篱迷宫",
        "hideout": "藏身处",
        "hidden_valley": "隐秘山谷",
        "highland": "灌木丛",
        "himeyama": "姬山",
        "highview": "高视野区",
        "high_view": "高视野区",
        "highwoods": "茂密树林",
        "hill_and_dale": "高山深谷",
        "king_of_the_hill": "占山为王",
        "lakeside": "湖畔",
        "lipany": "利帕尼",
        "marshland": "沼泽地",
        "michi": "开道",
        "migration": "迁移",
        "mongolian_heights": "蒙古高原",
        "mountain_clearing": "山中空地",
        "mountain_lakes": "山间湖泊",
        "mountain_pass": "隘口",
        "nagari": "那格利",
        "narrows": "狭窄区域",
        "nomadic_ridges": "游牧山脊",
        "nomadic_tarns": "游牧湖群",
        "oasis": "绿洲",
        "ocean_gateway": "海之门户",
        "peagee": "佩艾吉",
        "pit": "深坑",
        "plains": "平原",
        "ponds": "湿地",
        "prairie": "草原",
        "relic_river": "遗迹河",
        "rhinelands": "莱茵兰",
        "river_kingdom": "河流王国",
        "rocky_river": "岩石河",
        "rolling_rivers": "奔流",
        "rugged": "崎岖之地",
        "shadow_lake": "影子湖",
        "snake_river": "蛇河",
        "socotra": "索科特拉岛",
        "sunkenlands": "沉没之地",
        "turtle_ridge": "海龟山脊",
        "volcanic_island": "火山岛",
        "wadden_sea": "瓦登海",
        "warring_islands": "敌对岛屿",
        "wasteland": "荒地",
        "waterlanes": "水道",
        "waterholes": "水洼",
        "west_lake": "西湖",
        "wetlands": "湿地",
    },
    "maps_english": {
        "altai": "Altai",
        "acropolis": "Acropolis",
        "african_waters": "African Waters",
        "ancient_spires": "Ancient Spires",
        "archipelago": "Archipelago",
        "ascension": "Ascension",
        "atacama": "Atacama",
        "baltic": "Baltic",
        "black_forest": "Black Forest",
        "arabia": "Arabia",
        "boulder_bay": "Boulder Bay",
        "canal": "Canal",
        "canyon": "Canyon",
        "carmel": "Carmel",
        "channel": "Channel",
        "cliffsanity": "Cliffsanity",
        "cliff_side": "Cliff Side",
        "cliffside": "Cliff Side",
        "confluence": "Confluence",
        "continental": "Continental",
        "craters": "Craters",
        "danube_river": "Danube River",
        "dry_arabia": "Dry Arabia",
        "dry_river": "Dry River",
        "dungeon": "Dungeon",
        "enlightened_horizon": "Enlightened Horizon",
        "fangs": "Fangs",
        "flankwoods": "Flankwoods",
        "forest_ponds": "Forest Ponds",
        "forts": "Forts",
        "four_lakes": "Four Lakes",
        "french_pass": "French Pass",
        "glade": "Glade",
        "golden_heights": "Golden Heights",
        "golden_pits": "Golden Pits",
        "gorge": "Gorge",
        "haunted_gulch": "Haunted Gulch",
        "haywire": "Haywire",
        "hedgemaze": "Hedgemaze",
        "hideout": "Hideout",
        "hidden_valley": "Hidden Valley",
        "highland": "Highland",
        "himeyama": "Himeyama",
        "highview": "Highview",
        "high_view": "Highview",
        "highwoods": "Highwoods",
        "hill_and_dale": "Hill and Dale",
        "king_of_the_hill": "King of the Hill",
        "lakeside": "Lakeside",
        "lipany": "Lipany",
        "marshland": "Marshland",
        "michi": "Michi",
        "migration": "Migration",
        "mongolian_heights": "Mongolian Heights",
        "mountain_clearing": "Mountain Clearing",
        "mountain_lakes": "Mountain Lakes",
        "mountain_pass": "Mountain Pass",
        "nagari": "Nagari",
        "narrows": "Narrows",
        "nomadic_ridges": "Nomadic Ridges",
        "nomadic_tarns": "Nomadic Tarns",
        "oasis": "Oasis",
        "ocean_gateway": "Ocean Gateway",
        "peagee": "Peagee",
        "pit": "Pit",
        "plains": "Plains",
        "ponds": "Ponds",
        "prairie": "Prairie",
        "relic_river": "Relic River",
        "rhinelands": "Rhinelands",
        "river_kingdom": "River Kingdom",
        "rocky_river": "Dry River",
        "rolling_rivers": "Rolling Rivers",
        "rugged": "Rugged",
        "shadow_lake": "Shadow Lake",
        "snake_river": "Snake River",
        "socotra": "Socotra",
        "sunkenlands": "Sunkenlands",
        "turtle_ridge": "Turtle Ridge",
        "volcanic_island": "Volcanic Island",
        "wadden_sea": "Wadden Sea",
        "warring_islands": "Warring Islands",
        "wasteland": "Wasteland",
        "waterlanes": "Waterlanes",
        "waterholes": "Waterholes",
        "west_lake": "West Lake",
        "wetlands": "Ponds",
    },
    "rank_levels": {
        "bronze_1": "青铜 I",
        "bronze_2": "青铜 II",
        "bronze_3": "青铜 III",
        "silver_1": "白银 I",
        "silver_2": "白银 II",
        "silver_3": "白银 III",
        "gold_1": "黄金 I",
        "gold_2": "黄金 II",
        "gold_3": "黄金 III",
        "platinum_1": "白金 I",
        "platinum_2": "白金 II",
        "platinum_3": "白金 III",
        "diamond_1": "钻石 I",
        "diamond_2": "钻石 II",
        "diamond_3": "钻石 III",
        "conqueror_1": "征服者 I",
        "conqueror_2": "征服者 II",
        "conqueror_3": "征服者 III",
        "conqueror_4": "征服者 IV",
    },
    "tags": {
        "文明专精型": "Civ specialist",
        "文明池宽": "Wide civ pool",
        "文明池集中": "Focused civ pool",
        "近期状态火热": "Hot streak",
        "近期状态低迷": "Cold streak",
        "近期表现强": "Strong recent form",
        "近期表现弱": "Weak recent form",
        "快节奏": "Fast-paced",
        "运营发育型": "Macro-oriented",
        "节奏均衡": "Balanced tempo",
        "地图熟练度高": "Map comfort pick",
        "机动骚扰倾向": "Cavalry harassment tendency",
        "发育运营倾向": "Economy boom tendency",
        "固定认真局模式": "Fixed-player serious-game pattern",
        "上分/掉分搭档分化": "Rank-up/rank-down partner split",
    },
}


CIV_STYLE_PROFILES = {
    "abbasid_dynasty": {"economy", "castle"},
    "ayyubids": {"economy", "castle", "tempo"},
    "byzantines": {"economy", "castle"},
    "chinese": {"economy", "late"},
    "delhi_sultanate": {"feudal", "tempo"},
    "english": {"feudal", "defensive", "economy"},
    "french": {"cavalry", "feudal", "tempo"},
    "golden_horde": {"cavalry", "feudal", "tempo"},
    "holy_roman_empire": {"economy", "castle"},
    "house_of_lancaster": {"defensive", "economy"},
    "japanese": {"tempo", "castle"},
    "jeanne_darc": {"cavalry", "feudal", "tempo"},
    "jin_dynasty": {"cavalry", "castle", "tempo"},
    "knights_templar": {"cavalry", "feudal", "tempo"},
    "macedonian_dynasty": {"tempo", "castle"},
    "malians": {"cavalry", "feudal", "tempo"},
    "mongols": {"cavalry", "feudal", "tempo"},
    "order_of_the_dragon": {"castle", "tempo"},
    "ottomans": {"economy", "castle", "late"},
    "rus": {"cavalry", "castle", "economy"},
    "sengoku_daimyo": {"tempo", "castle"},
    "tughlaq_dynasty": {"economy", "castle", "tempo"},
    "vikings": {"feudal", "tempo"},
    "zhu_xis_legacy": {"economy", "late"},
}


def normalize_key(value: Any) -> str:
    if value is None:
        return "unknown"
    return (
        str(value)
        .strip()
        .lower()
        .replace("&", "and")
        .replace("'", "")
        .replace("’", "")
        .replace("-", "_")
        .replace(" ", "_")
    )


def display_name(value: Any) -> str:
    if value is None:
        return "Unknown"
    return str(value).replace("_", " ").title()


def translate_term(value: Any, category: str) -> str:
    key = normalize_key(value)
    return TRANSLATIONS.get(category, {}).get(key, display_name(value))


def english_term(value: Any, category: str) -> str:
    key = normalize_key(value)
    return TRANSLATIONS.get(f"{category}_english", {}).get(key, display_name(value))


def bilingual_label(value: Any, category: str) -> str:
    english = english_term(value, category)
    chinese = translate_term(value, category)
    if chinese == english:
        return chinese
    return f"{chinese}（{english}）"


def iter_game_players(game: dict[str, Any]):
    for player in game.get("players", []) or []:
        yield player.get("player", player)

    for team in game.get("teams", []) or []:
        for slot in team or []:
            yield slot.get("player", slot)


def find_target_player(game: dict[str, Any], profile_id: int) -> dict[str, Any] | None:
    for player in iter_game_players(game):
        if str(player.get("profile_id")) == str(profile_id):
            return player
    return None


def extract_games(games_data: Any) -> list[dict[str, Any]]:
    if isinstance(games_data, list):
        return games_data
    if isinstance(games_data, dict):
        games = games_data.get("games", [])
        if isinstance(games, list):
            return games
    return []


def game_duration_minutes(game: dict[str, Any]) -> float | None:
    duration = game.get("duration")
    if isinstance(duration, (int, float)) and duration >= 0:
        return round(duration / 60, 1)
    return None


def team_sizes(game: dict[str, Any]) -> list[int]:
    teams = game.get("teams")
    if isinstance(teams, list) and teams:
        sizes = []
        for team in teams:
            if isinstance(team, list):
                sizes.append(len(team))
            elif isinstance(team, dict):
                players = team.get("players") or team.get("members") or []
                sizes.append(len(players) if isinstance(players, list) else 1)
            else:
                sizes.append(1)
        return sizes

    players = game.get("players")
    if isinstance(players, list) and players:
        return [1 for _ in players]

    return []


def extract_game_mode_values(game: dict[str, Any]) -> set[str]:
    values: set[str] = set()
    keys = (
        "leaderboard",
        "leaderboard_id",
        "leaderboard_name",
        "kind",
        "mode",
        "game_mode",
        "match_type",
        "queue",
        "queue_type",
        "rating_type",
    )

    def add_value(value: Any) -> None:
        if value is None:
            return
        if isinstance(value, dict):
            for nested_key in ("id", "slug", "name", "key", "leaderboard"):
                add_value(value.get(nested_key))
            return
        if isinstance(value, (list, tuple, set)):
            for item in value:
                add_value(item)
            return
        values.add(normalize_key(value))

    for key in keys:
        add_value(game.get(key))

    return {value for value in values if value and value != "unknown"}


def leaderboard_family(leaderboard: str | None) -> str | None:
    key = normalize_key(leaderboard)
    if key in {"rm_solo", "rm_1v1", "solo_ranked", "ranked_solo", "ranked_1v1"}:
        return "ranked_1v1"
    if key in {"rm_team", "team_ranked", "ranked_team"} or key in {"rm_2v2", "rm_3v3", "rm_4v4"}:
        return "ranked_team"
    if key in {"qm_1v1", "quick_match_1v1"}:
        return "quick_1v1"
    if key in {"qm_2v2", "quick_match_2v2"}:
        return "quick_2v2"
    if key in {"qm_3v3", "quick_match_3v3"}:
        return "quick_3v3"
    if key in {"qm_4v4", "quick_match_4v4"}:
        return "quick_4v4"
    return None


def mode_family_from_value(value: str) -> str | None:
    key = normalize_key(value)
    if key in {"rm_solo", "rm_1v1"} or ("ranked" in key and ("solo" in key or "1v1" in key)):
        return "ranked_1v1"
    if key in {"rm_team", "rm_2v2", "rm_3v3", "rm_4v4"} or ("ranked" in key and "team" in key):
        return "ranked_team"
    if key == "qm_1v1" or ("quick" in key and "1v1" in key):
        return "quick_1v1"
    if key == "qm_2v2" or ("quick" in key and "2v2" in key):
        return "quick_2v2"
    if key == "qm_3v3" or ("quick" in key and "3v3" in key):
        return "quick_3v3"
    if key == "qm_4v4" or ("quick" in key and "4v4" in key):
        return "quick_4v4"
    return None


def inferred_family_from_teams(game: dict[str, Any], requested_family: str) -> bool | None:
    sizes = team_sizes(game)
    if not sizes:
        return None

    player_count = sum(sizes)
    max_team_size = max(sizes)

    if requested_family.endswith("1v1"):
        return player_count == 2 and max_team_size == 1

    if requested_family == "ranked_team":
        return player_count >= 4 and max_team_size >= 2

    expected_team_size = {
        "quick_2v2": 2,
        "quick_3v3": 3,
        "quick_4v4": 4,
    }.get(requested_family)
    if expected_team_size is not None:
        return len(sizes) == 2 and all(size == expected_team_size for size in sizes)

    return None


def game_matches_leaderboard(game: dict[str, Any], leaderboard: str | None) -> bool:
    requested_family = leaderboard_family(leaderboard)
    if requested_family is None:
        return True

    mode_values = extract_game_mode_values(game)
    mode_families = {mode_family_from_value(value) for value in mode_values}
    mode_families.discard(None)
    if mode_families:
        if requested_family == "ranked_team" and "ranked_team" in mode_families:
            return True
        return requested_family in mode_families

    inferred_match = inferred_family_from_teams(game, requested_family)
    if inferred_match is not None:
        return inferred_match

    return True


def is_player_win(player: dict[str, Any]) -> bool:
    result = str(player.get("result", "")).lower()
    return result == "win" or player.get("won") is True


def collect_short_loss_games(
    games: list[dict[str, Any]],
    profile_id: int,
    thresholds: "AnalysisThresholds",
) -> list[dict[str, Any]]:
    short_losses: list[dict[str, Any]] = []
    for game in games:
        player = find_target_player(game, profile_id)
        if player is None or is_player_win(player):
            continue

        duration_minutes = game_duration_minutes(game)
        if duration_minutes is None or duration_minutes > thresholds.suspicious_short_loss_minutes:
            continue

        short_losses.append(
            {
                "game_id": game.get("game_id"),
                "duration": duration_minutes,
                "started_at": game.get("started_at"),
                "map": translate_term(game.get("map") or game.get("map_name"), "maps"),
            }
        )
    return short_losses


def split_related_players(game: dict[str, Any], profile_id: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    teams = game.get("teams")
    if not isinstance(teams, list) or not teams:
        return [], []

    team_players: list[list[dict[str, Any]]] = []
    target_team_index: int | None = None
    for index, team in enumerate(teams):
        players: list[dict[str, Any]] = []
        if not isinstance(team, list):
            continue
        for slot in team:
            if not isinstance(slot, dict):
                continue
            player = slot.get("player", slot)
            if not isinstance(player, dict):
                continue
            players.append(player)
            if str(player.get("profile_id")) == str(profile_id):
                target_team_index = index
        team_players.append(players)

    if target_team_index is None:
        return [], []

    teammates: list[dict[str, Any]] = []
    opponents: list[dict[str, Any]] = []
    for index, players in enumerate(team_players):
        for player in players:
            if str(player.get("profile_id")) == str(profile_id):
                continue
            if index == target_team_index:
                teammates.append(player)
            else:
                opponents.append(player)

    return teammates, opponents


def relation_key(player: dict[str, Any]) -> str:
    profile_id = player.get("profile_id")
    if profile_id is not None:
        return str(profile_id)
    return normalize_key(player.get("name"))


def build_fixed_player_pattern(
    games: list[dict[str, Any]],
    profile_id: int,
    thresholds: "AnalysisThresholds",
) -> dict[str, Any]:
    if not games:
        return {}

    partner_stats: dict[str, dict[str, Any]] = {}
    raw_losses = 0
    invalid_short_losses = 0

    for game in games:
        player = find_target_player(game, profile_id)
        if player is None:
            continue

        won = is_player_win(player)
        duration_minutes = game_duration_minutes(game)
        is_invalid_short = (
            duration_minutes is not None
            and duration_minutes < thresholds.min_analyzable_game_minutes
        )
        is_short_loss = (
            not won
            and duration_minutes is not None
            and duration_minutes < thresholds.min_analyzable_game_minutes
        )
        if not won:
            raw_losses += 1
        if is_short_loss:
            invalid_short_losses += 1

        teammates, _opponents = split_related_players(game, profile_id)
        for teammate in teammates:
            key = relation_key(teammate)
            if not key or key == "unknown":
                continue
            stats = partner_stats.setdefault(
                key,
                {
                    "profile_id": teammate.get("profile_id"),
                    "name": teammate.get("name") or "Unknown",
                    "games": 0,
                    "wins": 0,
                    "losses": 0,
                    "analyzable_games": 0,
                    "analyzable_wins": 0,
                    "invalid_short_losses": 0,
                    "durations": [],
                },
            )
            stats["games"] += 1
            if won:
                stats["wins"] += 1
            else:
                stats["losses"] += 1
            if is_short_loss:
                stats["invalid_short_losses"] += 1
            if not is_invalid_short:
                stats["analyzable_games"] += 1
                if won:
                    stats["analyzable_wins"] += 1
                if duration_minutes is not None and duration_minutes > 0:
                    stats["durations"].append(duration_minutes)

    partner_summaries: list[dict[str, Any]] = []
    for stats in partner_stats.values():
        analyzable_games = stats["analyzable_games"]
        games_count = stats["games"]
        avg_duration = (
            round(sum(stats["durations"]) / len(stats["durations"]), 1)
            if stats["durations"]
            else None
        )
        analyzable_win_rate = (
            round(stats["analyzable_wins"] / analyzable_games * 100, 1)
            if analyzable_games
            else None
        )
        short_loss_rate = round(stats["invalid_short_losses"] / games_count * 100, 1) if games_count else 0.0
        partner_summaries.append(
            {
                "profile_id": stats["profile_id"],
                "name": stats["name"],
                "games": games_count,
                "wins": stats["wins"],
                "losses": stats["losses"],
                "analyzable_games": analyzable_games,
                "analyzable_win_rate": analyzable_win_rate,
                "avg_duration": avg_duration,
                "invalid_short_losses": stats["invalid_short_losses"],
                "short_loss_rate": short_loss_rate,
            }
        )

    serious_partners = [
        partner
        for partner in partner_summaries
        if partner["games"] >= thresholds.partner_min_games
        and partner["analyzable_games"] >= thresholds.partner_min_games
        and partner["analyzable_win_rate"] is not None
        and partner["analyzable_win_rate"] >= 70
        and partner["avg_duration"] is not None
        and partner["avg_duration"] >= 15
        and partner["invalid_short_losses"] == 0
    ]
    if not serious_partners:
        serious_partners = [
            partner
            for partner in partner_summaries
            if partner["games"] >= thresholds.partner_min_games
            and partner["analyzable_games"] >= thresholds.partner_min_games
            and partner["analyzable_win_rate"] is not None
            and partner["analyzable_win_rate"] >= 85
            and partner["avg_duration"] is not None
            and partner["avg_duration"] >= 15
            and partner["invalid_short_losses"] == 0
        ]

    short_loss_partners = [
        partner
        for partner in partner_summaries
        if partner["games"] >= thresholds.partner_min_games
        and partner["invalid_short_losses"] >= 3
        and partner["short_loss_rate"] >= 50
    ]

    serious_partners.sort(
        key=lambda item: (
            item["analyzable_win_rate"] or 0,
            item["analyzable_games"],
            item["avg_duration"] or 0,
        ),
        reverse=True,
    )
    short_loss_partners.sort(
        key=lambda item: (item["invalid_short_losses"], item["short_loss_rate"]),
        reverse=True,
    )

    invalid_short_loss_rate = round(invalid_short_losses / len(games) * 100, 1)
    serious_partner = serious_partners[0] if serious_partners else None

    high_risk = invalid_short_losses >= 5 and serious_partner is not None
    medium_risk = invalid_short_losses >= 3 and (serious_partner is not None or short_loss_partners)

    if high_risk:
        label = "疑似炸鱼：存在上分/掉分搭档分化"
        confidence = "高"
    elif medium_risk:
        label = "疑似上分/掉分搭档分化"
        confidence = "中"
    elif serious_partner:
        label = "存在上分搭档倾向"
        confidence = "低"
    elif short_loss_partners:
        label = "存在掉分搭档倾向"
        confidence = "低"
    else:
        label = "未发现明显上分/掉分搭档分化"
        confidence = "低"

    evidence = [
        f"当前模式最近 {len(games)} 局中，少于 {thresholds.min_analyzable_game_minutes:g} 分钟的失败局有 {invalid_short_losses} 局，占比 {invalid_short_loss_rate}%。",
        f"搭档判断门槛：同队至少 {thresholds.partner_min_games} 局，少于该样本不标为搭档。",
    ]
    if serious_partner:
        evidence.append(
            f"上分搭档候选：与 {serious_partner['name']} 同队时，可分析对局 {serious_partner['analyzable_games']} 局，"
            f"胜率 {serious_partner['analyzable_win_rate']}%，平均时长 {serious_partner['avg_duration']} 分钟，"
            "没有少于 3 分钟的失败局。"
        )
    if short_loss_partners:
        partner = short_loss_partners[0]
        evidence.append(
            f"掉分搭档候选：与 {partner['name']} 同队时，少于 3 分钟的失败局 {partner['invalid_short_losses']} 局，"
            f"占该搭档样本 {partner['short_loss_rate']}%。"
        )
    evidence.append("提示：这是基于公开对局时长、胜负和同队玩家的行为模式判断，不能替代人工复盘。")

    return {
        "label": label,
        "confidence": confidence,
        "is_fixed_serious_pattern": high_risk or medium_risk,
        "invalid_short_losses": invalid_short_losses,
        "invalid_short_loss_rate": invalid_short_loss_rate,
        "raw_losses": raw_losses,
        "rank_up_partners": serious_partners[:5],
        "rank_down_partners": short_loss_partners[:5],
        "serious_partners": serious_partners[:5],
        "short_loss_partners": short_loss_partners[:5],
        "evidence": evidence,
    }


def get_leaderboard_player(leaderboard_data: dict[str, Any]) -> dict[str, Any] | None:
    players = leaderboard_data.get("players", [])
    if players:
        return players[0]
    return None


@dataclass(frozen=True)
class AnalysisThresholds:
    min_analyzable_game_minutes: float = 3.0
    civ_specialist_pick_rate: float = 50.0
    wide_pool_min_civs: int = 6
    hot_last_10_win_rate: float = 70.0
    cold_last_10_win_rate: float = 40.0
    strong_recent_win_rate: float = 65.0
    weak_recent_win_rate: float = 40.0
    fast_avg_minutes: float = 22.0
    macro_avg_minutes: float = 32.0
    suspicious_short_loss_minutes: float = 6.0
    suspicious_short_loss_count: int = 3
    suspicious_short_loss_high_count: int = 5
    suspicious_short_loss_rate: float = 15.0
    suspicious_short_loss_high_rate: float = 25.0
    smurf_low_games_count: int = 20
    smurf_high_win_rate: float = 75.0
    smurf_very_high_win_rate: float = 85.0
    smurf_recent_win_rate: float = 70.0
    smurf_rating_floor: int = 1100
    local_many_games_count: int = 100
    local_very_many_games_count: int = 200
    local_win_rate_low: float = 45.0
    local_win_rate_high: float = 60.0
    local_stable_win_rate_low: float = 47.0
    local_stable_win_rate_high: float = 57.0
    partner_min_games: int = 5


def style_share(civ_count: Counter[str], style: str, total: int) -> float:
    if total <= 0:
        return 0.0
    games = 0
    for civ_key, count in civ_count.items():
        if style in CIV_STYLE_PROFILES.get(civ_key, set()):
            games += count
    return round(games / total * 100, 1)


def confidence_from_evidence(*conditions: bool) -> str:
    score = sum(1 for condition in conditions if condition)
    if score >= 3:
        return "高"
    if score == 2:
        return "中"
    return "低"


def build_behavior_risk(
    short_losses: list[dict[str, Any]],
    total: int,
    thresholds: AnalysisThresholds,
) -> dict[str, Any]:
    short_loss_count = len(short_losses)
    short_loss_rate = round(short_loss_count / total * 100, 1) if total else 0.0
    short_loss_examples = short_losses[:5]

    high_risk = (
        short_loss_count >= thresholds.suspicious_short_loss_high_count
        or (
            short_loss_count >= thresholds.suspicious_short_loss_count
            and short_loss_rate >= thresholds.suspicious_short_loss_high_rate
        )
    )
    medium_risk = (
        short_loss_count >= thresholds.suspicious_short_loss_count
        or short_loss_rate >= thresholds.suspicious_short_loss_rate
    )

    if high_risk:
        label = "疑似炸鱼风险高"
        confidence = "高"
    elif medium_risk:
        label = "疑似炸鱼风险中"
        confidence = "中"
    else:
        label = "未发现明显炸鱼迹象"
        confidence = "低"

    evidence = [
        (
            f"最近 {total} 局中，有 {short_loss_count} 局是 "
            f"{thresholds.suspicious_short_loss_minutes:g} 分钟以内失败，占比 {short_loss_rate}%。"
        )
    ]
    if short_loss_examples:
        examples = []
        for game in short_loss_examples:
            game_id = game.get("game_id")
            duration = game.get("duration")
            if game_id:
                examples.append(f"#{game_id}（{duration} 分钟）")
            else:
                examples.append(f"{duration} 分钟")
        evidence.append("示例短败局：" + "、".join(examples))
    evidence.append("提示：极短败局可能来自掉线、崩溃、队友退、排错图等原因，不能单独证明炸鱼。")

    return {
        "label": label,
        "confidence": confidence,
        "short_loss_count": short_loss_count,
        "short_loss_rate": short_loss_rate,
        "threshold_minutes": thresholds.suspicious_short_loss_minutes,
        "evidence": evidence,
    }


def build_smurf_risk(
    leaderboard_summary: dict[str, Any],
    recent_games: int,
    recent_win_rate: float,
    effective_games: int,
    effective_win_rate: float | None,
    thresholds: AnalysisThresholds,
) -> dict[str, Any]:
    games_count = leaderboard_summary.get("games_count")
    overall_win_rate = leaderboard_summary.get("win_rate")
    rating = leaderboard_summary.get("rating")
    rank_level_cn = leaderboard_summary.get("rank_level_cn")

    if games_count is None and overall_win_rate is None and rating is None:
        evidence = [
            "当前模式没有可用的总场次、总胜率或分数数据。",
            f"最近 {recent_games} 局原始胜率 {recent_win_rate}%。",
        ]
        if effective_win_rate is not None:
            evidence.append(f"排除极短失败局后，有效样本 {effective_games} 局，有效胜率 {effective_win_rate}%。")
        return {
            "label": "缺少账号总体数据，无法判断小号风险",
            "confidence": "低",
            "games_count": games_count,
            "overall_win_rate": overall_win_rate,
            "rating": rating,
            "effective_games": effective_games,
            "effective_win_rate": effective_win_rate,
            "is_smurf_risk": False,
            "is_local_account": False,
            "evidence": evidence,
        }

    low_games = isinstance(games_count, (int, float)) and games_count <= thresholds.smurf_low_games_count
    very_high_overall_wr = (
        isinstance(overall_win_rate, (int, float))
        and overall_win_rate >= thresholds.smurf_very_high_win_rate
    )
    high_overall_wr = (
        isinstance(overall_win_rate, (int, float))
        and overall_win_rate >= thresholds.smurf_high_win_rate
    )
    strength_win_rate = effective_win_rate if effective_win_rate is not None else recent_win_rate
    strength_games = effective_games if effective_win_rate is not None else recent_games
    high_recent_wr = strength_games >= 8 and strength_win_rate >= thresholds.smurf_recent_win_rate
    decent_rating = isinstance(rating, (int, float)) and rating >= thresholds.smurf_rating_floor
    many_games = isinstance(games_count, (int, float)) and games_count >= thresholds.local_many_games_count
    very_many_games = (
        isinstance(games_count, (int, float))
        and games_count >= thresholds.local_very_many_games_count
    )
    average_win_rate = (
        isinstance(overall_win_rate, (int, float))
        and thresholds.local_win_rate_low <= overall_win_rate <= thresholds.local_win_rate_high
    )
    stable_average_win_rate = (
        isinstance(overall_win_rate, (int, float))
        and thresholds.local_stable_win_rate_low <= overall_win_rate <= thresholds.local_stable_win_rate_high
    )

    high_risk = low_games and (very_high_overall_wr or (high_overall_wr and high_recent_wr and decent_rating))
    medium_risk = low_games and (high_overall_wr or high_recent_wr)
    local_account = many_games and average_win_rate
    stable_local_account = very_many_games and stable_average_win_rate

    if high_risk:
        label = "疑似高手小号风险高"
        confidence = "高"
    elif medium_risk:
        label = "疑似高手小号风险中"
        confidence = "中"
    elif stable_local_account:
        label = "本地人/正常长期玩家"
        confidence = "高"
    elif local_account:
        label = "偏本地人/正常账号"
        confidence = "中"
    else:
        label = "未发现明显高手小号迹象"
        confidence = "低"

    evidence = []
    if games_count is not None:
        evidence.append(f"当前模式总场次 {games_count} 局。")
    if overall_win_rate is not None:
        evidence.append(f"当前模式总胜率 {overall_win_rate}%。")
    evidence.append(f"最近 {recent_games} 局原始胜率 {recent_win_rate}%。")
    if effective_win_rate is not None:
        evidence.append(f"排除极短失败局后，有效样本 {effective_games} 局，有效胜率 {effective_win_rate}%。")
    if rating is not None:
        rating_text = f"当前分数 {rating}"
        if rank_level_cn:
            rating_text += f"，段位 {rank_level_cn}"
        evidence.append(rating_text + "。")
    if high_risk or medium_risk:
        evidence.append("提示：高胜率低场次也可能是老玩家回归、换平台或赛季初样本少，不能单独证明炸鱼。")
    elif local_account or stable_local_account:
        evidence.append("提示：本地人表示账号更像长期正常匹配样本，不代表实力固定或一定没有异常。")
    else:
        evidence.append("提示：账号类型判断只基于当前模式总场次、总胜率和近期表现。")

    return {
        "label": label,
        "confidence": confidence,
        "games_count": games_count,
        "overall_win_rate": overall_win_rate,
        "rating": rating,
        "effective_games": effective_games,
        "effective_win_rate": effective_win_rate,
        "is_smurf_risk": high_risk or medium_risk,
        "is_local_account": local_account or stable_local_account,
        "evidence": evidence,
    }


def build_style_profile(
    total: int,
    recent_win_rate: float,
    last_10_win_rate: float,
    avg_duration: float | None,
    main_civs: list[dict[str, Any]],
    civ_count: Counter[str],
) -> dict[str, Any]:
    cavalry_share = style_share(civ_count, "cavalry", total)
    economy_share = style_share(civ_count, "economy", total)
    feudal_share = style_share(civ_count, "feudal", total)
    castle_share = style_share(civ_count, "castle", total)
    late_share = style_share(civ_count, "late", total)
    top_civ = main_civs[0] if main_civs else None

    duration_text = "缺少对局时长数据"
    if avg_duration is not None:
        duration_text = f"最近对局平均 {avg_duration} 分钟"

    economy_conditions = (
        avg_duration is not None and avg_duration >= 30,
        economy_share >= 35,
        recent_win_rate >= 55 and avg_duration is not None and avg_duration >= 26,
    )
    if economy_share >= 45 or (avg_duration is not None and avg_duration >= 32):
        economy_label = "发育运营倾向明显"
    elif economy_share >= 25 or (avg_duration is not None and avg_duration >= 27):
        economy_label = "有一定发育运营倾向"
    else:
        economy_label = "不属于明显纯发育型"

    cavalry_conditions = (
        cavalry_share >= 35,
        top_civ is not None and "cavalry" in CIV_STYLE_PROFILES.get(top_civ["key"], set()),
        avg_duration is not None and avg_duration <= 26,
    )
    if cavalry_share >= 45:
        cavalry_label = "跑马/机动骚扰倾向强"
    elif cavalry_share >= 25:
        cavalry_label = "有一定跑马/机动骚扰倾向"
    else:
        cavalry_label = "跑马倾向不明显"

    dominant_timing = max(
        [
            ("封建时代", "feudal", feudal_share),
            ("城堡时代", "castle", castle_share),
            ("帝王/后期", "late", late_share),
        ],
        key=lambda item: item[2],
    )

    duration_timing_key = "unknown"
    if avg_duration is None:
        timing_label = "开战时代无法判断"
        timing_detail = "最近对局缺少时长数据，无法推断常见开战窗口。"
    elif avg_duration < 20 and castle_share >= 45:
        duration_timing_key = "castle"
        timing_label = "偏封建后期到城堡初期抢节奏"
        timing_detail = "平均时长很短，但文明池明显偏城堡节奏，更像快速转城堡或城堡初期打决定性一波。"
    elif avg_duration < 20:
        duration_timing_key = "feudal"
        timing_label = "偏封建时代开战"
        timing_detail = "平均时长很短，更像封建前中期就出现高强度交战或一波结束。"
    elif avg_duration < 26:
        duration_timing_key = "feudal" if feudal_share >= castle_share else "castle"
        timing_label = "偏封建中后期到城堡初期开战"
        timing_detail = "平均时长偏短，常见决胜窗口大概率在封建后期或刚进城堡时。"
    elif avg_duration < 34:
        duration_timing_key = "castle"
        timing_label = "偏城堡时代中期打架"
        timing_detail = "平均时长居中，更像进入城堡时代后通过中期推进、控图或持续换兵决胜。"
    else:
        duration_timing_key = "late"
        timing_label = "偏城堡后期到帝王时代"
        timing_detail = "平均时长较长，说明不少对局会拖入大规模运营和后期会战。"

    timing_aligned = dominant_timing[2] < 35 or dominant_timing[1] == duration_timing_key
    timing_evidence = [
        duration_text,
        f"文明池倾向：封建 {feudal_share}%，城堡 {castle_share}%，后期 {late_share}%",
        timing_detail,
    ]
    if dominant_timing[2] >= 35:
        timing_evidence.append(f"结合文明池，更偏向{dominant_timing[0]}节奏。")

    overall_parts = []
    if top_civ:
        overall_parts.append(
            f"最常用文明是{top_civ['civ']}，使用率 {top_civ['pick_rate']}%。"
        )
    if total >= 10:
        overall_parts.append(f"最近 {total} 局胜率 {recent_win_rate}%，最近 10 局胜率 {last_10_win_rate}%。")
    else:
        overall_parts.append(f"最近 {total} 局胜率 {recent_win_rate}%。")
    overall_parts.append(f"综合判断：{economy_label}，{cavalry_label}，{timing_label}。")

    return {
        "overall": "".join(overall_parts),
        "economy": {
            "label": economy_label,
            "confidence": confidence_from_evidence(*economy_conditions),
            "evidence": [
                duration_text,
                f"发育型文明占比约 {economy_share}%。",
                "注意：这里是从文明池和对局时长推断，不等同于确认双 TC 或裸城堡。",
            ],
        },
        "cavalry": {
            "label": cavalry_label,
            "confidence": confidence_from_evidence(*cavalry_conditions),
            "evidence": [
                f"骑兵/机动文明占比约 {cavalry_share}%。",
                duration_text,
                "注意：公开接口没有提供具体骑兵数量或骚扰次数，所以这是倾向判断。",
            ],
        },
        "fight_timing": {
            "label": timing_label,
            "confidence": confidence_from_evidence(
                avg_duration is not None,
                timing_aligned,
                total >= 20,
            ),
            "evidence": timing_evidence,
        },
    }


def add_translation_entry(
    table: list[dict[str, str]],
    seen: set[tuple[str, str]],
    category: str,
    raw: Any,
    english: str,
    chinese: str,
) -> None:
    key = (category, normalize_key(raw))
    if key in seen:
        return
    seen.add(key)
    if chinese == english:
        return
    table.append({"category": category, "english": english, "chinese": chinese})


def analyze_player_style(
    profile_id: int,
    games_data: Any,
    leaderboard_data: dict[str, Any] | None = None,
    leaderboard: str | None = None,
    thresholds: AnalysisThresholds | None = None,
) -> dict[str, Any]:
    thresholds = thresholds or AnalysisThresholds()
    source_games = extract_games(games_data)
    mode_games = [game for game in source_games if game_matches_leaderboard(game, leaderboard)]
    games = []
    for game in mode_games:
        duration_minutes = game_duration_minutes(game)
        if duration_minutes is None or duration_minutes >= thresholds.min_analyzable_game_minutes:
            games.append(game)

    filtered_out_games = len(source_games) - len(mode_games)
    excluded_short_games = len(mode_games) - len(games)
    behavior_short_losses = collect_short_loss_games(mode_games, profile_id, thresholds)
    relation_pattern = build_fixed_player_pattern(mode_games, profile_id, thresholds)
    tracked_games: list[dict[str, Any]] = []

    wins = 0
    last_10_wins = 0
    civ_count: Counter[str] = Counter()
    civ_wins: defaultdict[str, int] = defaultdict(int)
    civ_names: dict[str, dict[str, str]] = {}
    map_count: Counter[str] = Counter()
    map_wins: defaultdict[str, int] = defaultdict(int)
    map_names: dict[str, dict[str, str]] = {}
    durations: list[float] = []
    effective_games = 0
    effective_wins = 0

    for game in games:
        player = find_target_player(game, profile_id)
        if player is None:
            continue

        tracked_games.append(game)
        result = str(player.get("result", "")).lower()
        won = result == "win" or player.get("won") is True

        if won:
            wins += 1
            if len(tracked_games) <= 10:
                last_10_wins += 1

        civ_raw = player.get("civilization") or player.get("civilization_name")
        civ_key = normalize_key(civ_raw)
        civ_count[civ_key] += 1
        civ_names[civ_key] = {
            "raw": civ_key,
            "english": english_term(civ_raw, "civilizations"),
            "chinese": translate_term(civ_raw, "civilizations"),
        }
        if won:
            civ_wins[civ_key] += 1

        map_raw = game.get("map") or game.get("map_name")
        map_key = normalize_key(map_raw)
        map_count[map_key] += 1
        map_names[map_key] = {
            "raw": map_key,
            "english": english_term(map_raw, "maps"),
            "chinese": translate_term(map_raw, "maps"),
        }
        if won:
            map_wins[map_key] += 1

        duration_minutes = game_duration_minutes(game)
        is_short_loss = False
        if duration_minutes is not None and duration_minutes > 0:
            durations.append(duration_minutes)
            if not won and duration_minutes <= thresholds.suspicious_short_loss_minutes:
                is_short_loss = True
        if not is_short_loss:
            effective_games += 1
            if won:
                effective_wins += 1

    total = len(tracked_games)
    if total == 0:
        return {
            "recent_games": 0,
            "recent_win_rate": 0.0,
            "last_10_win_rate": None,
            "avg_duration": None,
            "main_civs": [],
            "top_maps": [],
            "tags": [],
            "style_profile": {},
            "behavior_risk": build_behavior_risk(behavior_short_losses, len(mode_games), thresholds),
            "account_profile": {},
            "relation_pattern": relation_pattern,
            "translation_table": [],
            "leaderboard": {},
            "requested_leaderboard": leaderboard,
            "source_games": len(source_games),
            "filtered_out_games": filtered_out_games,
            "excluded_short_games": excluded_short_games,
            "min_analyzable_game_minutes": thresholds.min_analyzable_game_minutes,
            "summary": (
                f"该模式下没有找到可用于分析的最近对局。"
                f"{thresholds.min_analyzable_game_minutes:g} 分钟以内的对局已被排除。"
            ),
        }

    recent_win_rate = round(wins / total * 100, 1)
    last_10_count = min(10, total)
    last_10_win_rate = round(last_10_wins / last_10_count * 100, 1)
    effective_win_rate = round(effective_wins / effective_games * 100, 1) if effective_games else None
    avg_duration = round(sum(durations) / len(durations), 1) if durations else None

    main_civs = []
    for civ_key, count in civ_count.most_common(5):
        names = civ_names[civ_key]
        main_civs.append(
            {
                "key": civ_key,
                "civ": names["chinese"],
                "civ_en": names["english"],
                "games": count,
                "pick_rate": round(count / total * 100, 1),
                "win_rate": round(civ_wins[civ_key] / count * 100, 1),
            }
        )

    top_maps = []
    for map_key, count in map_count.most_common(5):
        names = map_names[map_key]
        top_maps.append(
            {
                "key": map_key,
                "map": names["chinese"],
                "map_en": names["english"],
                "games": count,
                "pick_rate": round(count / total * 100, 1),
                "win_rate": round(map_wins[map_key] / count * 100, 1),
            }
        )

    tags: list[str] = []
    insights: list[str] = []

    if main_civs:
        top_civ = main_civs[0]
        if top_civ["pick_rate"] >= thresholds.civ_specialist_pick_rate:
            tags.append("文明专精型")
            insights.append(
                f"最近对局明显集中在{top_civ['civ']}，使用率 {top_civ['pick_rate']}%。"
            )
        elif len(civ_count) >= thresholds.wide_pool_min_civs:
            tags.append("文明池宽")
            insights.append(f"最近使用过 {len(civ_count)} 个不同文明，文明池较宽。")
        else:
            tags.append("文明池集中")

    if last_10_win_rate >= thresholds.hot_last_10_win_rate:
        tags.append("近期状态火热")
        insights.append(f"最近 {last_10_count} 局胜率 {last_10_win_rate}%，短期状态很好。")
    elif last_10_win_rate <= thresholds.cold_last_10_win_rate:
        tags.append("近期状态低迷")
        insights.append(f"最近 {last_10_count} 局胜率 {last_10_win_rate}%，短期状态一般。")
    elif recent_win_rate >= thresholds.strong_recent_win_rate:
        tags.append("近期表现强")
    elif recent_win_rate <= thresholds.weak_recent_win_rate:
        tags.append("近期表现弱")

    if avg_duration is not None:
        if avg_duration < thresholds.fast_avg_minutes:
            tags.append("快节奏")
            insights.append("平均对局时长偏短，说明经常在前中期结束。")
        elif avg_duration > thresholds.macro_avg_minutes:
            tags.append("运营发育型")
            insights.append("平均对局时长偏长，说明不少对局会进入中后期运营。")
        else:
            tags.append("节奏均衡")

    if top_maps and top_maps[0]["games"] >= 3 and top_maps[0]["win_rate"] >= 65:
        tags.append("地图熟练度高")
        insights.append(
            f"{top_maps[0]['map']} 出现 {top_maps[0]['games']} 局，胜率 {top_maps[0]['win_rate']}%，表现较好。"
        )

    style_profile = build_style_profile(
        total=total,
        recent_win_rate=recent_win_rate,
        last_10_win_rate=last_10_win_rate,
        avg_duration=avg_duration,
        main_civs=main_civs,
        civ_count=civ_count,
    )
    if "跑马/机动骚扰倾向强" in style_profile["cavalry"]["label"]:
        tags.append("机动骚扰倾向")
    if "发育运营倾向明显" in style_profile["economy"]["label"]:
        tags.append("发育运营倾向")

    leaderboard_player = get_leaderboard_player(leaderboard_data or {})
    leaderboard_summary = {}
    if leaderboard_player:
        rank_level = leaderboard_player.get("rank_level")
        leaderboard_summary = {
            "rating": leaderboard_player.get("rating"),
            "rank": leaderboard_player.get("rank"),
            "rank_level": rank_level,
            "rank_level_cn": translate_term(rank_level, "rank_levels") if rank_level else None,
            "max_rating": leaderboard_player.get("max_rating"),
            "games_count": leaderboard_player.get("games_count"),
            "win_rate": leaderboard_player.get("win_rate"),
            "last_game_at": leaderboard_player.get("last_game_at"),
        }

    behavior_risk = build_behavior_risk(behavior_short_losses, len(mode_games), thresholds)
    if behavior_risk.get("label") and ("风险高" in behavior_risk["label"] or "风险中" in behavior_risk["label"]):
        tags.append("疑似炸鱼")
        insights.append(
            f"检测到 {behavior_risk['short_loss_count']} 局极短失败，"
            f"占最近样本 {behavior_risk['short_loss_rate']}%，存在疑似炸鱼风险。"
        )

    if relation_pattern.get("is_fixed_serious_pattern"):
        tags.append("上分/掉分搭档分化")
        evidence = relation_pattern.get("evidence") or []
        partner_evidence = next((item for item in evidence if "上分搭档候选" in item), None)
        insights.append(partner_evidence or relation_pattern["label"])

    account_profile = build_smurf_risk(
        leaderboard_summary=leaderboard_summary,
        recent_games=total,
        recent_win_rate=recent_win_rate,
        effective_games=effective_games,
        effective_win_rate=effective_win_rate,
        thresholds=thresholds,
    )
    if account_profile.get("is_smurf_risk"):
        tags.append("疑似高手小号")
        insights.append(f"{account_profile['label']}：总场次少但胜率偏高，需要结合对局详情人工判断。")
    elif account_profile.get("is_local_account"):
        tags.append("本地人")
        insights.append("账号总场次较多且长期胜率接近正常匹配区间，更像正常长期玩家。")

    translation_table: list[dict[str, str]] = []
    seen_translations: set[tuple[str, str]] = set()
    for civ in main_civs:
        add_translation_entry(
            translation_table,
            seen_translations,
            "文明",
            civ["key"],
            civ["civ_en"],
            civ["civ"],
        )
    for map_info in top_maps:
        add_translation_entry(
            translation_table,
            seen_translations,
            "地图",
            map_info["key"],
            map_info["map_en"],
            map_info["map"],
        )
    for tag in tags:
        english = TRANSLATIONS["tags"].get(tag)
        if english:
            add_translation_entry(
                translation_table,
                seen_translations,
                "标签",
                tag,
                english,
                tag,
            )

    if total >= 10:
        summary_parts = [
            f"最近 {total} 局胜率 {recent_win_rate}%，最近 {last_10_count} 局胜率 {last_10_win_rate}%。"
        ]
    else:
        summary_parts = [f"最近 {total} 局胜率 {recent_win_rate}%。"]
    if main_civs:
        top_civ = main_civs[0]
        summary_parts.append(
            f"主力文明是{top_civ['civ']}，使用率 {top_civ['pick_rate']}%，该文明胜率 {top_civ['win_rate']}%。"
        )
    if avg_duration is not None:
        summary_parts.append(f"平均对局时长约 {avg_duration} 分钟。")
    summary_parts.append(style_profile["overall"])
    if insights:
        summary_parts.extend(insights)

    return {
        "recent_games": total,
        "recent_win_rate": recent_win_rate,
        "last_10_win_rate": last_10_win_rate,
        "effective_games": effective_games,
        "effective_win_rate": effective_win_rate,
        "avg_duration": avg_duration,
        "main_civs": main_civs,
        "top_maps": top_maps,
        "tags": tags,
        "style_profile": style_profile,
        "behavior_risk": behavior_risk,
        "account_profile": account_profile,
        "relation_pattern": relation_pattern,
        "translation_table": translation_table,
        "leaderboard": leaderboard_summary,
        "requested_leaderboard": leaderboard,
        "source_games": len(source_games),
        "filtered_out_games": filtered_out_games,
        "excluded_short_games": excluded_short_games,
        "min_analyzable_game_minutes": thresholds.min_analyzable_game_minutes,
        "summary": " ".join(summary_parts),
    }

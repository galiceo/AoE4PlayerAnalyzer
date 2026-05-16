import sys
from typing import Any, Callable

from PySide6.QtCore import QObject, QRunnable, QStringListModel, QThreadPool, QTimer, Qt, Signal, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QCompleter,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from analyzer import LEADERBOARD_LABELS, analyze_player_style, translate_term
from aoe4_api import Aoe4ApiError, Aoe4WorldClient


class WorkerSignals(QObject):
    result = Signal(object)
    error = Signal(str)
    finished = Signal()


class Worker(QRunnable):
    def __init__(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self) -> None:
        try:
            self.signals.result.emit(self.fn(*self.args, **self.kwargs))
        except Exception as exc:
            self.signals.error.emit(str(exc))
        finally:
            self.signals.finished.emit()


class Metric(QFrame):
    def __init__(self, label: str) -> None:
        super().__init__()
        self.setObjectName("Metric")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)

        self.value_label = QLabel("-")
        self.value_label.setObjectName("MetricValue")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        label_widget = QLabel(label)
        label_widget.setObjectName("MetricLabel")

        layout.addWidget(self.value_label)
        layout.addWidget(label_widget)

    def set_value(self, value: Any) -> None:
        self.value_label.setText("-" if value is None or value == "" else str(value))


class AoE4AnalyzerWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.client = Aoe4WorldClient()
        self.thread_pool = QThreadPool.globalInstance()
        self.active_workers: set[Worker] = set()
        self.players: list[dict[str, Any]] = []
        self.selected_player: dict[str, Any] | None = None
        self.completion_lookup: dict[str, dict[str, Any]] = {}
        self.completion_model = QStringListModel(self)
        self.autocomplete_request_id = 0

        self.autocomplete_timer = QTimer(self)
        self.autocomplete_timer.setInterval(350)
        self.autocomplete_timer.setSingleShot(True)
        self.autocomplete_timer.timeout.connect(self.fetch_autocomplete)

        self.setWindowTitle("AoE4 Player Style Analyzer")
        self.resize(1080, 720)

        self._build_ui()
        self._apply_styles()

    def _build_ui(self) -> None:
        root = QWidget()
        outer = QVBoxLayout(root)
        outer.setContentsMargins(22, 18, 22, 18)
        outer.setSpacing(16)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("AoE4 战绩风格分析器")
        title.setObjectName("AppTitle")
        subtitle = QLabel("本地桌面工具，数据来自 AOE4 World API")
        subtitle.setObjectName("SubTitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box, 1)

        self.clear_cache_button = QPushButton("清除缓存")
        self.clear_cache_button.clicked.connect(self.clear_cache)
        header.addWidget(self.clear_cache_button)
        outer.addLayout(header)

        controls = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入玩家名，至少 3 个字符后自动联想")
        self.completer = QCompleter(self.completion_model, self.search_input)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.activated[str].connect(self.select_completion)
        self.search_input.setCompleter(self.completer)
        self.search_input.textChanged.connect(self.schedule_autocomplete)
        self.search_input.returnPressed.connect(self.search_players)
        controls.addWidget(self.search_input, 3)

        self.mode_box = QComboBox()
        for key, label in LEADERBOARD_LABELS.items():
            self.mode_box.addItem(label, key)
        self.mode_box.setCurrentIndex(self.mode_box.findData("rm_solo"))
        self.mode_box.currentIndexChanged.connect(
            lambda: self.schedule_autocomplete(self.search_input.text())
        )
        controls.addWidget(self.mode_box, 1)

        self.search_button = QPushButton("搜索")
        self.search_button.clicked.connect(self.search_players)
        controls.addWidget(self.search_button)
        outer.addLayout(controls)

        content = QHBoxLayout()
        content.setSpacing(16)

        left = QVBoxLayout()
        left_title = QLabel("匹配玩家")
        left_title.setObjectName("SectionTitle")
        left.addWidget(left_title)

        self.result_list = QListWidget()
        self.result_list.itemClicked.connect(self.select_player)
        left.addWidget(self.result_list, 1)
        content.addLayout(left, 2)

        right = QVBoxLayout()
        right_title = QLabel("玩家分析")
        right_title.setObjectName("SectionTitle")
        right.addWidget(right_title)

        self.player_header = QLabel("输入玩家名并选择一个玩家")
        self.player_header.setObjectName("PlayerHeader")
        right.addWidget(self.player_header)

        metrics_grid = QGridLayout()
        metrics_grid.setHorizontalSpacing(10)
        metrics_grid.setVerticalSpacing(10)
        self.metric_rating = Metric("当前分数")
        self.metric_rank = Metric("排名/段位")
        self.metric_recent_wr = Metric("最近胜率")
        self.metric_last10_wr = Metric("最近 10 局")
        self.metric_games = Metric("统计局数")
        self.metric_duration = Metric("平均时长")
        metrics = [
            self.metric_rating,
            self.metric_rank,
            self.metric_recent_wr,
            self.metric_last10_wr,
            self.metric_games,
            self.metric_duration,
        ]
        for index, widget in enumerate(metrics):
            metrics_grid.addWidget(widget, index // 3, index % 3)
        right.addLayout(metrics_grid)

        self.tags_label = QLabel("风格标签：-")
        self.tags_label.setObjectName("Tags")
        self.tags_label.setWordWrap(True)
        right.addWidget(self.tags_label)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("分析结果会显示在这里")
        right.addWidget(self.output, 1)

        content.addLayout(right, 4)
        outer.addLayout(content, 1)

        self.status_label = QLabel("就绪")
        self.status_label.setObjectName("Status")
        outer.addWidget(self.status_label)

        self.setCentralWidget(root)

    def _apply_styles(self) -> None:
        QApplication.instance().setFont(QFont("Segoe UI", 10))
        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background: #f5f7fa;
                color: #17212b;
            }
            #AppTitle {
                font-size: 24px;
                font-weight: 700;
            }
            #SubTitle, #Status, #MetricLabel {
                color: #667085;
            }
            #SectionTitle {
                font-size: 15px;
                font-weight: 700;
            }
            #PlayerHeader {
                font-size: 18px;
                font-weight: 700;
                padding: 4px 0;
            }
            QLineEdit, QComboBox, QTextEdit, QListWidget {
                background: #ffffff;
                border: 1px solid #d0d5dd;
                border-radius: 6px;
                padding: 8px;
            }
            QListWidget::item {
                padding: 9px;
                border-bottom: 1px solid #eef1f5;
            }
            QListWidget::item:selected {
                background: #d9e8ff;
                color: #101828;
            }
            QPushButton {
                background: #205493;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 9px 14px;
                font-weight: 600;
            }
            QPushButton:disabled {
                background: #98a2b3;
            }
            QPushButton:hover {
                background: #174472;
            }
            #Metric {
                background: #ffffff;
                border: 1px solid #d0d5dd;
                border-radius: 6px;
            }
            #MetricValue {
                font-size: 19px;
                font-weight: 700;
            }
            #Tags {
                background: #edf6f9;
                border: 1px solid #b9dfe8;
                border-radius: 6px;
                padding: 10px;
            }
            """
        )

    def set_busy(self, busy: bool, message: str) -> None:
        self.status_label.setText(message)
        self.search_button.setEnabled(not busy)
        self.clear_cache_button.setEnabled(not busy)
        self.result_list.setEnabled(not busy)
        self.mode_box.setEnabled(not busy)
        self.search_input.setEnabled(not busy)

    def run_worker(
        self,
        fn: Callable[..., Any],
        result_handler: Callable[[Any], None],
        busy_message: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.set_busy(True, busy_message)
        worker = Worker(fn, *args, **kwargs)
        self.active_workers.add(worker)
        worker.signals.result.connect(result_handler)
        worker.signals.error.connect(self.handle_error)
        worker.signals.finished.connect(
            lambda worker=worker: self.finish_worker(worker, reset_busy=True)
        )
        self.thread_pool.start(worker)

    def run_background_worker(
        self,
        fn: Callable[..., Any],
        result_handler: Callable[[Any], None],
        error_handler: Callable[[str], None],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        worker = Worker(fn, *args, **kwargs)
        self.active_workers.add(worker)
        worker.signals.result.connect(result_handler)
        worker.signals.error.connect(error_handler)
        worker.signals.finished.connect(
            lambda worker=worker: self.finish_worker(worker, reset_busy=False)
        )
        self.thread_pool.start(worker)

    def finish_worker(self, worker: Worker, reset_busy: bool) -> None:
        self.active_workers.discard(worker)
        if reset_busy:
            self.set_busy(False, "就绪")

    def schedule_autocomplete(self, text: str) -> None:
        query = text.strip()
        if len(query) < 3:
            self.autocomplete_timer.stop()
            self.autocomplete_request_id += 1
            self.players = []
            self.result_list.clear()
            self.status_label.setText("至少输入 3 个字符后自动联想" if query else "就绪")
            return

        self.autocomplete_timer.start()

    def fetch_autocomplete(self) -> None:
        query = self.search_input.text().strip()
        if len(query) < 3:
            return

        self.autocomplete_request_id += 1
        request_id = self.autocomplete_request_id
        leaderboard = self.autocomplete_leaderboard()
        self.status_label.setText(f"正在联想：{query}...")
        self.run_background_worker(
            self.load_autocomplete,
            self.handle_autocomplete_results,
            lambda message, request_id=request_id: self.handle_autocomplete_error(request_id, message),
            request_id,
            query,
            leaderboard,
        )

    def autocomplete_leaderboard(self) -> str:
        leaderboard = str(self.mode_box.currentData() or "rm_solo")
        allowed = {"rm_solo", "rm_team", "qm_1v1", "qm_2v2", "qm_3v3", "qm_4v4"}
        if leaderboard in allowed:
            return leaderboard
        if leaderboard == "rm_1v1":
            return "rm_solo"
        if leaderboard.startswith("rm_"):
            return "rm_team"
        return "rm_solo"

    def load_autocomplete(
        self,
        request_id: int,
        query: str,
        leaderboard: str,
    ) -> dict[str, Any]:
        data = self.client.autocomplete_players(query, leaderboard=leaderboard, limit=8)
        return {"request_id": request_id, "query": query, "data": data}

    def handle_autocomplete_results(self, payload: dict[str, Any]) -> None:
        if payload["request_id"] != self.autocomplete_request_id:
            return
        if payload["query"] != self.search_input.text().strip():
            return

        self.players = payload["data"].get("players", []) or []
        self.result_list.clear()
        self.completion_lookup = {}
        completion_labels = []

        if not self.players:
            self.completion_model.setStringList([])
            self.player_header.setText("没有找到匹配玩家")
            self.status_label.setText("没有找到匹配玩家")
            return

        for player in self.players:
            item = QListWidgetItem(self.format_player_row(player))
            item.setData(Qt.ItemDataRole.UserRole, player.get("profile_id"))
            self.result_list.addItem(item)
            label = self.format_completion_label(player)
            completion_labels.append(label)
            self.completion_lookup[label] = player

        self.completion_model.setStringList(completion_labels)
        if self.search_input.hasFocus():
            self.completer.complete()

        self.player_header.setText("选择左侧玩家开始分析")
        self.status_label.setText(f"自动匹配 {len(self.players)} 个玩家")

    def handle_autocomplete_error(self, request_id: int, message: str) -> None:
        if request_id != self.autocomplete_request_id:
            return
        self.status_label.setText(f"自动联想失败：{message}")

    def search_players(self) -> None:
        query = self.search_input.text().strip()
        if len(query) < 3:
            QMessageBox.warning(self, "输入太短", "请输入至少 3 个字符。")
            return
        self.autocomplete_timer.stop()
        self.autocomplete_request_id += 1
        self.output.clear()
        self.player_header.setText("搜索中...")
        self.result_list.clear()
        self.run_worker(
            self.client.search_players,
            self.handle_search_results,
            "正在搜索玩家...",
            query,
        )

    def handle_search_results(self, data: dict[str, Any]) -> None:
        self.players = data.get("players", []) or []
        self.result_list.clear()
        self.completion_model.setStringList([])
        self.completion_lookup = {}

        if not self.players:
            self.player_header.setText("没有找到玩家")
            self.status_label.setText("没有找到玩家")
            return

        for player in self.players:
            item = QListWidgetItem(self.format_player_row(player))
            item.setData(Qt.ItemDataRole.UserRole, player.get("profile_id"))
            self.result_list.addItem(item)

        self.player_header.setText("选择左侧玩家开始分析")
        self.status_label.setText(f"找到 {len(self.players)} 个玩家")

    def format_player_row(self, player: dict[str, Any]) -> str:
        name = player.get("name", "Unknown")
        profile_id = player.get("profile_id", "-")
        country = str(player.get("country") or "??").upper()
        leaderboard = str(self.mode_box.currentData() or "rm_solo")
        leaderboard_data = (player.get("leaderboards") or {}).get(leaderboard) or {}
        rating = player.get("rating", leaderboard_data.get("rating"))
        rank = player.get("rank", leaderboard_data.get("rank"))
        rank_level_value = player.get("rank_level", leaderboard_data.get("rank_level"))
        rank_level = translate_term(rank_level_value, "rank_levels") if rank_level_value else "未定级"
        mode = LEADERBOARD_LABELS.get(leaderboard, leaderboard)
        rating_text = f"{rating}" if rating is not None else "-"
        rank_text = f"#{rank}" if rank else "无排名"
        return f"{name}\nID: {profile_id} | {country} | {mode} {rating_text} | {rank_text} | {rank_level}"

    def format_completion_label(self, player: dict[str, Any]) -> str:
        name = player.get("name", "Unknown")
        profile_id = player.get("profile_id", "-")
        country = str(player.get("country") or "??").upper()
        rating = player.get("rating")
        rank = player.get("rank")
        rank_level = translate_term(player.get("rank_level"), "rank_levels") if player.get("rank_level") else "未定级"
        rating_text = f"{rating}" if rating is not None else "-"
        rank_text = f"#{rank}" if rank else "无排名"
        return f"{name} | ID {profile_id} | {country} | {rating_text} | {rank_text} | {rank_level}"

    def select_completion(self, label: str) -> None:
        player = self.completion_lookup.get(label)
        if player is None:
            return
        self.start_player_analysis(player)

    def select_player(self, item: QListWidgetItem) -> None:
        index = self.result_list.row(item)
        if index < 0 or index >= len(self.players):
            return

        self.start_player_analysis(self.players[index])

    def start_player_analysis(self, player: dict[str, Any]) -> None:
        self.selected_player = player
        profile_id = int(player["profile_id"])
        leaderboard = self.mode_box.currentData()
        name = player.get("name", "Unknown")

        self.autocomplete_timer.stop()
        self.autocomplete_request_id += 1
        self.search_input.blockSignals(True)
        self.search_input.setText(name)
        self.search_input.blockSignals(False)
        self.player_header.setText(f"{name} 分析中...")
        self.output.setText("正在读取最近对局和排行榜数据...")
        self.run_worker(
            self.load_analysis,
            self.handle_analysis_result,
            f"正在分析 {name}...",
            profile_id,
            leaderboard,
        )

    def load_analysis(self, profile_id: int, leaderboard: str) -> dict[str, Any]:
        leaderboard = self.normalize_analysis_leaderboard(leaderboard)
        games = self.client.get_player_games(profile_id, leaderboard=leaderboard, limit=50)
        leaderboard_warning = None
        try:
            leaderboard_data = self.client.get_leaderboard_entry(profile_id, leaderboard=leaderboard)
        except Aoe4ApiError as exc:
            leaderboard_data = {"players": []}
            leaderboard_warning = str(exc)
        analysis = analyze_player_style(
            profile_id,
            games,
            leaderboard_data,
            leaderboard=leaderboard,
        )
        return {
            "profile_id": profile_id,
            "leaderboard": leaderboard,
            "analysis": analysis,
            "leaderboard_data": leaderboard_data,
            "leaderboard_warning": leaderboard_warning,
        }

    def normalize_analysis_leaderboard(self, leaderboard: str) -> str:
        allowed = set(LEADERBOARD_LABELS)
        if leaderboard in allowed:
            return leaderboard
        if leaderboard == "rm_1v1":
            return "rm_solo"
        if leaderboard.startswith("rm_"):
            return "rm_team"
        return "rm_solo"

    def handle_analysis_result(self, payload: dict[str, Any]) -> None:
        analysis = payload["analysis"]
        leaderboard = payload["leaderboard"]
        leaderboard_warning = payload.get("leaderboard_warning")
        name = "Unknown"
        if self.selected_player:
            name = self.selected_player.get("name", "Unknown")

        leaderboard_info = analysis.get("leaderboard", {})
        rank = leaderboard_info.get("rank")
        rank_level = leaderboard_info.get("rank_level_cn") or (
            translate_term(leaderboard_info.get("rank_level"), "rank_levels")
            if leaderboard_info.get("rank_level")
            else "-"
        )

        self.player_header.setText(f"{name} | {LEADERBOARD_LABELS.get(leaderboard, leaderboard)}")
        self.metric_rating.set_value(leaderboard_info.get("rating"))
        self.metric_rank.set_value(f"#{rank} / {rank_level}" if rank else rank_level)
        self.metric_recent_wr.set_value(f"{analysis['recent_win_rate']}%")
        self.metric_last10_wr.set_value(
            "-" if analysis["last_10_win_rate"] is None else f"{analysis['last_10_win_rate']}%"
        )
        self.metric_games.set_value(analysis["recent_games"])
        self.metric_duration.set_value(
            "-" if analysis["avg_duration"] is None else f"{analysis['avg_duration']} 分钟"
        )

        tags = analysis.get("tags") or []
        self.tags_label.setText("风格标签：" + (" / ".join(tags) if tags else "-"))
        self.output.setText(
            self.format_analysis_text(
                analysis,
                leaderboard_info,
                leaderboard_warning=leaderboard_warning,
            )
        )

    def format_analysis_text(
        self,
        analysis: dict[str, Any],
        leaderboard_info: dict[str, Any],
        leaderboard_warning: str | None = None,
    ) -> str:
        lines: list[str] = []
        if leaderboard_info:
            lines.append("当前排行榜")
            lines.append(f"- 当前分数: {leaderboard_info.get('rating', '-')}")
            lines.append(f"- 最高分数: {leaderboard_info.get('max_rating', '-')}")
            lines.append(
                f"- 段位: {leaderboard_info.get('rank_level_cn') or translate_term(leaderboard_info.get('rank_level'), 'rank_levels')}"
            )
            lines.append(f"- 总场次: {leaderboard_info.get('games_count', '-')}")
            lines.append(f"- 总胜率: {leaderboard_info.get('win_rate', '-')}%")
            lines.append("")
        elif leaderboard_warning:
            lines.append("当前排行榜")
            lines.append("- 当前模式没有可用排行榜数据，但最近对局分析仍会显示。")
            lines.append("")

        lines.append("最近表现")
        mode_label = LEADERBOARD_LABELS.get(analysis.get("requested_leaderboard"), analysis.get("requested_leaderboard") or "-")
        lines.append(f"- 当前统计模式: {mode_label}")
        if analysis.get("filtered_out_games", 0) > 0:
            lines.append(f"- 已排除其他模式对局: {analysis['filtered_out_games']} 局")
        if analysis.get("excluded_short_games", 0) > 0:
            min_minutes = analysis.get("min_analyzable_game_minutes", 3)
            lines.append(f"- 已排除少于 {min_minutes:g} 分钟的无参考对局: {analysis['excluded_short_games']} 局")
        lines.append(f"- 统计局数: {analysis['recent_games']}")
        lines.append(f"- 最近胜率: {analysis['recent_win_rate']}%")
        if analysis.get("effective_win_rate") is not None:
            lines.append(
                f"- 排除极短失败后的有效胜率: {analysis['effective_win_rate']}%"
                f"（有效样本 {analysis.get('effective_games', 0)} 局）"
            )
        if analysis["last_10_win_rate"] is not None:
            lines.append(f"- 最近 10 局胜率: {analysis['last_10_win_rate']}%")
        if analysis["avg_duration"] is not None:
            lines.append(f"- 平均对局时长: {analysis['avg_duration']} 分钟")
        lines.append("")

        style_profile = analysis.get("style_profile") or {}
        if style_profile:
            lines.append("玩家风格画像")
            lines.append(style_profile.get("overall", "暂无明确风格画像。"))
            for title, key in [
                ("发育运营", "economy"),
                ("跑马/机动骚扰", "cavalry"),
                ("主要开战时代", "fight_timing"),
            ]:
                section = style_profile.get(key) or {}
                if not section:
                    continue
                lines.append(
                    f"- {title}: {section.get('label', '-')}，可信度：{section.get('confidence', '-')}"
                )
                for evidence in section.get("evidence", [])[:3]:
                    lines.append(f"  · {evidence}")
            lines.append("")

        behavior_risk = analysis.get("behavior_risk") or {}
        if behavior_risk:
            lines.append("异常短局 / 疑似炸鱼")
            lines.append(
                f"- {behavior_risk.get('label', '-')}，可信度：{behavior_risk.get('confidence', '-')}"
            )
            for evidence in behavior_risk.get("evidence", [])[:3]:
                lines.append(f"  · {evidence}")
            lines.append("")

        relation_pattern = analysis.get("relation_pattern") or {}
        if relation_pattern:
            lines.append("上分 / 掉分搭档")
            lines.append(
                f"- {relation_pattern.get('label', '-')}，可信度：{relation_pattern.get('confidence', '-')}"
            )
            for evidence in relation_pattern.get("evidence", [])[:4]:
                lines.append(f"  · {evidence}")
            rank_up_partners = relation_pattern.get("rank_up_partners") or relation_pattern.get("serious_partners") or []
            if rank_up_partners:
                lines.append("  · 上分搭档候选：")
                for partner in rank_up_partners[:3]:
                    lines.append(
                        f"    - {partner.get('name', '-')}: "
                        f"{partner.get('analyzable_games', 0)} 局，"
                        f"胜率 {partner.get('analyzable_win_rate', '-')}%，"
                        f"平均 {partner.get('avg_duration', '-')} 分钟"
                    )
            rank_down_partners = relation_pattern.get("rank_down_partners") or relation_pattern.get("short_loss_partners") or []
            if rank_down_partners:
                lines.append("  · 掉分搭档候选：")
                for partner in rank_down_partners[:3]:
                    lines.append(
                        f"    - {partner.get('name', '-')}: "
                        f"{partner.get('invalid_short_losses', 0)} 局少于 3 分钟失败，"
                        f"占比 {partner.get('short_loss_rate', '-')}%"
                    )
            lines.append("")

        account_profile = analysis.get("account_profile") or {}
        if account_profile:
            lines.append("账号类型 / 小号风险")
            lines.append(
                f"- {account_profile.get('label', '-')}，可信度：{account_profile.get('confidence', '-')}"
            )
            for evidence in account_profile.get("evidence", [])[:5]:
                lines.append(f"  · {evidence}")
            lines.append("")

        lines.append("常用文明")
        main_civs = analysis.get("main_civs", [])
        if main_civs:
            for civ in main_civs:
                lines.append(
                    f"- {civ['civ']}: {civ['games']} 局，"
                    f"使用率 {civ['pick_rate']}%，胜率 {civ['win_rate']}%"
                )
        else:
            lines.append("- 暂无文明数据")
        lines.append("")

        lines.append("常见地图")
        top_maps = analysis.get("top_maps", [])
        if top_maps:
            for map_info in top_maps:
                lines.append(
                    f"- {map_info['map']}: {map_info['games']} 局，"
                    f"出现率 {map_info['pick_rate']}%，胜率 {map_info['win_rate']}%"
                )
        else:
            lines.append("- 暂无地图数据")
        lines.append("")

        lines.append("风格总结")
        lines.append(analysis["summary"])
        lines.append("")
        lines.append("说明：这是基于公开对局元数据的规则推断，不会编造封建时间、开局路线、TC 数量等公开接口未提供的数据。")
        return "\n".join(lines)

    def clear_cache(self) -> None:
        self.client.cache.clear()
        QMessageBox.information(self, "缓存已清除", "本地 API 缓存已经清除。")

    def handle_error(self, message: str) -> None:
        QMessageBox.critical(self, "错误", message)
        self.status_label.setText("请求失败")
        self.player_header.setText("加载失败")
        self.output.setText(
            "加载玩家数据失败。\n\n"
            f"{message}\n\n"
            "可以尝试：\n"
            "- 切换到“天梯单排”或“天梯组队”\n"
            "- 点击“清除缓存”后重试\n"
            "- 确认当前网络能访问 aoe4world.com"
        )


def main() -> int:
    app = QApplication(sys.argv)
    window = AoE4AnalyzerWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

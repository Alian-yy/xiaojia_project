# ui/pages/subscriber_page.py
"""
订阅界面 - B同学负责开发
"""

import json
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit,
    QPushButton, QTextEdit, QListWidget, QListWidgetItem, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, pyqtSignal

from .base_page import BasePage
from subscriber.subscriber_logic import SubscriberLogic
from subscriber.location_widget import LocationWidget
from subscriber.xiaojia_display import XiaojiaDisplay
from ui.widgets.data_card import MiniCard, StatusCard
from ui.widgets.chart_widget import LineChart
from ui.widgets.map_widget import MapWidget


class SubscriberPage(BasePage):
    """订阅界面"""

    message_received = pyqtSignal(dict)
    connection_changed = pyqtSignal(bool)

    def init_ui(self):
        """初始化UI"""
        # 逻辑
        self.logic = SubscriberLogic()
        self.logic.set_on_message(self._emit_message)
        self.logic.set_on_connection(self._emit_connection)

        self.message_received.connect(self._on_message)
        self.connection_changed.connect(self._on_connection)

        self.msg_count = 0
        self.recent_values = []

        # 标题
        self.content_layout.addWidget(
            self.create_section_title("数据订阅", "📥")
        )

        # 顶部状态卡
        status_row = self.create_row_layout()
        self.status_card = StatusCard("MQTT 状态", "未连接", "offline", "🛰️")
        self.count_card = MiniCard("已接收", "0", "", True)
        self.subs_card = MiniCard("订阅主题数", "0", "", True)
        status_row.addWidget(self.status_card)
        status_row.addWidget(self.count_card)
        status_row.addWidget(self.subs_card)
        self.content_layout.addLayout(status_row)

        # 控制区
        control_panel, control_layout = self.create_panel("订阅控制", "🪢")
        ctrl_row = self.create_row_layout()
        self.topic_input = QLineEdit("sensor/#")
        self.topic_input.setPlaceholderText("输入要订阅的Topic，例如 sensor/#")
        self.btn_sub = QPushButton("订阅")
        self.btn_unsub = QPushButton("取消订阅")
        self.btn_clear = QPushButton("清空日志")

        self.btn_sub.clicked.connect(self._on_subscribe_clicked)
        self.btn_unsub.clicked.connect(self._on_unsubscribe_clicked)
        self.btn_clear.clicked.connect(self._clear_logs)

        ctrl_row.addWidget(self.topic_input, 3)
        ctrl_row.addWidget(self.btn_sub)
        ctrl_row.addWidget(self.btn_unsub)
        ctrl_row.addWidget(self.btn_clear)
        control_layout.addLayout(ctrl_row)

        # 地图 + 信息 + 订阅列表（左右布局，左侧大地图）
        side_row = self.create_row_layout()

        # 左：地图
        map_panel, map_layout = self.create_panel("传感器地图", "🗺️")
        map_layout.setContentsMargins(5, 5, 5, 5)
        self.map_widget = MapWidget()
        self.map_widget.setSizePolicy(self.map_widget.sizePolicy().Expanding, self.map_widget.sizePolicy().Expanding)
        map_layout.addWidget(self.map_widget)
        side_row.addWidget(map_panel, 3)

        # 右：信息 + 订阅列表
        right_col = QVBoxLayout()
        right_col.setSpacing(10)
        info_panel, info_layout = self.create_panel("位置与播报", "🤖")
        self.loc_widget = LocationWidget()
        self.loc_widget.set_location("JX_Teach", "教学楼A", "本地模拟")
        self.xiaojia = XiaojiaDisplay()
        info_layout.addWidget(self.loc_widget)
        info_layout.addWidget(self.xiaojia)
        right_col.addWidget(info_panel)

        sub_panel, sub_layout = self.create_panel("订阅列表", "🧭")
        self.sub_list = QListWidget()
        sub_layout.addWidget(self.sub_list)
        right_col.addWidget(sub_panel)

        side_row.addLayout(right_col, 1)

        control_layout.addLayout(side_row)
        self.content_layout.addWidget(control_panel)

        # 消息表 + 日志 + 趋势
        main_panel, main_layout = self.create_panel("消息与趋势", "📑")
        main_row = self.create_row_layout()

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["时间", "Topic", "类型", "数值", "位置"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(self.table.NoEditTriggers)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("消息 JSON 原文...")

        self.chart = LineChart("最近数值趋势")

        table_panel = QFrame()
        tp_layout = QVBoxLayout(table_panel)
        tp_layout.setContentsMargins(0, 0, 0, 0)
        tp_layout.addWidget(self.table)
        tp_layout.addWidget(self.log)

        main_row.addWidget(table_panel, 2)
        main_row.addWidget(self.chart, 1)

        main_layout.addLayout(main_row)
        self.content_layout.addWidget(main_panel)
        self.content_layout.addStretch()

        # 初始连接并订阅默认主题
        self.logic.connect()
        self.logic.subscribe("sensor/#")
        self._refresh_sub_list()
        self.send_status("✅ 订阅端已连接，本地 broker 127.0.0.1:1883")

    # -------- UI 事件 --------
    def _on_subscribe_clicked(self):
        topic = self.topic_input.text().strip()
        if not topic:
            self.send_status("⚠️ 请输入 Topic")
            return
        ok = self.logic.subscribe(topic)
        if ok:
            self._refresh_sub_list()
            self.send_status(f"✅ 已订阅: {topic}")
        else:
            self.send_status("⚠️ Topic 不合法或订阅失败，请检查通配符位置", "warning")

    def _on_unsubscribe_clicked(self):
        topic = self.topic_input.text().strip()
        if not topic:
            self.send_status("⚠️ 请输入要取消的 Topic")
            return
        self.logic.unsubscribe(topic)
        self._refresh_sub_list()
        self.send_status(f"ℹ️ 已取消订阅: {topic}")

    def _clear_logs(self):
        self.table.setRowCount(0)
        self.log.clear()
        self.chart.clear_data()
        self.msg_count = 0
        self.recent_values.clear()
        self._update_cards()

    # -------- 信号桥接 --------
    def _emit_message(self, data: dict):
        self.message_received.emit(data)

    def _emit_connection(self, connected: bool):
        self.connection_changed.emit(connected)

    # -------- 槽函数 --------
    def _on_connection(self, connected: bool):
        if connected:
            self.status_card.set_status("已连接", "online")
            self.send_status("✅ MQTT 已连接")
        else:
            self.status_card.set_status("已断开", "offline")
            self.send_status("⚠️ MQTT 断开")

    def _on_message(self, data: dict):
        self.msg_count += 1
        self._update_cards()

        ts = data.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        topic = data.get("topic", "-")
        val = data.get("value", data.get("payload", "-"))
        dtype = data.get("type", "-")
        loc = data.get("location", "-")
        sensor_id = data.get("sensor_id", "-")

        self._append_table(ts, topic, dtype, val, loc)
        self._append_log(data)
        self._update_chart(val)
        self._update_xiaojia(dtype, val, loc, sensor_id)

    # -------- 辅助 --------
    def _append_table(self, ts, topic, dtype, val, loc):
        row = self.table.rowCount()
        self.table.insertRow(row)
        for col, content in enumerate([ts, topic, str(dtype), str(val), str(loc)]):
            item = QTableWidgetItem(content)
            self.table.setItem(row, col, item)
        self.table.scrollToBottom()

    def _append_log(self, data: dict):
        try:
            text = json.dumps(data, ensure_ascii=False)
        except Exception:
            text = str(data)
        self.log.append(text)

    def _update_chart(self, val):
        try:
            num = float(val)
        except Exception:
            return
        self.recent_values.append(num)
        if len(self.recent_values) > 50:
            self.recent_values.pop(0)
        self.chart.set_data(self.recent_values)

    def _update_xiaojia(self, dtype, val, loc, sensor_id):
        mood = "normal"
        tip = f"来自 {loc or '未知位置'} 的 {dtype or '数据'}: {val}"
        status_for_map = "normal"
        try:
            num = float(val)
            if dtype == "temperature" and num >= 30:
                mood, tip = "hot", f"{loc or '此处'}有点热 ({num}℃)，注意通风降温。"
                status_for_map = "warning"
            elif dtype == "humidity" and num >= 80:
                mood, tip = "humid", f"{loc or '此处'}偏湿 ({num}%RH)，注意防潮。"
                status_for_map = "warning"
            elif dtype == "temperature" and num <= 5:
                mood, tip = "cold", f"{loc or '此处'}偏冷 ({num}℃)，注意保暖。"
                status_for_map = "warning"
            elif dtype == "pressure" and num < 990:
                status_for_map = "error"
            elif dtype == "pressure" and num > 1030:
                status_for_map = "warning"
        except Exception:
            pass
        self.xiaojia.set_tip(tip, mood)
        # 更新位置/地图标记
        if loc or sensor_id:
            self.map_widget.update_marker(sensor_id, loc, status_for_map)
        if loc:
            self.loc_widget.set_location(sensor_id or "-", loc, "实时更新")

    def _update_cards(self):
        self.count_card.set_value(str(self.msg_count))
        self.subs_card.set_value(str(len(self.logic.list_subscriptions())))

    def _refresh_sub_list(self):
        self.sub_list.clear()
        for t in self.logic.list_subscriptions():
            QListWidgetItem(t, self.sub_list)
        self._update_cards()

    def refresh_data(self):
        """刷新数据"""
        self.send_status("订阅页面已刷新")

    def cleanup(self):
        self.logic.disconnect()

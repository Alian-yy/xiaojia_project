# ui/pages/subscriber_page.py
"""
订阅界面 - B同学负责开发
"""

import json
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QCheckBox, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor

from .base_page import BasePage
from subscriber.subscriber_logic import SubscriberLogic
from subscriber.location_widget import LocationWidget
from subscriber.xiaojia_display import XiaojiaDisplay
from ui.widgets.data_card import MiniCard, StatusCard, DataCard
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
        
        # 存储三类数据的历史值
        self.data_history = {
            "temperature": [],
            "humidity": [],
            "pressure": []
        }
        
        # 存储当前最新值
        self.current_values = {
            "temperature": None,
            "humidity": None,
            "pressure": None
        }
        
        # 设置定期检测连接状态的定时器（每3秒检测一次）
        self.connection_check_timer = QTimer()
        self.connection_check_timer.timeout.connect(self._check_connection_status)
        self.connection_check_timer.start(3000)  # 每3秒检测一次

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
        
        # 主题选择区域
        topic_group = QGroupBox("选择订阅主题")
        topic_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #1a4a7a;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #00d4ff;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        topic_layout = QHBoxLayout(topic_group)
        topic_layout.setSpacing(20)
        
        # 定义可订阅的主题
        self.topic_configs = {
            "temperature": {
                "label": "🌡️ 温度",
                "topic": "sensor/temperature",
                "checkbox": None
            },
            "humidity": {
                "label": "💧 湿度",
                "topic": "sensor/humidity",
                "checkbox": None
            },
            "pressure": {
                "label": "📊 气压",
                "topic": "sensor/pressure",
                "checkbox": None
            }
        }
        
        # 创建复选框
        for key, config in self.topic_configs.items():
            checkbox = QCheckBox(config["label"])
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: #dfe9f5;
                    font-size: 13px;
                    spacing: 8px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border: 2px solid #1a4a7a;
                    border-radius: 3px;
                    background: rgba(10, 30, 60, 0.8);
                }
                QCheckBox::indicator:hover {
                    border: 2px solid #00d4ff;
                }
                QCheckBox::indicator:checked {
                    background: qlineargradient(
                        x1:0, y1:0, x2:0, y2:1,
                        stop:0 #00a0cc,
                        stop:1 #0080aa
                    );
                    border: 2px solid #00d4ff;
                }
                QCheckBox::indicator:checked::after {
                    content: "✓";
                    color: white;
                }
            """)
            checkbox.stateChanged.connect(lambda state, t=config["topic"]: self._on_topic_checkbox_changed(t, state))
            config["checkbox"] = checkbox
            topic_layout.addWidget(checkbox)
        
        topic_layout.addStretch()
        control_layout.addWidget(topic_group)
        
        # 操作按钮行
        btn_row = self.create_row_layout()
        self.btn_clear = QPushButton("清空数据")
        self.btn_clear.clicked.connect(self._clear_data)
        btn_row.addWidget(self.btn_clear)
        btn_row.addStretch()
        control_layout.addLayout(btn_row)

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
        sub_list_layout = QVBoxLayout()
        sub_list_layout.setContentsMargins(0, 0, 0, 0)
        
        self.sub_list = QListWidget()
        self.sub_list.setStyleSheet("""
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #1a3a5c;
            }
            QListWidget::item:hover {
                background: rgba(0, 200, 255, 0.1);
            }
        """)
        self.sub_list.itemDoubleClicked.connect(self._on_sub_list_double_clicked)
        
        sub_list_layout.addWidget(self.sub_list)
        
        # 添加取消订阅提示
        hint_label = QLabel("💡 双击列表项可取消订阅")
        hint_label.setStyleSheet("color: #5588aa; font-size: 11px; padding: 5px;")
        hint_label.setAlignment(Qt.AlignCenter)
        sub_list_layout.addWidget(hint_label)
        
        sub_layout.addLayout(sub_list_layout)
        right_col.addWidget(sub_panel)

        side_row.addLayout(right_col, 1)

        control_layout.addLayout(side_row)
        self.content_layout.addWidget(control_panel)

        # 三类数据面板（上下排列）
        self.data_panels = {}
        data_panels_container = QVBoxLayout()
        data_panels_container.setSpacing(15)
        
        # 创建三个数据面板
        for dtype, config in self.topic_configs.items():
            panel_dict = self._create_data_panel(dtype, config["label"])
            self.data_panels[dtype] = panel_dict
            # 添加面板widget到布局
            data_panels_container.addWidget(panel_dict["panel"])
        
        # 将数据面板容器添加到内容布局
        data_container_widget = QWidget()
        data_container_widget.setLayout(data_panels_container)
        self.content_layout.addWidget(data_container_widget)
        self.content_layout.addStretch()

        # 初始状态：尝试自动连接broker（如果broker可用）
        # 这样当发布端已连接时，订阅端也能显示连接状态
        self._refresh_sub_list()
        # 尝试连接broker（异步，连接结果会通过回调更新状态）
        self.logic.connect()
        self.send_status("ℹ️ 订阅端已就绪，正在检测MQTT Broker...")

    # -------- UI 事件 --------
    def _create_data_panel(self, dtype: str, label: str):
        """创建数据面板（数据展示 + 趋势图）"""
        panel, panel_layout = self.create_panel(label, self.topic_configs[dtype]["label"].split()[0])
        
        # 内容布局（水平：左侧数据卡片，右侧趋势图）
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        # 左侧：数据展示卡片
        unit_map = {
            "temperature": "°C",
            "humidity": "%RH",
            "pressure": "hPa"
        }
        data_card = DataCard(
            label,
            "--",
            unit_map.get(dtype, ""),
            self.topic_configs[dtype]["label"].split()[0],
            "normal"
        )
        data_card.setMinimumWidth(250)
        
        # 右侧：趋势图
        chart = LineChart(f"{label}趋势")
        chart.setMinimumHeight(200)
        
        # 根据数据类型设置图表颜色
        color_map = {
            "temperature": "#ff8800",  # 橙色
            "humidity": "#6496ff",     # 蓝色
            "pressure": "#00d4ff"      # 青色
        }
        chart.set_line_color(QColor(color_map.get(dtype, "#00d4ff")))
        
        content_layout.addWidget(data_card, 1)
        content_layout.addWidget(chart, 2)
        
        panel_layout.addLayout(content_layout)
        
        # 初始状态：隐藏（未订阅时）
        panel.setVisible(False)
        
        return {
            "panel": panel,
            "card": data_card,
            "chart": chart
        }
    
    def _on_topic_checkbox_changed(self, topic: str, state: int):
        """当复选框状态改变时，自动订阅或取消订阅"""
        is_checked = (state == Qt.Checked)
        
        # 找到对应的数据类型
        dtype = None
        for key, config in self.topic_configs.items():
            if config["topic"] == topic:
                dtype = key
                break
        
        if is_checked:
            # 订阅主题（会自动尝试连接）
            ok = self.logic.subscribe(topic)
            if ok:
                self._refresh_sub_list()
                # 显示对应的数据面板
                if dtype and dtype in self.data_panels:
                    self.data_panels[dtype]["panel"].setVisible(True)
                self.send_status(f"✅ 已订阅: {topic}")
            else:
                # 订阅失败，取消复选框勾选
                for config in self.topic_configs.values():
                    if config["topic"] == topic:
                        config["checkbox"].blockSignals(True)
                        config["checkbox"].setChecked(False)
                        config["checkbox"].blockSignals(False)
                        break
                self.send_status(f"⚠️ 订阅失败: {topic}，请检查MQTT Broker是否运行", "warning")
        else:
            # 取消订阅
            self.logic.unsubscribe(topic)
            self._refresh_sub_list()
            # 隐藏对应的数据面板
            if dtype and dtype in self.data_panels:
                self.data_panels[dtype]["panel"].setVisible(False)
                # 清空该类型的数据
                self.data_history[dtype].clear()
                self.current_values[dtype] = None
                self.data_panels[dtype]["card"].set_value("--")
                self.data_panels[dtype]["chart"].clear_data()
            self.send_status(f"ℹ️ 已取消订阅: {topic}")
    
    def _on_sub_list_double_clicked(self, item: QListWidgetItem):
        """双击列表项取消订阅"""
        # 从列表项文本中提取topic（格式：📌 sensor/temperature）
        item_text = item.text()
        # 移除图标和空格，提取实际的topic
        topic = item_text.replace("📌", "").strip()
        
        # 取消订阅
        self.logic.unsubscribe(topic)
        # 更新对应的复选框状态
        for config in self.topic_configs.values():
            if config["topic"] == topic:
                config["checkbox"].blockSignals(True)
                config["checkbox"].setChecked(False)
                config["checkbox"].blockSignals(False)
                break
        self._refresh_sub_list()
        self.send_status(f"ℹ️ 已取消订阅: {topic}")

    def _clear_data(self):
        """清空所有数据"""
        self.msg_count = 0
        for dtype in ["temperature", "humidity", "pressure"]:
            self.data_history[dtype].clear()
            self.current_values[dtype] = None
            if dtype in self.data_panels:
                self.data_panels[dtype]["card"].set_value("--")
                self.data_panels[dtype]["chart"].clear_data()
        self._update_cards()
        self.send_status("✅ 已清空所有数据")

    # -------- 信号桥接 --------
    def _emit_message(self, data: dict):
        self.message_received.emit(data)

    def _emit_connection(self, connected: bool):
        self.connection_changed.emit(connected)

    # -------- 槽函数 --------
    def _on_connection(self, connected: bool):
        """连接状态变化 - 与发布界面保持一致"""
        if connected:
            self.status_card.set_status("已连接", "online")
            self.send_status("✅ 已连接到 MQTT Broker")
        else:
            self.status_card.set_status("未连接", "offline")
            self.send_status("❌ 已断开连接")

    def _on_message(self, data: dict):
        self.msg_count += 1
        self._update_cards()

        val = data.get("value", data.get("payload", "-"))
        dtype = data.get("type", "-")
        loc = data.get("location", "-")
        sensor_id = data.get("sensor_id", "-")

        # 更新对应类型的数据面板
        if dtype in ["temperature", "humidity", "pressure"]:
            try:
                num_val = float(val)
                self._update_data_panel(dtype, num_val)
            except (ValueError, TypeError):
                pass
        
        self._update_xiaojia(dtype, val, loc, sensor_id)

    # -------- 辅助 --------
    def _update_data_panel(self, dtype: str, value: float):
        """更新指定类型的数据面板"""
        if dtype not in self.data_panels:
            return
        
        # 更新当前值
        self.current_values[dtype] = value
        
        # 更新历史数据（最多保留50个点）
        self.data_history[dtype].append(value)
        if len(self.data_history[dtype]) > 50:
            self.data_history[dtype].pop(0)
        
        # 更新数据卡片
        panel = self.data_panels[dtype]
        panel["card"].set_value(f"{value:.1f}")
        
        # 更新趋势图
        panel["chart"].set_data(self.data_history[dtype])
        
        # 根据数值设置状态
        status = "normal"
        if dtype == "temperature":
            if value >= 30:
                status = "warning"
            elif value <= 5:
                status = "warning"
        elif dtype == "humidity":
            if value >= 80:
                status = "warning"
        elif dtype == "pressure":
            if value < 990 or value > 1030:
                status = "warning"
        
        panel["card"].set_status(status)

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
        """刷新订阅列表，并同步更新复选框状态和数据面板显示"""
        self.sub_list.clear()
        subscribed_topics = set(self.logic.list_subscriptions())
        
        # 更新列表
        for t in sorted(subscribed_topics):
            item = QListWidgetItem(f"📌 {t}")
            item.setToolTip("双击取消订阅")
            self.sub_list.addItem(item)
        
        # 同步更新复选框状态和数据面板显示
        for dtype, config in self.topic_configs.items():
            topic = config["topic"]
            checkbox = config["checkbox"]
            is_subscribed = topic in subscribed_topics
            
            checkbox.blockSignals(True)
            checkbox.setChecked(is_subscribed)
            checkbox.blockSignals(False)
            
            # 显示/隐藏对应的数据面板
            if dtype in self.data_panels:
                self.data_panels[dtype]["panel"].setVisible(is_subscribed)
        
        self._update_cards()

    def refresh_data(self):
        """刷新数据"""
        # 刷新时也检测连接状态
        self._check_connection_status()
        self.send_status("订阅页面已刷新")
    
    def _check_connection_status(self):
        """定期检测MQTT连接状态，如果未连接则尝试连接"""
        # 如果当前未连接，尝试连接broker（这样当broker可用时能自动连接）
        # 这样当发布端连接broker后，订阅端也能自动检测并连接
        if not self.logic.is_connected():
            try:
                self.logic.connect()
            except Exception:
                pass

    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'connection_check_timer'):
            self.connection_check_timer.stop()
        self.logic.disconnect()

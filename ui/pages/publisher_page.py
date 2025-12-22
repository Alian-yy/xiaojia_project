# ui/pages/publisher_page.py
"""
发布界面 - A同学负责开发
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit,
    QPushButton, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox,
    QProgressBar
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer

from .base_page import BasePage
from publisher.publish_logic import PublisherLogic
from ui.widgets.data_card import MiniCard, StatusCard


class PublisherPage(BasePage):
    """发布界面"""

    message_published = pyqtSignal(str, dict)
    connection_changed = pyqtSignal(bool)

    def init_ui(self):
        """初始化UI"""
        # 逻辑
        self.logic = PublisherLogic()
        self.logic.set_on_message(self._emit_message)
        self.logic.set_on_connection(self._emit_connection)
        self.logic.set_on_publish_complete(self._on_publish_complete)

        self.message_published.connect(self._on_message_published)
        self.connection_changed.connect(self._on_connection_changed)

        self.pub_count = 0
        self.is_publishing = False

        # 标题
        self.content_layout.addWidget(
            self.create_section_title("消息发布", "📤")
        )

        # 顶部状态卡
        status_row = self.create_row_layout()
        self.status_card = StatusCard("MQTT 状态", "未连接", "offline", "🛰️")
        self.count_card = MiniCard("已发布", "0", "", True)
        self.file_card = MiniCard("数据文件", "3 个", "", True)
        status_row.addWidget(self.status_card)
        status_row.addWidget(self.count_card)
        status_row.addWidget(self.file_card)
        self.content_layout.addLayout(status_row)

        # 连接配置面板
        conn_panel, conn_layout = self.create_panel("连接配置", "🔌")
        
        # Broker 设置
        broker_row = self.create_row_layout()
        broker_label = QLabel("Broker:")
        broker_label.setMinimumWidth(60)
        broker_row.addWidget(broker_label)
        self.broker_input = QLineEdit("127.0.0.1")
        self.broker_input.setPlaceholderText("输入MQTT Broker地址")
        self.broker_input.setStyleSheet("""
            QLineEdit {
                padding: 6px 10px;
                font-size: 13px;
            }
        """)
        broker_row.addWidget(self.broker_input, 2)
        
        port_label = QLabel("端口:")
        port_label.setMinimumWidth(40)
        broker_row.addWidget(port_label)
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(1883)
        self.port_input.setMinimumWidth(80)
        broker_row.addWidget(self.port_input)
        
        # 连接按钮组
        btn_group = QHBoxLayout()
        btn_group.setSpacing(8)
        self.btn_connect = QPushButton("🔗 连接")
        self.btn_connect.setMinimumWidth(100)
        self.btn_connect.setStyleSheet("""
            QPushButton {
                padding: 10px 18px;
                font-size: 13px;
                font-weight: bold;
                color: #0c1729;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7ce7ff,
                    stop:1 #3cc5ff);
                border: 2px solid #4fd4ff;
                border-radius: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #9bf0ff,
                    stop:1 #56d6ff);
                border-color: #7ce7ff;
            }
            QPushButton:disabled {
                color: #6f7b91;
                background: #1e2f4a;
                border-color: #2c456a;
            }
        """)
        self.btn_disconnect = QPushButton("🔌 断开")
        self.btn_disconnect.setMinimumWidth(100)
        self.btn_disconnect.setEnabled(False)
        self.btn_disconnect.setStyleSheet("""
            QPushButton {
                padding: 10px 18px;
                font-size: 13px;
                font-weight: bold;
                color: #ffecec;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff6b6b,
                    stop:1 #d83c3c);
                border: 2px solid #ff8a8a;
                border-radius: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff8a8a,
                    stop:1 #e34f4f);
                border-color: #ffc1c1;
            }
            QPushButton:disabled {
                color: #7f6f6f;
                background: #2d2222;
                border-color: #3c2e2e;
            }
        """)
        
        self.btn_connect.clicked.connect(self._on_connect_clicked)
        self.btn_disconnect.clicked.connect(self._on_disconnect_clicked)
        
        btn_group.addWidget(self.btn_connect)
        btn_group.addWidget(self.btn_disconnect)
        broker_row.addLayout(btn_group)
        conn_layout.addLayout(broker_row)
        
        self.content_layout.addWidget(conn_panel)

        # 传感器配置面板
        sensor_panel, sensor_layout = self.create_panel("传感器配置", "📍")
        
        sensor_row1 = self.create_row_layout()
        id_label = QLabel("传感器ID:")
        id_label.setMinimumWidth(70)
        sensor_row1.addWidget(id_label)
        self.sensor_id_input = QLineEdit("JX_Teach_01")
        self.sensor_id_input.setPlaceholderText("例如: JX_Teach_01")
        self.sensor_id_input.setStyleSheet("padding: 6px 10px; font-size: 13px;")
        sensor_row1.addWidget(self.sensor_id_input, 2)
        
        loc_label = QLabel("位置:")
        loc_label.setMinimumWidth(50)
        sensor_row1.addWidget(loc_label)
        self.location_input = QLineEdit("教学楼A")
        self.location_input.setPlaceholderText("例如: 教学楼A")
        self.location_input.setStyleSheet("padding: 6px 10px; font-size: 13px;")
        sensor_row1.addWidget(self.location_input, 2)
        sensor_layout.addLayout(sensor_row1)
        
        sensor_row2 = self.create_row_layout()
        extra_label = QLabel("备注:")
        extra_label.setMinimumWidth(70)
        sensor_row2.addWidget(extra_label)
        self.extra_input = QLineEdit("三楼301教室")
        self.extra_input.setPlaceholderText("例如: 三楼301教室")
        self.extra_input.setStyleSheet("padding: 6px 10px; font-size: 13px;")
        sensor_row2.addWidget(self.extra_input)
        sensor_layout.addLayout(sensor_row2)
        
        self.content_layout.addWidget(sensor_panel)

        # 发布控制面板（左右布局）
        control_row = self.create_row_layout()
        
        # 左侧：从文件发布
        file_panel, file_layout = self.create_panel("从文件发布数据", "📁")
        
        interval_row = self.create_row_layout()
        interval_label = QLabel("发布间隔:")
        interval_label.setMinimumWidth(80)
        interval_row.addWidget(interval_label)
        self.interval_input = QDoubleSpinBox()
        self.interval_input.setRange(0.01, 10.0)
        self.interval_input.setValue(0.2)
        self.interval_input.setSuffix(" 秒")
        self.interval_input.setDecimals(2)
        self.interval_input.setMinimumWidth(100)
        self.interval_input.setStyleSheet("padding: 6px 10px; font-size: 13px;")
        interval_row.addWidget(self.interval_input)
        
        # 添加进度条显示发布进度
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #1a4a7a;
                border-radius: 4px;
                text-align: center;
                height: 20px;
                background: rgba(10, 30, 60, 0.8);
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00a0cc,
                    stop:1 #00d4ff
                );
                border-radius: 3px;
            }
        """)
        interval_row.addWidget(self.progress_bar, 1)
        file_layout.addLayout(interval_row)
        
        btn_row = self.create_row_layout()
        self.btn_start = QPushButton("🚀 开始发布")
        self.btn_start.setMinimumHeight(40)
        self.btn_start.setStyleSheet("""
            QPushButton {
                padding: 12px 22px;
                font-size: 14px;
                font-weight: bold;
                color: #0b1a2a;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #8df5c5,
                    stop:1 #3ddf9e);
                border: 2px solid #6ce6b4;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(61, 223, 158, 0.3);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #adf9d6,
                    stop:1 #5aecb4);
                border-color: #9cf7d0;
                box-shadow: 0 6px 14px rgba(92, 236, 180, 0.35);
            }
            QPushButton:disabled {
                color: #6e7b82;
                background: #1f2f35;
                border-color: #2f444c;
                box-shadow: none;
            }
        """)
        self.btn_stop = QPushButton("⏹ 停止发布")
        self.btn_stop.setMinimumHeight(40)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setStyleSheet("""
            QPushButton {
                padding: 12px 22px;
                font-size: 14px;
                font-weight: bold;
                color: #ffecec;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ff8c7a,
                    stop:1 #ff5263);
                border: 2px solid #ff8fa0;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(255, 92, 113, 0.35);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ff9f8f,
                    stop:1 #ff6f7f);
                border-color: #ffc0c9;
                box-shadow: 0 6px 14px rgba(255, 111, 127, 0.4);
            }
            QPushButton:disabled {
                color: #7f6f6f;
                background: #2d2222;
                border-color: #3c2e2e;
                box-shadow: none;
            }
        """)
        
        self.btn_start.clicked.connect(self._on_start_publish)
        self.btn_stop.clicked.connect(self._on_stop_publish)
        
        btn_row.addWidget(self.btn_start)
        btn_row.addWidget(self.btn_stop)
        file_layout.addLayout(btn_row)
        
        control_row.addWidget(file_panel, 1)
        
        # 右侧：手动发布单条
        manual_panel, manual_layout = self.create_panel("手动发布", "✍️")
        
        manual_row1 = self.create_row_layout()
        type_label = QLabel("数据类型:")
        type_label.setMinimumWidth(70)
        manual_row1.addWidget(type_label)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["temperature", "humidity", "pressure"])
        self.type_combo.setStyleSheet("padding: 6px 10px; font-size: 13px;")
        manual_row1.addWidget(self.type_combo)
        manual_layout.addLayout(manual_row1)
        
        manual_row2 = self.create_row_layout()
        value_label = QLabel("数值:")
        value_label.setMinimumWidth(70)
        manual_row2.addWidget(value_label)
        self.value_input = QDoubleSpinBox()
        self.value_input.setRange(-100, 200)
        self.value_input.setValue(25.0)
        self.value_input.setDecimals(1)
        self.value_input.setStyleSheet("padding: 6px 10px; font-size: 13px;")
        manual_row2.addWidget(self.value_input)
        manual_layout.addLayout(manual_row2)
        
        self.btn_publish = QPushButton("📤 发布消息")
        self.btn_publish.setMinimumHeight(40)
        self.btn_publish.setStyleSheet("""
            QPushButton {
                padding: 12px 22px;
                font-size: 14px;
                font-weight: bold;
                color: #e8f3ff;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3aa0ff,
                    stop:1 #1f6fff);
                border: 2px solid #5ab3ff;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(58, 160, 255, 0.35);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #62b6ff,
                    stop:1 #3685ff);
                border-color: #8dcaff;
                box-shadow: 0 6px 14px rgba(80, 181, 255, 0.4);
            }
            QPushButton:disabled {
                color: #7c889a;
                background: #1d2b45;
                border-color: #2d4166;
                box-shadow: none;
            }
        """)
        self.btn_publish.clicked.connect(self._on_publish_single)
        manual_layout.addWidget(self.btn_publish)
        
        control_row.addWidget(manual_panel, 1)
        
        self.content_layout.addLayout(control_row)

        # 发布日志
        log_panel, log_layout = self.create_panel("发布日志", "📝")
        
        log_controls = self.create_row_layout()
        self.btn_clear_log = QPushButton("清空日志")
        self.btn_clear_log.clicked.connect(self._clear_log)
        log_controls.addStretch()
        log_controls.addWidget(self.btn_clear_log)
        log_layout.addLayout(log_controls)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background: rgba(10, 30, 50, 0.8);
                color: #aaddff;
                border: 1px solid #1a4a7a;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                line-height: 1.4;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        # 日志更新防抖定时器
        self._log_buffer = []
        self._log_timer = QTimer()
        self._log_timer.setSingleShot(True)
        self._log_timer.timeout.connect(self._flush_log_buffer)
        
        self.content_layout.addWidget(log_panel)
        self.content_layout.addStretch()
        
        # 设置按钮动画（在所有控件创建后）
        self._setup_animations()

    def _emit_message(self, topic: str, payload: dict):
        """触发消息发送信号"""
        self.message_published.emit(topic, payload)

    def _emit_connection(self, connected: bool):
        """触发连接状态变化信号"""
        self.connection_changed.emit(connected)

    def _setup_animations(self):
        """设置按钮动画效果"""
        # 连接按钮动画
        self._connect_anim = QPropertyAnimation(self.btn_connect, b"geometry")
        self._connect_anim.setDuration(200)
        self._connect_anim.setEasingCurve(QEasingCurve.OutCubic)
    
    def _on_connect_clicked(self):
        """连接按钮点击"""
        broker = self.broker_input.text().strip()
        port = self.port_input.value()
        
        if not broker:
            self.send_status("⚠️ Broker地址不能为空", "error")
            # 输入框高亮提示
            self.broker_input.setStyleSheet("""
                QLineEdit {
                    padding: 6px 10px;
                    font-size: 13px;
                    border: 2px solid #ff5050;
                }
            """)
            QTimer.singleShot(2000, lambda: self.broker_input.setStyleSheet("padding: 6px 10px; font-size: 13px;"))
            return
        
        self.logic.broker = broker
        self.logic.port = port
        
        # 按钮动画反馈
        original_geom = self.btn_connect.geometry()
        self._connect_anim.setStartValue(original_geom)
        self._connect_anim.setEndValue(original_geom.adjusted(-2, -2, 2, 2))
        self._connect_anim.setKeyValueAt(0.5, original_geom.adjusted(-3, -3, 3, 3))
        self._connect_anim.start()
        
        if self.logic.connect():
            self.send_status(f"⏳ 正在连接到 {broker}:{port}...")
            self.btn_connect.setEnabled(False)
            self.btn_connect.setText("连接中...")
        else:
            self.send_status("❌ 连接失败，请检查Broker是否运行", "error")

    def _on_disconnect_clicked(self):
        """断开按钮点击"""
        self.logic.stop_publish()
        self.logic.disconnect()
        self.send_status("已断开连接")

    def _on_connection_changed(self, connected: bool):
        """连接状态变化"""
        if connected:
            self.status_card.set_status("已连接", "online")
            self.btn_connect.setEnabled(False)
            self.btn_connect.setText("🔗 已连接")
            self.btn_disconnect.setEnabled(True)
            self.btn_start.setEnabled(True)
            self.btn_publish.setEnabled(True)
            self.send_status("✅ 已连接到 MQTT Broker")
            self._log("✅ 连接成功")
        else:
            self.status_card.set_status("未连接", "offline")
            self.btn_connect.setEnabled(True)
            self.btn_connect.setText("🔗 连接")
            self.btn_disconnect.setEnabled(False)
            self.btn_start.setEnabled(False)
            self.btn_publish.setEnabled(False)
            self.btn_stop.setEnabled(False)
            if self.is_publishing:
                self._on_stop_publish()
            self.send_status("❌ 已断开连接")
            self._log("❌ 连接已断开")

    def _on_start_publish(self):
        """开始发布"""
        # 更新传感器配置
        self.logic.set_sensor_config(
            self.sensor_id_input.text().strip(),
            self.location_input.text().strip(),
            self.extra_input.text().strip()
        )
        
        interval = self.interval_input.value()
        records = self.logic.load_records()
        total_records = len(records)
        
        if total_records == 0:
            self.send_status("⚠️ 没有可发布的数据文件", "warning")
            return
        
        if self.logic.start_publish_from_files(interval):
            self.is_publishing = True
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(total_records)
            self.progress_bar.setValue(0)
            self.send_status(f"🚀 开始发布数据（共 {total_records} 条，间隔 {interval}s）...")
            self._log(f"🚀 开始从文件发布数据（间隔 {interval}s，共 {total_records} 条）")
        else:
            self.send_status("⚠️ 发布失败，可能已在运行中", "error")

    def _on_stop_publish(self):
        """停止发布"""
        self.logic.stop_publish()
        self.is_publishing = False
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.send_status("⏹ 已停止发布")
        self._log("⏹ 停止发布")

    def _on_publish_single(self):
        """发布单条消息"""
        # 更新传感器配置
        self.logic.set_sensor_config(
            self.sensor_id_input.text().strip(),
            self.location_input.text().strip(),
            self.extra_input.text().strip()
        )
        
        data_type = self.type_combo.currentText()
        value = self.value_input.value()
        
        if self.logic.publish_single(data_type, value):
            self.send_status(f"✅ 已发布 {data_type}={value}")
        else:
            self.send_status("❌ 发布失败，请先连接MQTT Broker", "error")

    def _on_message_published(self, topic: str, payload: dict):
        """消息发布回调"""
        self.pub_count += 1
        self.count_card.set_value(str(self.pub_count))
        
        # 更新进度条
        if self.is_publishing and self.progress_bar.isVisible():
            current_value = self.progress_bar.value()
            self.progress_bar.setValue(current_value + 1)
        
        # 添加到日志（使用缓冲，避免频繁更新）
        log_msg = f"[{payload.get('timestamp', 'N/A')}] {topic} → {payload.get('type')}: {payload.get('value')}"
        self._log_buffered(log_msg)

    def _on_publish_complete(self):
        """发布完成回调"""
        self.is_publishing = False
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.send_status("✅ 所有数据发布完成")
        self._log("✅ 文件数据发布完成")

    def _log(self, message: str):
        """添加日志（立即）"""
        self.log_text.append(message)
        # 自动滚动到底部
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.End)
        self.log_text.setTextCursor(cursor)
    
    def _log_buffered(self, message: str):
        """添加日志（缓冲，批量更新以提高性能）"""
        self._log_buffer.append(message)
        if not self._log_timer.isActive():
            self._log_timer.start(100)  # 100ms后批量刷新
    
    def _flush_log_buffer(self):
        """刷新日志缓冲区"""
        if self._log_buffer:
            # 批量添加日志
            self.log_text.append("\n".join(self._log_buffer))
            self._log_buffer.clear()
            # 自动滚动到底部
            cursor = self.log_text.textCursor()
            cursor.movePosition(cursor.End)
            self.log_text.setTextCursor(cursor)

    def _clear_log(self):
        """清空日志"""
        self.log_text.clear()
        self.send_status("日志已清空")

    def refresh_data(self):
        """刷新数据"""
        self.send_status("发布页面已刷新")
        
        # 检查数据文件
        records = self.logic.load_records()
        self.file_card.set_value(f"{len(records)} 条")

    def closeEvent(self, event):
        """窗口关闭时清理"""
        if self.logic:
            self.logic.stop_publish()
            self.logic.disconnect()
        event.accept()

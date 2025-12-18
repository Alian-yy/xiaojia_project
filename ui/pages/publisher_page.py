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
    QPushButton, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal

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
        broker_row.addWidget(QLabel("Broker:"))
        self.broker_input = QLineEdit("127.0.0.1")
        broker_row.addWidget(self.broker_input, 2)
        
        broker_row.addWidget(QLabel("端口:"))
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(1883)
        broker_row.addWidget(self.port_input)
        
        self.btn_connect = QPushButton("连接")
        self.btn_disconnect = QPushButton("断开")
        self.btn_disconnect.setEnabled(False)
        
        self.btn_connect.clicked.connect(self._on_connect_clicked)
        self.btn_disconnect.clicked.connect(self._on_disconnect_clicked)
        
        broker_row.addWidget(self.btn_connect)
        broker_row.addWidget(self.btn_disconnect)
        conn_layout.addLayout(broker_row)
        
        self.content_layout.addWidget(conn_panel)

        # 传感器配置面板
        sensor_panel, sensor_layout = self.create_panel("传感器配置", "📍")
        
        sensor_row1 = self.create_row_layout()
        sensor_row1.addWidget(QLabel("传感器ID:"))
        self.sensor_id_input = QLineEdit("JX_Teach_01")
        sensor_row1.addWidget(self.sensor_id_input, 2)
        
        sensor_row1.addWidget(QLabel("位置:"))
        self.location_input = QLineEdit("教学楼A")
        sensor_row1.addWidget(self.location_input, 2)
        sensor_layout.addLayout(sensor_row1)
        
        sensor_row2 = self.create_row_layout()
        sensor_row2.addWidget(QLabel("备注:"))
        self.extra_input = QLineEdit("三楼301教室")
        sensor_row2.addWidget(self.extra_input)
        sensor_layout.addLayout(sensor_row2)
        
        self.content_layout.addWidget(sensor_panel)

        # 发布控制面板（左右布局）
        control_row = self.create_row_layout()
        
        # 左侧：从文件发布
        file_panel, file_layout = self.create_panel("从文件发布数据", "📁")
        
        interval_row = self.create_row_layout()
        interval_row.addWidget(QLabel("发布间隔:"))
        self.interval_input = QDoubleSpinBox()
        self.interval_input.setRange(0.01, 10.0)
        self.interval_input.setValue(0.2)
        self.interval_input.setSuffix(" 秒")
        self.interval_input.setDecimals(2)
        interval_row.addWidget(self.interval_input)
        interval_row.addStretch()
        file_layout.addLayout(interval_row)
        
        btn_row = self.create_row_layout()
        self.btn_start = QPushButton("🚀 开始发布")
        self.btn_stop = QPushButton("⏹ 停止发布")
        self.btn_stop.setEnabled(False)
        
        self.btn_start.clicked.connect(self._on_start_publish)
        self.btn_stop.clicked.connect(self._on_stop_publish)
        
        btn_row.addWidget(self.btn_start)
        btn_row.addWidget(self.btn_stop)
        file_layout.addLayout(btn_row)
        
        control_row.addWidget(file_panel, 1)
        
        # 右侧：手动发布单条
        manual_panel, manual_layout = self.create_panel("手动发布", "✍️")
        
        manual_row1 = self.create_row_layout()
        manual_row1.addWidget(QLabel("数据类型:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["temperature", "humidity", "pressure"])
        manual_row1.addWidget(self.type_combo)
        manual_layout.addLayout(manual_row1)
        
        manual_row2 = self.create_row_layout()
        manual_row2.addWidget(QLabel("数值:"))
        self.value_input = QDoubleSpinBox()
        self.value_input.setRange(-100, 200)
        self.value_input.setValue(25.0)
        self.value_input.setDecimals(1)
        manual_row2.addWidget(self.value_input)
        manual_layout.addLayout(manual_row2)
        
        self.btn_publish = QPushButton("📤 发布消息")
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
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        self.content_layout.addWidget(log_panel)
        self.content_layout.addStretch()

    def _emit_message(self, topic: str, payload: dict):
        """触发消息发送信号"""
        self.message_published.emit(topic, payload)

    def _emit_connection(self, connected: bool):
        """触发连接状态变化信号"""
        self.connection_changed.emit(connected)

    def _on_connect_clicked(self):
        """连接按钮点击"""
        broker = self.broker_input.text().strip()
        port = self.port_input.value()
        
        if not broker:
            self.send_status("Broker地址不能为空", "error")
            return
        
        self.logic.broker = broker
        self.logic.port = port
        
        if self.logic.connect():
            self.send_status(f"正在连接到 {broker}:{port}...")
            self.btn_connect.setEnabled(False)
        else:
            self.send_status("连接失败", "error")

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
            self.btn_disconnect.setEnabled(True)
            self.btn_start.setEnabled(True)
            self.btn_publish.setEnabled(True)
            self.send_status("✅ 已连接到 MQTT Broker")
            self._log("✅ 连接成功")
        else:
            self.status_card.set_status("未连接", "offline")
            self.btn_connect.setEnabled(True)
            self.btn_disconnect.setEnabled(False)
            self.btn_start.setEnabled(False)
            self.btn_publish.setEnabled(False)
            self.btn_stop.setEnabled(False)
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
        if self.logic.start_publish_from_files(interval):
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
            self.send_status("🚀 开始发布数据...")
            self._log(f"🚀 开始从文件发布数据（间隔 {interval}s）")
        else:
            self.send_status("发布失败，可能已在运行中", "error")

    def _on_stop_publish(self):
        """停止发布"""
        self.logic.stop_publish()
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
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
            self.send_status("发布失败，请先连接", "error")

    def _on_message_published(self, topic: str, payload: dict):
        """消息发布回调"""
        self.pub_count += 1
        self.count_card.set_value(str(self.pub_count))
        
        # 添加到日志
        log_msg = f"[{payload.get('timestamp', 'N/A')}] {topic} → {payload.get('type')}: {payload.get('value')}"
        self._log(log_msg)

    def _on_publish_complete(self):
        """发布完成回调"""
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.send_status("✅ 所有数据发布完成")
        self._log("✅ 文件数据发布完成")

    def _log(self, message: str):
        """添加日志"""
        self.log_text.append(message)
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

# subscriber/location_widget.py
# 显示传感器位置信息的简单卡片

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class LocationWidget(QFrame):
    """展示位置与传感器 ID 的卡片。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("locationCard")
        self._sensor_id = "-"
        self._location = "-"
        self._extra = "-"
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("""
            #locationCard {
                background: rgba(20, 50, 90, 0.9);
                border: 1px solid #1a4a7a;
                border-radius: 8px;
            }
            #locationCard QLabel {
                color: #dfe9f5;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(6)

        self.title = QLabel("📍 传感器位置")
        self.title.setStyleSheet("font-size: 13px; font-weight: bold; color: #00d4ff;")

        self.sensor_label = QLabel(f"ID: {self._sensor_id}")
        self.location_label = QLabel(f"位置: {self._location}")
        self.extra_label = QLabel(f"备注: {self._extra}")

        layout.addWidget(self.title)
        layout.addWidget(self.sensor_label)
        layout.addWidget(self.location_label)
        layout.addWidget(self.extra_label)
        layout.addStretch()

    def set_location(self, sensor_id: str, location: str, extra: str = "-"):
        self._sensor_id = sensor_id or "-"
        self._location = location or "-"
        self._extra = extra or "-"
        self.sensor_label.setText(f"ID: {self._sensor_id}")
        self.location_label.setText(f"位置: {self._location}")
        self.extra_label.setText(f"备注: {self._extra}")


__all__ = ["LocationWidget"]

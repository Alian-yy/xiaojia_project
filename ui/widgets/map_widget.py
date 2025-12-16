# ui/widgets/map_widget.py
# 简易底图标注组件，基于静态图片与预设坐标

from typing import Dict, Tuple

from PyQt5.QtWidgets import QFrame
from PyQt5.QtGui import QPainter, QPixmap, QColor, QPen, QBrush, QFont
from PyQt5.QtCore import Qt


DEFAULT_LOCATION_POINTS: Dict[str, Tuple[float, float]] = {
    # 教学楼 A-H，基于 map.png 尺寸 1592x1219 的归一化坐标
    "教学楼A": (0.495, 0.481),
    "教学楼B": (0.516, 0.432),
    "教学楼C": (0.534, 0.391),
    "教学楼D": (0.584, 0.558),
    "教学楼E": (0.633, 0.598),
    "教学楼F": (0.609, 0.509),
    "教学楼G": (0.665, 0.550),
    "教学楼H": (0.679, 0.516),
}

DEFAULT_SENSOR_POINTS: Dict[str, Tuple[float, float, str]] = {
    # 传感器 ID -> (x_norm, y_norm, label)
    "JX_Teach": (0.495, 0.481, "教学楼A"),
}

STATUS_COLORS = {
    "normal": QColor(0, 255, 136),
    "warning": QColor(255, 200, 0),
    "error": QColor(255, 80, 80),
}


class MapWidget(QFrame):
    """
    使用静态底图 + 预设坐标绘制传感器位置。
    支持根据 sensor_id 或 location 字符串匹配坐标，未命中时落到中心。
    """

    def __init__(
        self,
        image_path: str = "assets/map.png",
        location_points: Dict[str, Tuple[float, float]] = None,
        sensor_points: Dict[str, Tuple[float, float, str]] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("mapWidget")
        self.setMinimumHeight(600)
        self.setStyleSheet("""
            #mapWidget {
                background: rgba(15, 35, 60, 0.9);
                border: 1px solid #1a4a7a;
                border-radius: 8px;
            }
        """)

        self._image_path = image_path
        self._pixmap = QPixmap(self._image_path)
        self._markers: Dict[str, Dict] = {}

        self.location_points = location_points or DEFAULT_LOCATION_POINTS
        self.sensor_points = sensor_points or DEFAULT_SENSOR_POINTS

    def _resolve_coord(self, sensor_id: str = "", location: str = "") -> Tuple[float, float, str]:
        """返回 (x_norm, y_norm, label)，未命中则居中。"""
        loc = (location or "").strip()
        sid = (sensor_id or "").strip()

        if loc and loc in self.location_points:
            x, y = self.location_points[loc]
            return x, y, loc

        if sid and sid in self.sensor_points:
            x, y, lbl = self.sensor_points[sid]
            return x, y, lbl

        # 未命中
        return 0.5, 0.5, loc or sid or "未知"

    def update_marker(self, sensor_id: str = "", location: str = "", status: str = "normal"):
        """更新/新增标记点。status: normal/warning/error"""
        x, y, label = self._resolve_coord(sensor_id, location)
        self._markers[sensor_id or label] = {
            "x": x,
            "y": y,
            "label": label,
            "status": status if status in STATUS_COLORS else "normal",
        }
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 背景
        painter.fillRect(self.rect(), QColor(10, 20, 40, 220))

        if not self._pixmap or self._pixmap.isNull():
            painter.setPen(QColor(180, 200, 220))
            painter.setFont(QFont("Microsoft YaHei", 10))
            painter.drawText(self.rect(), Qt.AlignCenter, "未找到地图文件：assets/map.png")
            return

        # 保持比例缩放并居中
        scaled = self._pixmap.scaled(
            self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        start_x = (self.width() - scaled.width()) / 2
        start_y = (self.height() - scaled.height()) / 2

        painter.drawPixmap(int(start_x), int(start_y), scaled)

        # 绘制标记
        for marker in self._markers.values():
            x = start_x + marker["x"] * scaled.width()
            y = start_y + marker["y"] * scaled.height()

            color = STATUS_COLORS.get(marker["status"], STATUS_COLORS["normal"])
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawEllipse(int(x) - 6, int(y) - 6, 12, 12)

            # 外圈
            painter.setPen(QPen(color, 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(int(x) - 10, int(y) - 10, 20, 20)

            # 标签
            painter.setPen(QColor(220, 230, 240))
            painter.setFont(QFont("Microsoft YaHei", 9))
            painter.drawText(int(x) + 8, int(y) - 8, marker["label"])


__all__ = ["MapWidget"]

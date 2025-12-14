# ui/widgets/gauge_widget.py
"""
仪表盘组件
提供圆形仪表盘、环形进度条等组件
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import Qt, QRectF, QTimer, QPointF
from PyQt5.QtGui import (
    QPainter, QPen, QColor, QFont, QConicalGradient,
    QBrush, QLinearGradient, QPainterPath
)
import math


class GaugeWidget(QWidget):
    """
    圆形仪表盘组件

    用法示例:
        gauge = GaugeWidget("温度", 0, 50, "°C")
        gauge.set_value(25.5)
        gauge.set_warning_range(35, 50)
    """

    def __init__(self, title: str = "", min_val: float = 0,
                 max_val: float = 100, unit: str = "%", parent=None):
        super().__init__(parent)

        self.title = title
        self.min_val = min_val
        self.max_val = max_val
        self.unit = unit

        self._value = min_val
        self._target_value = min_val
        self._warning_min = max_val * 0.7
        self._danger_min = max_val * 0.85

        # 颜色配置
        self.color_normal = QColor(0, 255, 200)
        self.color_warning = QColor(255, 200, 0)
        self.color_danger = QColor(255, 80, 80)
        self.color_bg = QColor(30, 60, 100)

        self.setMinimumSize(180, 200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 动画定时器
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate_value)

    def set_value(self, value: float, animate: bool = True):
        """设置数值"""
        self._target_value = max(self.min_val, min(self.max_val, value))

        if animate:
            if not self._timer.isActive():
                self._timer.start(16)
        else:
            self._value = self._target_value
            self.update()

    def set_warning_range(self, warning_start: float, danger_start: float):
        """设置警告和危险范围"""
        self._warning_min = warning_start
        self._danger_min = danger_start
        self.update()

    def set_range(self, min_val: float, max_val: float):
        """设置数值范围"""
        self.min_val = min_val
        self.max_val = max_val
        self.update()

    def _animate_value(self):
        """动画过渡"""
        diff = self._target_value - self._value
        if abs(diff) < 0.1:
            self._value = self._target_value
            self._timer.stop()
        else:
            self._value += diff * 0.12
        self.update()

    def _get_value_color(self) -> QColor:
        """根据数值获取颜色"""
        if self._value >= self._danger_min:
            return self.color_danger
        elif self._value >= self._warning_min:
            return self.color_warning
        return self.color_normal

    def paintEvent(self, event):
        """绑定绑定绘制"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 计算绘制区域
        size = min(self.width(), self.height() - 50)
        center_x = self.width() / 2
        center_y = size / 2 + 10
        radius = size / 2 - 20

        rect = QRectF(center_x - radius, center_y - radius,
                      radius * 2, radius * 2)

        # ===== 绘制背景圆弧 =====
        pen = QPen(self.color_bg, 14, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, 225 * 16, -270 * 16)

        # ===== 绘制刻度 =====
        self._draw_scale(painter, center_x, center_y, radius)

        # ===== 绘制进度圆弧 =====
        progress = (self._value - self.min_val) / (self.max_val - self.min_val)
        progress = max(0, min(1, progress))
        angle = int(-270 * progress * 16)

        # 渐变色
        gradient = QConicalGradient(center_x, center_y, 225)
        gradient.setColorAt(0, self.color_normal)
        gradient.setColorAt(0.7, self.color_warning)
        gradient.setColorAt(1, self.color_danger)

        pen = QPen(QBrush(gradient), 14, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, 225 * 16, angle)

        # ===== 绘制中心圆 =====
        inner_radius = radius - 35
        painter.setPen(Qt.NoPen)

        inner_gradient = QLinearGradient(
            center_x, center_y - inner_radius,
            center_x, center_y + inner_radius
        )
        inner_gradient.setColorAt(0, QColor(20, 45, 80))
        inner_gradient.setColorAt(1, QColor(10, 25, 50))
        painter.setBrush(inner_gradient)
        painter.drawEllipse(QPointF(center_x, center_y), inner_radius, inner_radius)

        # ===== 绘制数值 =====
        value_color = self._get_value_color()
        painter.setPen(value_color)

        font = QFont("Arial", 28, QFont.Bold)
        painter.setFont(font)

        value_text = f"{self._value:.1f}"
        text_rect = QRectF(center_x - radius, center_y - 20, radius * 2, 40)
        painter.drawText(text_rect, Qt.AlignCenter, value_text)

        # 绘制单位
        painter.setPen(QColor(100, 140, 180))
        font = QFont("Arial", 12)
        painter.setFont(font)
        unit_rect = QRectF(center_x - radius, center_y + 15, radius * 2, 25)
        painter.drawText(unit_rect, Qt.AlignCenter, self.unit)

        # ===== 绘制标题 =====
        painter.setPen(QColor(0, 200, 255))
        font = QFont("Microsoft YaHei", 12, QFont.Bold)
        painter.setFont(font)
        title_rect = QRectF(0, size - 5, self.width(), 35)
        painter.drawText(title_rect, Qt.AlignCenter, self.title)

    def _draw_scale(self, painter: QPainter, cx: float, cy: float, radius: float):
        """绘制刻度线"""
        scale_radius = radius + 5
        num_scales = 10

        for i in range(num_scales + 1):
            angle_deg = 225 - (270 * i / num_scales)
            angle_rad = math.radians(angle_deg)

            inner_r = scale_radius - 8
            outer_r = scale_radius - 3

            x1 = cx + inner_r * math.cos(angle_rad)
            y1 = cy - inner_r * math.sin(angle_rad)
            x2 = cx + outer_r * math.cos(angle_rad)
            y2 = cy - outer_r * math.sin(angle_rad)

            if i % 2 == 0:
                painter.setPen(QPen(QColor(80, 120, 160), 2))
            else:
                painter.setPen(QPen(QColor(50, 80, 110), 1))

            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    def get_value(self) -> float:
        """获取当前值"""
        return self._value


class ProgressRing(QWidget):
    """
    环形进度条组件

    用法示例:
        ring = ProgressRing("CPU使用率")
        ring.set_value(75)
        ring.set_color(QColor(0, 200, 255))
    """

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)

        self.title = title
        self._value = 0
        self._target_value = 0
        self._color = QColor(0, 200, 255)
        self._bg_color = QColor(30, 60, 100)

        self.setMinimumSize(100, 120)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 动画定时器
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)

    def set_value(self, value: float, animate: bool = True):
        """设置百分比值 (0-100)"""
        self._target_value = max(0, min(100, value))

        if animate:
            if not self._timer.isActive():
                self._timer.start(16)
        else:
            self._value = self._target_value
            self.update()

    def set_color(self, color: QColor):
        """设置进度条颜色"""
        self._color = color
        self.update()

    def _animate(self):
        """动画"""
        diff = self._target_value - self._value
        if abs(diff) < 0.5:
            self._value = self._target_value
            self._timer.stop()
        else:
            self._value += diff * 0.1
        self.update()

    def paintEvent(self, event):
        """绑定绑定绘制"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 计算尺寸
        size = min(self.width(), self.height() - 25)
        center_x = self.width() / 2
        center_y = size / 2 + 5
        radius = size / 2 - 10

        rect = QRectF(center_x - radius, center_y - radius,
                      radius * 2, radius * 2)

        # ===== 背景圆环 =====
        pen = QPen(self._bg_color, 8)
        painter.setPen(pen)
        painter.drawEllipse(rect)

        # ===== 进度圆弧 =====
        gradient = QConicalGradient(center_x, center_y, 90)
        gradient.setColorAt(0, self._color)
        gradient.setColorAt(0.5, self._color.lighter(120))
        gradient.setColorAt(1, self._color)

        pen = QPen(QBrush(gradient), 8, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)

        # 绘制进度弧
        span_angle = int(-360 * (self._value / 100) * 16)
        painter.drawArc(rect, 90 * 16, span_angle)

        # ===== 中心文字 =====
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Arial", 16, QFont.Bold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, f"{int(self._value)}%")

        # ===== 标题 =====
        painter.setPen(QColor(100, 140, 180))
        font = QFont("Microsoft YaHei", 9)
        painter.setFont(font)
        title_rect = QRectF(0, size, self.width(), 25)
        painter.drawText(title_rect, Qt.AlignCenter, self.title)

    def get_value(self) -> float:
        """获取当前值"""
        return self._value


class DashboardGauge(QWidget):
    """
    仪表盘风格的大型组件
    包含仪表盘 + 数值 + 状态信息

    用法示例:
        dashboard = DashboardGauge("系统负载", 0, 100, "%")
        dashboard.set_value(65)
        dashboard.set_status_text("运行正常")
    """

    def __init__(self, title: str = "", min_val: float = 0,
                 max_val: float = 100, unit: str = "%", parent=None):
        super().__init__(parent)

        self.title = title
        self.min_val = min_val
        self.max_val = max_val
        self.unit = unit
        self._value = min_val
        self._target_value = min_val
        self._status_text = ""

        # 阈值设置
        self._thresholds = [
            (0.6, QColor(0, 255, 200), "正常"),
            (0.8, QColor(255, 200, 0), "警告"),
            (1.0, QColor(255, 80, 80), "危险")
        ]

        self.setMinimumSize(220, 250)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 动画
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)

    def set_value(self, value: float, animate: bool = True):
        """设置数值"""
        self._target_value = max(self.min_val, min(self.max_val, value))
        if animate:
            if not self._timer.isActive():
                self._timer.start(16)
        else:
            self._value = self._target_value
            self.update()

    def set_status_text(self, text: str):
        """设置状态文本"""
        self._status_text = text
        self.update()

    def set_thresholds(self, thresholds: list):
        """
        设置阈值
        thresholds: [(比例, 颜色, 文本), ...]
        """
        self._thresholds = thresholds
        self.update()

    def _animate(self):
        """动画"""
        diff = self._target_value - self._value
        if abs(diff) < 0.1:
            self._value = self._target_value
            self._timer.stop()
        else:
            self._value += diff * 0.1
        self.update()

    def _get_current_state(self) -> tuple:
        """获取当前状态（颜色，文本）"""
        ratio = (self._value - self.min_val) / (self.max_val - self.min_val)
        for threshold, color, text in self._thresholds:
            if ratio <= threshold:
                return color, text
        return self._thresholds[-1][1], self._thresholds[-1][2]

    def paintEvent(self, event):
        """绘制"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        size = min(w, h - 60)
        cx, cy = w / 2, size / 2 + 10
        radius = size / 2 - 25

        rect = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)

        color, status = self._get_current_state()

        # ===== 外圈装饰 =====
        painter.setPen(QPen(QColor(40, 70, 110), 2))
        painter.drawEllipse(rect.adjusted(-8, -8, 8, 8))

        # ===== 背景弧 =====
        painter.setPen(QPen(QColor(30, 55, 90), 16, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(rect, 225 * 16, -270 * 16)

        # ===== 进度弧 =====
        progress = (self._value - self.min_val) / (self.max_val - self.min_val)
        progress = max(0, min(1, progress))

        # 渐变
        gradient = QConicalGradient(cx, cy, 225)
        gradient.setColorAt(0, color.lighter(130))
        gradient.setColorAt(0.5, color)
        gradient.setColorAt(1, color.darker(120))

        painter.setPen(QPen(QBrush(gradient), 16, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(rect, 225 * 16, int(-270 * progress * 16))

        # ===== 中心背景 =====
        inner_radius = radius - 30
        gradient_bg = QLinearGradient(cx, cy - inner_radius, cx, cy + inner_radius)
        gradient_bg.setColorAt(0, QColor(25, 50, 85))
        gradient_bg.setColorAt(1, QColor(15, 35, 60))

        painter.setPen(Qt.NoPen)
        painter.setBrush(gradient_bg)
        painter.drawEllipse(QPointF(cx, cy), inner_radius, inner_radius)

        # ===== 数值 =====
        painter.setPen(color)
        font = QFont("Arial", 32, QFont.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(cx - radius, cy - 25, radius * 2, 50),
                         Qt.AlignCenter, f"{self._value:.1f}")

        # 单位
        painter.setPen(QColor(100, 140, 180))
        font = QFont("Arial", 12)
        painter.setFont(font)
        painter.drawText(QRectF(cx - radius, cy + 20, radius * 2, 25),
                         Qt.AlignCenter, self.unit)

        # ===== 标题 =====
        painter.setPen(QColor(0, 200, 255))
        font = QFont("Microsoft YaHei", 13, QFont.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(0, size + 5, w, 25),
                         Qt.AlignCenter, self.title)

        # ===== 状态 =====
        status_text = self._status_text if self._status_text else status
        painter.setPen(color)
        font = QFont("Microsoft YaHei", 10)
        painter.setFont(font)
        painter.drawText(QRectF(0, size + 28, w, 22),
                         Qt.AlignCenter, f"● {status_text}")


class MultiRingGauge(QWidget):
    """
    多环仪表盘
    可同时展示多个数据指标

    用法示例:
        gauge = MultiRingGauge()
        gauge.set_rings([
            ("CPU", 75, QColor(0, 200, 255)),
            ("内存", 60, QColor(0, 255, 150)),
            ("磁盘", 45, QColor(255, 200, 0))
        ])
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self._rings = []  # [(name, value, color), ...]
        self.setMinimumSize(200, 220)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_rings(self, rings: list):
        """
        设置环形数据
        rings: [(name, value, color), ...]
        """
        self._rings = rings
        self.update()

    def update_ring(self, index: int, value: float):
        """更新单个环的值"""
        if 0 <= index < len(self._rings):
            name, _, color = self._rings[index]
            self._rings[index] = (name, value, color)
            self.update()

    def paintEvent(self, event):
        """绘制"""
        if not self._rings:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        size = min(w, h - 40)
        cx, cy = w / 2, size / 2 + 5

        base_radius = size / 2 - 15
        ring_width = 12
        ring_gap = 6

        # 绘制每个环
        for i, (name, value, color) in enumerate(self._rings):
            radius = base_radius - i * (ring_width + ring_gap)
            if radius <= 20:
                break

            rect = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)

            # 背景环
            painter.setPen(QPen(QColor(30, 55, 90), ring_width, Qt.SolidLine, Qt.RoundCap))
            painter.drawArc(rect, 90 * 16, -360 * 16)

            # 进度环
            gradient = QConicalGradient(cx, cy, 90)
            gradient.setColorAt(0, color)
            gradient.setColorAt(0.5, color.lighter(120))
            gradient.setColorAt(1, color)

            painter.setPen(QPen(QBrush(gradient), ring_width, Qt.SolidLine, Qt.RoundCap))
            span = int(-360 * (value / 100) * 16)
            painter.drawArc(rect, 90 * 16, span)

        # 中心文字
        if self._rings:
            painter.setPen(QColor(255, 255, 255))
            font = QFont("Arial", 14, QFont.Bold)
            painter.setFont(font)

            # 显示第一个值
            name, value, _ = self._rings[0]
            painter.drawText(QRectF(cx - 50, cy - 15, 100, 30),
                             Qt.AlignCenter, f"{value:.0f}%")

        # 图例
        legend_y = size + 10
        legend_x = 10
        painter.setFont(QFont("Microsoft YaHei", 9))

        for i, (name, value, color) in enumerate(self._rings):
            painter.setPen(color)
            painter.setBrush(color)
            painter.drawEllipse(legend_x, int(legend_y), 8, 8)

            painter.setPen(QColor(180, 200, 220))
            painter.drawText(legend_x + 12, int(legend_y + 9), f"{name}: {value:.0f}%")

            legend_x += 80
            if legend_x > w - 80:
                legend_x = 10
                legend_y += 15

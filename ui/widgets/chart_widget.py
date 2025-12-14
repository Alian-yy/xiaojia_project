# ui/widgets/chart_widget.py
"""
图表组件
提供折线图、柱状图、饼图等数据可视化组件
"""

from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QSizePolicy, QWidget
)
from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt5.QtGui import (
    QPainter, QPen, QColor, QLinearGradient,
    QPainterPath, QFont, QBrush, QConicalGradient
)
import math


class LineChart(QFrame):
    """
    折线图组件

    用法示例:
        chart = LineChart("温度趋势")
        chart.set_data([20, 22, 25, 23, 26, 28, 27])
        chart.add_point(29)  # 动态添加点
    """

    def __init__(self, title: str = "数据趋势", parent=None):
        super().__init__(parent)
        self.setObjectName("chartWidget")

        self.title = title
        self.data_points = []
        self.max_points = 30

        # 样式设置
        self.line_color = QColor(0, 200, 255)
        self.fill_color_top = QColor(0, 200, 255, 80)
        self.fill_color_bottom = QColor(0, 200, 255, 10)
        self.grid_color = QColor(30, 60, 100)
        self.text_color = QColor(100, 140, 180)

        self.setMinimumHeight(200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._apply_style()
        self.setup_ui()

    def _apply_style(self):
        """应用样式"""
        self.setStyleSheet("""
            #chartWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(20, 50, 90, 0.9),
                    stop:1 rgba(10, 30, 60, 0.9)
                );
                border: 1px solid #1a4a7a;
                border-radius: 10px;
            }
        """)

    def setup_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题头部
        header = QFrame()
        header.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(0, 150, 255, 0.3),
                stop:1 transparent
            );
            border-bottom: 1px solid #1a4a7a;
            border-radius: 10px 10px 0 0;
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 10, 15, 10)

        title_label = QLabel(f"📈 {self.title}")
        title_label.setStyleSheet("""
            color: #00d4ff;
            font-size: 14px;
            font-weight: bold;
            background: transparent;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        # 实时值显示
        self.value_label = QLabel("--")
        self.value_label.setStyleSheet("""
            color: #00ffff;
            font-size: 16px;
            font-weight: bold;
            background: transparent;
        """)
        header_layout.addWidget(self.value_label)

        layout.addWidget(header)
        layout.addStretch()

    def add_point(self, value: float):
        """添加单个数据点"""
        self.data_points.append(value)
        if len(self.data_points) > self.max_points:
            self.data_points.pop(0)
        self.value_label.setText(f"{value:.1f}")
        self.update()

    def set_data(self, data: list):
        """设置完整数据"""
        self.data_points = list(data[-self.max_points:])
        if self.data_points:
            self.value_label.setText(f"{self.data_points[-1]:.1f}")
        self.update()

    def clear_data(self):
        """清空数据"""
        self.data_points = []
        self.value_label.setText("--")
        self.update()

    def set_line_color(self, color: QColor):
        """设置线条颜色"""
        self.line_color = color
        self.fill_color_top = QColor(color.red(), color.green(), color.blue(), 80)
        self.fill_color_bottom = QColor(color.red(), color.green(), color.blue(), 10)
        self.update()

    def paintEvent(self, event):
        """绘制图表"""
        super().paintEvent(event)

        if len(self.data_points) < 2:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 计算绘图区域
        margin_left = 50
        margin_right = 20
        margin_top = 55
        margin_bottom = 35

        chart_rect = QRectF(
            margin_left,
            margin_top,
            self.width() - margin_left - margin_right,
            self.height() - margin_top - margin_bottom
        )

        if chart_rect.width() <= 0 or chart_rect.height() <= 0:
            return

        # 计算数据范围
        min_val = min(self.data_points)
        max_val = max(self.data_points)
        value_range = max_val - min_val if max_val != min_val else 1

        # 留出10%边距
        min_val -= value_range * 0.1
        max_val += value_range * 0.1
        value_range = max_val - min_val

        # ===== 绘制网格线 =====
        painter.setPen(QPen(self.grid_color, 1, Qt.DashLine))
        num_grid_lines = 5

        for i in range(num_grid_lines):
            y = chart_rect.top() + chart_rect.height() * i / (num_grid_lines - 1)
            painter.drawLine(
                QPointF(chart_rect.left(), y),
                QPointF(chart_rect.right(), y)
            )

            # Y轴刻度值
            val = max_val - value_range * i / (num_grid_lines - 1)
            painter.setPen(self.text_color)
            painter.setFont(QFont("Arial", 9))
            painter.drawText(
                QRectF(5, y - 10, margin_left - 10, 20),
                Qt.AlignRight | Qt.AlignVCenter,
                f"{val:.1f}"
            )
            painter.setPen(QPen(self.grid_color, 1, Qt.DashLine))

        # ===== 计算数据点坐标 =====
        points = []
        for i, val in enumerate(self.data_points):
            x = chart_rect.left() + chart_rect.width() * i / (len(self.data_points) - 1)
            y = chart_rect.bottom() - chart_rect.height() * (val - min_val) / value_range
            points.append(QPointF(x, y))

        # ===== 绘制填充区域 =====
        fill_path = QPainterPath()
        fill_path.moveTo(QPointF(points[0].x(), chart_rect.bottom()))
        fill_path.lineTo(points[0])

        for p in points[1:]:
            fill_path.lineTo(p)

        fill_path.lineTo(QPointF(points[-1].x(), chart_rect.bottom()))
        fill_path.closeSubpath()

        # 渐变填充
        gradient = QLinearGradient(0, chart_rect.top(), 0, chart_rect.bottom())
        gradient.setColorAt(0, self.fill_color_top)
        gradient.setColorAt(1, self.fill_color_bottom)
        painter.fillPath(fill_path, gradient)

        # ===== 绘制折线 =====
        line_path = QPainterPath()
        line_path.moveTo(points[0])
        for p in points[1:]:
            line_path.lineTo(p)

        painter.setPen(QPen(self.line_color, 2))
        painter.drawPath(line_path)

        # ===== 绘制数据点 =====
        painter.setBrush(self.line_color)
        painter.setPen(QPen(QColor(255, 255, 255), 2))

        # 只绘制最后一个点（当前值）
        if points:
            last_point = points[-1]
            painter.drawEllipse(last_point, 5, 5)

        # ===== 绘制X轴标签 =====
        painter.setPen(self.text_color)
        painter.setFont(QFont("Arial", 8))

        num_x_labels = min(6, len(self.data_points))
        for i in range(num_x_labels):
            idx = int(i * (len(self.data_points) - 1) / (num_x_labels - 1)) if num_x_labels > 1 else 0
            x = chart_rect.left() + chart_rect.width() * idx / (len(self.data_points) - 1)
            painter.drawText(
                QRectF(x - 20, chart_rect.bottom() + 5, 40, 20),
                Qt.AlignCenter,
                str(idx + 1)
            )


class BarChart(QFrame):
    """
    柱状图组件

    用法示例:
        chart = BarChart("设备统计")
        chart.set_data({
            "在线": 42,
            "离线": 8,
            "告警": 3
        })
    """

    def __init__(self, title: str = "数据统计", parent=None):
        super().__init__(parent)
        self.setObjectName("chartWidget")

        self.title = title
        self.data = {}

        # 默认颜色列表
        self.colors = [
            QColor(0, 200, 255),
            QColor(0, 255, 150),
            QColor(255, 200, 0),
            QColor(255, 100, 100),
            QColor(200, 100, 255),
            QColor(255, 150, 50),
        ]

        self.setMinimumHeight(200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._apply_style()
        self.setup_ui()

    def _apply_style(self):
        """应用样式"""
        self.setStyleSheet("""
            #chartWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(20, 50, 90, 0.9),
                    stop:1 rgba(10, 30, 60, 0.9)
                );
                border: 1px solid #1a4a7a;
                border-radius: 10px;
            }
        """)

    def setup_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题头部
        header = QFrame()
        header.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(0, 150, 255, 0.3),
                stop:1 transparent
            );
            border-bottom: 1px solid #1a4a7a;
            border-radius: 10px 10px 0 0;
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 10, 15, 10)

        title_label = QLabel(f"📊 {self.title}")
        title_label.setStyleSheet("""
            color: #00d4ff;
            font-size: 14px;
            font-weight: bold;
            background: transparent;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addWidget(header)
        layout.addStretch()

    def set_data(self, data: dict):
        """
        设置数据
        data: {标签: 值, ...}
        """
        self.data = data
        self.update()

    def set_colors(self, colors: list):
        """设置颜色列表"""
        self.colors = colors
        self.update()

    def paintEvent(self, event):
        """绘制图表"""
        super().paintEvent(event)

        if not self.data:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 计算绘图区域
        margin_left = 50
        margin_right = 20
        margin_top = 55
        margin_bottom = 50

        chart_rect = QRectF(
            margin_left,
            margin_top,
            self.width() - margin_left - margin_right,
            self.height() - margin_top - margin_bottom
        )

        if chart_rect.width() <= 0 or chart_rect.height() <= 0:
            return

        # 数据处理
        labels = list(self.data.keys())
        values = list(self.data.values())
        max_val = max(values) if values else 1

        # 计算柱子尺寸
        num_bars = len(labels)
        bar_width = min(60, chart_rect.width() / num_bars * 0.6)
        gap = (chart_rect.width() - bar_width * num_bars) / (num_bars + 1)

        # ===== 绘制网格线 =====
        painter.setPen(QPen(QColor(30, 60, 100), 1, Qt.DashLine))
        for i in range(5):
            y = chart_rect.top() + chart_rect.height() * i / 4
            painter.drawLine(
                QPointF(chart_rect.left(), y),
                QPointF(chart_rect.right(), y)
            )

            # Y轴刻度
            val = max_val * (4 - i) / 4
            painter.setPen(QColor(100, 140, 180))
            painter.setFont(QFont("Arial", 9))
            painter.drawText(
                QRectF(5, y - 10, margin_left - 10, 20),
                Qt.AlignRight | Qt.AlignVCenter,
                f"{val:.0f}"
            )
            painter.setPen(QPen(QColor(30, 60, 100), 1, Qt.DashLine))

        # ===== 绘制柱子 =====
        for i, (label, value) in enumerate(zip(labels, values)):
            x = chart_rect.left() + gap + i * (bar_width + gap)
            bar_height = chart_rect.height() * value / max_val
            y = chart_rect.bottom() - bar_height

            color = self.colors[i % len(self.colors)]

            # 渐变填充
            gradient = QLinearGradient(x, y, x, chart_rect.bottom())
            gradient.setColorAt(0, color.lighter(120))
            gradient.setColorAt(1, color)

            painter.setPen(Qt.NoPen)
            painter.setBrush(gradient)

            # 绘制圆角矩形
            bar_rect = QRectF(x, y, bar_width, bar_height)
            painter.drawRoundedRect(bar_rect, 4, 4)

            # 顶部高亮
            painter.setBrush(QColor(255, 255, 255, 50))
            highlight_rect = QRectF(x, y, bar_width, min(5, bar_height))
            painter.drawRoundedRect(highlight_rect, 4, 4)

            # 数值标签
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Arial", 10, QFont.Bold))
            painter.drawText(
                QRectF(x, y - 22, bar_width, 20),
                Qt.AlignCenter,
                str(value)
            )

            # X轴标签
            painter.setPen(QColor(150, 180, 210))
            painter.setFont(QFont("Microsoft YaHei", 9))
            painter.drawText(
                QRectF(x - 10, chart_rect.bottom() + 8, bar_width + 20, 25),
                Qt.AlignCenter,
                label
            )


class PieChart(QFrame):
    """
    饼图/环形图组件

    用法示例:
        chart = PieChart("占比分析")
        chart.set_data({
            "温度": 35,
            "湿度": 25,
            "光照": 20,
            "其他": 20
        })
        chart.set_donut(True)  # 设置为环形图
    """

    def __init__(self, title: str = "占比分析", parent=None):
        super().__init__(parent)
        self.setObjectName("chartWidget")

        self.title = title
        self.data = {}
        self._is_donut = True  # 默认环形图

        # 默认颜色
        self.colors = [
            QColor(0, 200, 255),
            QColor(0, 255, 150),
            QColor(255, 200, 0),
            QColor(255, 100, 100),
            QColor(200, 100, 255),
            QColor(100, 200, 100),
        ]

        self.setMinimumSize(200, 250)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._apply_style()
        self.setup_ui()

    def _apply_style(self):
        """应用样式"""
        self.setStyleSheet("""
            #chartWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(20, 50, 90, 0.9),
                    stop:1 rgba(10, 30, 60, 0.9)
                );
                border: 1px solid #1a4a7a;
                border-radius: 10px;
            }
        """)

    def setup_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题头部
        header = QFrame()
        header.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(0, 150, 255, 0.3),
                stop:1 transparent
            );
            border-bottom: 1px solid #1a4a7a;
            border-radius: 10px 10px 0 0;
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 10, 15, 10)

        title_label = QLabel(f"🥧 {self.title}")
        title_label.setStyleSheet("""
            color: #00d4ff;
            font-size: 14px;
            font-weight: bold;
            background: transparent;
        """)
        header_layout.addWidget(title_label)

        layout.addWidget(header)
        layout.addStretch()

    def set_data(self, data: dict):
        """
        设置数据
        data: {标签: 值, ...}
        """
        self.data = data
        self.update()

    def set_donut(self, is_donut: bool):
        """设置是否为环形图"""
        self._is_donut = is_donut
        self.update()

    def set_colors(self, colors: list):
        """设置颜色列表"""
        self.colors = colors
        self.update()

    def paintEvent(self, event):
        """绘制图表"""
        super().paintEvent(event)

        if not self.data:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 计算绘图区域
        header_height = 45
        legend_height = 60

        available_height = self.height() - header_height - legend_height
        available_width = self.width()

        size = min(available_width - 40, available_height - 20)
        cx = available_width / 2
        cy = header_height + available_height / 2
        radius = size / 2

        rect = QRectF(cx - radius, cy - radius, size, size)

        # 计算总值
        total = sum(self.data.values())
        if total == 0:
            return

        # ===== 绘制饼图扇区 =====
        start_angle = 90 * 16  # 从顶部开始

        labels = list(self.data.keys())
        values = list(self.data.values())

        for i, (label, value) in enumerate(zip(labels, values)):
            span_angle = int(-360 * value / total * 16)
            color = self.colors[i % len(self.colors)]

            # 绘制扇区
            painter.setPen(QPen(QColor(20, 40, 70), 2))
            painter.setBrush(color)
            painter.drawPie(rect, start_angle, span_angle)

            start_angle += span_angle

        # ===== 环形图中心 =====
        if self._is_donut:
            inner_radius = radius * 0.55
            inner_rect = QRectF(
                cx - inner_radius,
                cy - inner_radius,
                inner_radius * 2,
                inner_radius * 2
            )

            # 内圆背景
            gradient = QLinearGradient(cx, cy - inner_radius, cx, cy + inner_radius)
            gradient.setColorAt(0, QColor(20, 45, 80))
            gradient.setColorAt(1, QColor(10, 30, 55))

            painter.setPen(Qt.NoPen)
            painter.setBrush(gradient)
            painter.drawEllipse(inner_rect)

            # 中心文字
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Arial", 18, QFont.Bold))
            painter.drawText(inner_rect, Qt.AlignCenter, f"{total:.0f}")

        # ===== 绘制图例 =====
        legend_y = self.height() - legend_height + 10
        legend_start_x = 15
        item_width = (self.width() - 30) / min(3, len(labels))

        painter.setFont(QFont("Microsoft YaHei", 9))

        for i, (label, value) in enumerate(zip(labels, values)):
            col = i % 3
            row = i // 3

            x = legend_start_x + col * item_width
            y = legend_y + row * 22

            color = self.colors[i % len(self.colors)]

            # 颜色块
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            painter.drawRoundedRect(QRectF(x, y + 2, 12, 12), 2, 2)

            # 标签文字
            percent = value / total * 100
            painter.setPen(QColor(180, 200, 220))
            painter.drawText(
                QRectF(x + 16, y, item_width - 20, 18),
                Qt.AlignLeft | Qt.AlignVCenter,
                f"{label}: {percent:.1f}%"
            )



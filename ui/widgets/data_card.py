# ui/widgets/data_card.py
"""
数据卡片组件
提供多种样式的数据展示卡片
"""

from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QGraphicsDropShadowEffect, QSizePolicy, QWidget
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QFont


class DataCard(QFrame):
    """
    标准数据卡片
    用于展示单个数据指标

    用法示例:
        card = DataCard("温度", "25.5", "°C", "🌡️", "normal")
        card.set_value("26.0")
        card.set_status("warning")
        card.set_subtext("较昨日上升 0.5°C")
    """

    def __init__(self, title: str, value: str = "0", unit: str = "",
                 icon: str = "📊", status: str = "normal", parent=None):
        super().__init__(parent)
        self.setObjectName("dataCard")
        self._title = title
        self._value = value
        self._unit = unit
        self._icon = icon
        self._status = status

        self.setup_ui()
        self.setup_shadow()

        # 设置尺寸策略
        self.setMinimumSize(200, 120)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def setup_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ===== 头部 =====
        header = QFrame()
        header.setObjectName("cardHeader")
        header.setStyleSheet("""
            #cardHeader {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 150, 255, 0.3),
                    stop:1 transparent
                );
                border-bottom: 1px solid #1a4a7a;
                border-radius: 8px 8px 0 0;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 8, 12, 8)

        # 图标
        icon_label = QLabel(self._icon)
        icon_label.setStyleSheet("font-size: 16px; background: transparent;")
        header_layout.addWidget(icon_label)

        # 标题
        self.title_label = QLabel(self._title)
        self.title_label.setStyleSheet("""
            color: #00d4ff;
            font-size: 13px;
            font-weight: bold;
            background: transparent;
        """)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        # 状态指示器
        self.status_label = QLabel(self._get_status_text())
        self._apply_status_style()
        header_layout.addWidget(self.status_label)

        layout.addWidget(header)

        # ===== 主体 =====
        body = QFrame()
        body.setStyleSheet("background: transparent;")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(15, 12, 15, 15)
        body_layout.setSpacing(5)

        # 数值行
        value_row = QHBoxLayout()
        value_row.setSpacing(5)

        self.value_label = QLabel(self._value)
        self.value_label.setStyleSheet("""
            color: #00ffff;
            font-size: 32px;
            font-weight: bold;
        """)
        value_row.addWidget(self.value_label)

        # 单位
        if self._unit:
            self.unit_label = QLabel(self._unit)
            self.unit_label.setStyleSheet("""
                color: #5588aa;
                font-size: 14px;
                padding-top: 12px;
            """)
            value_row.addWidget(self.unit_label)

        value_row.addStretch()
        body_layout.addLayout(value_row)

        # 副标题/描述
        self.subtext_label = QLabel("")
        self.subtext_label.setStyleSheet("""
            color: #5588aa;
            font-size: 11px;
        """)
        body_layout.addWidget(self.subtext_label)

        layout.addWidget(body)

    def setup_shadow(self):
        """添加发光阴影效果"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 200, 255, 60))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)

    def _get_status_text(self) -> str:
        """获取状态文本"""
        status_map = {
            "normal": "● 正常",
            "warning": "● 警告",
            "error": "● 异常",
            "offline": "● 离线"
        }
        return status_map.get(self._status, "● 未知")

    def _apply_status_style(self):
        """应用状态样式"""
        styles = {
            "normal": """
                background: rgba(0, 255, 136, 0.15);
                color: #00ff88;
                border: 1px solid rgba(0, 255, 136, 0.5);
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 11px;
            """,
            "warning": """
                background: rgba(255, 200, 0, 0.15);
                color: #ffc800;
                border: 1px solid rgba(255, 200, 0, 0.5);
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 11px;
            """,
            "error": """
                background: rgba(255, 80, 80, 0.15);
                color: #ff5050;
                border: 1px solid rgba(255, 80, 80, 0.5);
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 11px;
            """,
            "offline": """
                background: rgba(100, 100, 100, 0.15);
                color: #888888;
                border: 1px solid rgba(100, 100, 100, 0.5);
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 11px;
            """
        }
        self.status_label.setStyleSheet(styles.get(self._status, styles["normal"]))

    # ===== 公共API方法 =====

    def set_value(self, value: str):
        """设置数值"""
        self._value = value
        self.value_label.setText(value)

    def set_status(self, status: str):
        """设置状态: normal, warning, error, offline"""
        self._status = status
        self.status_label.setText(self._get_status_text())
        self._apply_status_style()

    def set_subtext(self, text: str):
        """设置副标题"""
        self.subtext_label.setText(text)

    def set_title(self, title: str):
        """设置标题"""
        self._title = title
        self.title_label.setText(title)

    def get_value(self) -> str:
        """获取当前值"""
        return self._value


class MiniCard(QFrame):
    """
    迷你数据卡片
    用于展示简洁的数据，带趋势指示

    用法示例:
        card = MiniCard("今日访问", "1,234", "+12%", True)
        card.set_value("1,456")
        card.set_trend("+18%", True)
    """

    def __init__(self, title: str, value: str, trend: str = "",
                 trend_up: bool = True, parent=None):
        super().__init__(parent)
        self.setObjectName("miniCard")
        self._title = title
        self._value = value
        self._trend = trend
        self._trend_up = trend_up

        self.setup_ui()
        self.setMinimumSize(160, 90)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def setup_ui(self):
        """初始化UI"""
        self.setStyleSheet("""
            #miniCard {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(20, 50, 90, 0.9),
                    stop:1 rgba(10, 30, 60, 0.9)
                );
                border: 1px solid #1a4a7a;
                border-radius: 8px;
            }
            #miniCard:hover {
                border: 1px solid #00d4ff;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(5)

        # 标题
        self.title_label = QLabel(self._title)
        self.title_label.setStyleSheet("color: #5588aa; font-size: 12px;")
        layout.addWidget(self.title_label)

        # 数值行
        value_row = QHBoxLayout()
        value_row.setSpacing(8)

        self.value_label = QLabel(self._value)
        self.value_label.setStyleSheet("""
            color: #00ffff;
            font-size: 22px;
            font-weight: bold;
        """)
        value_row.addWidget(self.value_label)

        # 趋势指示
        self.trend_label = QLabel()
        self._update_trend_display()
        value_row.addWidget(self.trend_label)

        value_row.addStretch()
        layout.addLayout(value_row)

    def _update_trend_display(self):
        """更新趋势显示"""
        if self._trend:
            trend_color = "#00ff88" if self._trend_up else "#ff5050"
            trend_arrow = "↑" if self._trend_up else "↓"
            self.trend_label.setText(f"{trend_arrow} {self._trend}")
            self.trend_label.setStyleSheet(f"""
                color: {trend_color};
                font-size: 11px;
                padding-top: 8px;
            """)
            self.trend_label.show()
        else:
            self.trend_label.hide()

    def set_value(self, value: str):
        """设置数值"""
        self._value = value
        self.value_label.setText(value)

    def set_trend(self, trend: str, trend_up: bool = True):
        """设置趋势"""
        self._trend = trend
        self._trend_up = trend_up
        self._update_trend_display()

    def set_title(self, title: str):
        """设置标题"""
        self._title = title
        self.title_label.setText(title)


class StatusCard(QFrame):
    """
    状态卡片
    用于展示设备/系统状态

    用法示例:
        card = StatusCard("服务器状态", "运行中", "online")
        card.set_status("离线", "offline")
    """

    STATUS_COLORS = {
        "online": ("#00ff88", "rgba(0, 255, 136, 0.1)"),
        "offline": ("#ff5050", "rgba(255, 80, 80, 0.1)"),
        "warning": ("#ffc800", "rgba(255, 200, 0, 0.1)"),
        "idle": ("#5588aa", "rgba(85, 136, 170, 0.1)"),
    }

    def __init__(self, title: str, status_text: str = "未知",
                 status: str = "idle", icon: str = "🖥️", parent=None):
        super().__init__(parent)
        self.setObjectName("statusCard")
        self._title = title
        self._status_text = status_text
        self._status = status
        self._icon = icon

        self.setup_ui()
        self.setMinimumSize(180, 100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def setup_ui(self):
        """初始化UI"""
        self.setStyleSheet("""
            #statusCard {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(20, 50, 90, 0.9),
                    stop:1 rgba(10, 30, 60, 0.9)
                );
                border: 1px solid #1a4a7a;
                border-radius: 8px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 左侧图标
        self.icon_label = QLabel(self._icon)
        self.icon_label.setStyleSheet("font-size: 32px;")
        self.icon_label.setFixedSize(50, 50)
        self.icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.icon_label)

        # 右侧信息
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)

        self.title_label = QLabel(self._title)
        self.title_label.setStyleSheet("""
            color: #aabbcc;
            font-size: 12px;
        """)
        info_layout.addWidget(self.title_label)

        # 状态指示
        status_row = QHBoxLayout()
        status_row.setSpacing(8)

        self.status_dot = QLabel("●")
        self.status_text_label = QLabel(self._status_text)
        self._apply_status_style()

        status_row.addWidget(self.status_dot)
        status_row.addWidget(self.status_text_label)
        status_row.addStretch()

        info_layout.addLayout(status_row)
        layout.addLayout(info_layout, 1)

    def _apply_status_style(self):
        """应用状态样式"""
        color, bg_color = self.STATUS_COLORS.get(
            self._status,
            self.STATUS_COLORS["idle"]
        )

        self.status_dot.setStyleSheet(f"color: {color}; font-size: 12px;")
        self.status_text_label.setStyleSheet(f"""
            color: {color};
            font-size: 16px;
            font-weight: bold;
        """)

        # 更新边框颜色
        self.setStyleSheet(f"""
            #statusCard {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(20, 50, 90, 0.9),
                    stop:1 rgba(10, 30, 60, 0.9)
                );
                border: 1px solid {color};
                border-radius: 8px;
            }}
        """)

    def set_status(self, status_text: str, status: str = "idle"):
        """设置状态"""
        self._status_text = status_text
        self._status = status
        self.status_text_label.setText(status_text)
        self._apply_status_style()

    def set_title(self, title: str):
        """设置标题"""
        self._title = title
        self.title_label.setText(title)

    def set_icon(self, icon: str):
        """设置图标"""
        self._icon = icon
        self.icon_label.setText(icon)


class AnimatedValueCard(DataCard):
    """
    带动画效果的数值卡片
    数值变化时有动画过渡效果
    """

    def __init__(self, title: str, value: float = 0, unit: str = "",
                 icon: str = "📊", decimals: int = 1, parent=None):
        self._numeric_value = value
        self._target_value = value
        self._decimals = decimals

        super().__init__(title, self._format_value(value), unit, icon, "normal", parent)

        # 动画定时器
        self._animation_timer = QTimer(self)
        self._animation_timer.timeout.connect(self._animate_value)

    def _format_value(self, value: float) -> str:
        """格式化数值"""
        if self._decimals == 0:
            return str(int(value))
        return f"{value:.{self._decimals}f}"

    def _animate_value(self):
        """动画更新数值"""
        diff = self._target_value - self._numeric_value

        if abs(diff) < 0.01:
            self._numeric_value = self._target_value
            self._animation_timer.stop()
        else:
            self._numeric_value += diff * 0.15

        self.value_label.setText(self._format_value(self._numeric_value))

    def set_numeric_value(self, value: float, animate: bool = True):
        """设置数值（带动画）"""
        self._target_value = value

        if animate:
            if not self._animation_timer.isActive():
                self._animation_timer.start(16)  # ~60fps
        else:
            self._numeric_value = value
            self.value_label.setText(self._format_value(value))

# ui/base_window.py
"""
基础窗口类 - 提供统一的窗口框架
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from datetime import datetime
from ui.styles.dark_theme import DARK_THEME


class BaseWindow(QMainWindow):
    """基础窗口类"""

    def __init__(self, title: str = "小嘉智能系统",
                 width: int = 1400, height: int = 900):
        super().__init__()

        self.setWindowTitle(title)
        self.setMinimumSize(width, height)
        self.resize(width, height)

        # 应用样式
        self.setStyleSheet(DARK_THEME)

        # 初始化UI
        self._setup_central_widget()
        self._setup_header()
        self._setup_main_area()
        self._setup_status_bar()
        self._setup_timer()

    def _setup_central_widget(self):
        """设置中央部件"""
        self.central_widget = QWidget()
        self.central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self.central_widget)

        self.root_layout = QVBoxLayout(self.central_widget)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

    def _setup_header(self):
        """设置顶部标题栏"""
        self.header = QFrame()
        self.header.setObjectName("headerFrame")
        self.header.setFixedHeight(70)

        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(25, 10, 25, 10)

        # 左侧：标题
        title_container = QVBoxLayout()
        title_container.setSpacing(2)

        self.title_label = QLabel("🏠 小嘉智能环境监控系统")
        self.title_label.setObjectName("titleLabel")
        title_container.addWidget(self.title_label)

        self.subtitle_label = QLabel("Smart Environment Monitoring System")
        self.subtitle_label.setObjectName("subtitleLabel")
        title_container.addWidget(self.subtitle_label)

        header_layout.addLayout(title_container)
        header_layout.addStretch()

        # 右侧：时间显示
        time_container = QVBoxLayout()
        time_container.setAlignment(Qt.AlignRight)

        self.date_label = QLabel()
        self.date_label.setObjectName("datetimeLabel")
        self.date_label.setAlignment(Qt.AlignRight)
        time_container.addWidget(self.date_label)

        self.time_label = QLabel()
        self.time_label.setObjectName("datetimeLabel")
        self.time_label.setAlignment(Qt.AlignRight)
        self.time_label.setStyleSheet("font-size: 20px;")
        time_container.addWidget(self.time_label)

        header_layout.addLayout(time_container)

        # 添加发光效果
        self._add_glow_effect(self.header, QColor(0, 200, 255, 50))

        self.root_layout.addWidget(self.header)

    def _setup_main_area(self):
        """设置主要内容区域 - 子类重写"""
        self.main_container = QFrame()
        self.main_layout = QHBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.root_layout.addWidget(self.main_container, 1)

    def _setup_status_bar(self):
        """设置底部状态栏"""
        self.status_frame = QFrame()
        self.status_frame.setObjectName("statusBar")
        self.status_frame.setFixedHeight(35)

        status_layout = QHBoxLayout(self.status_frame)
        status_layout.setContentsMargins(15, 0, 15, 0)

        # 左侧状态信息
        self.status_left = QLabel("🟢 系统运行正常")
        status_layout.addWidget(self.status_left)

        status_layout.addStretch()

        # 右侧信息
        self.status_right = QLabel("小嘉 v1.0.0")
        status_layout.addWidget(self.status_right)

        self.root_layout.addWidget(self.status_frame)

    def _setup_timer(self):
        """设置时间更新定时器"""
        self._update_datetime()
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_datetime)
        self.timer.start(1000)

    def _update_datetime(self):
        """更新日期时间显示"""
        now = datetime.now()
        self.date_label.setText(now.strftime("%Y年%m月%d日 %A"))
        self.time_label.setText(now.strftime("%H:%M:%S"))

    def _add_glow_effect(self, widget: QWidget, color: QColor):
        """添加发光效果"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(color)
        shadow.setOffset(0, 5)
        widget.setGraphicsEffect(shadow)

    def set_status(self, message: str, level: str = "info"):
        """
        设置状态栏消息
        level: info, success, warning, error
        """
        icons = {
            "info": "🔵",
            "success": "🟢",
            "warning": "🟡",
            "error": "🔴"
        }
        icon = icons.get(level, "🔵")
        self.status_left.setText(f"{icon} {message}")

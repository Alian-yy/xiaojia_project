# ui/pages/base_page.py
"""
页面基类 - 所有页面继承此类
A/B/C 三位同学都需要继承这个基类
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QScrollArea, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal


class BasePage(QWidget):
    """页面基类"""

    # 定义信号，用于向主窗口发送状态消息
    status_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("basePage")
        self._setup_base_layout()
        self.init_ui()  # 子类实现

    def _setup_base_layout(self):
        """设置基础布局"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 创建可滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
        """)

        # 内容容器
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(20)

        self.scroll_area.setWidget(self.content_widget)
        self.main_layout.addWidget(self.scroll_area)

    def init_ui(self):
        """
        初始化UI - 子类必须实现此方法
        """
        raise NotImplementedError("子类必须实现 init_ui 方法")

    def refresh_data(self):
        """
        刷新数据 - 子类可选实现
        当页面切换或点击刷新时调用
        """
        pass

    def cleanup(self):
        """
        清理资源 - 子类可选实现
        当窗口关闭时调用
        """
        pass

    # ==================== 便捷方法供子类使用 ====================

    def create_section_title(self, title: str, icon: str = "📌") -> QLabel:
        """
        创建区域标题
        用法: self.content_layout.addWidget(self.create_section_title("标题", "🎯"))
        """
        label = QLabel(f"{icon} {title}")
        label.setStyleSheet("""
            QLabel {
                color: #00d4ff;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 0;
                border-bottom: 2px solid qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00d4ff,
                    stop:0.3 #1a4a7a,
                    stop:1 transparent
                );
                margin-bottom: 5px;
            }
        """)
        return label

    def create_card_grid(self, columns: int = 4) -> tuple:
        """
        创建卡片网格布局
        返回: (container_frame, grid_layout)
        用法: container, grid = self.create_card_grid(4)
              grid.addWidget(card, row, col)
              self.content_layout.addWidget(container)
        """
        container = QFrame()
        container.setStyleSheet("background: transparent;")
        grid = QGridLayout(container)
        grid.setSpacing(15)
        grid.setContentsMargins(0, 0, 0, 0)
        return container, grid

    def create_panel(self, title: str = "", icon: str = "") -> tuple:
        """
        创建面板容器
        返回: (panel_frame, panel_layout)
        用法: panel, layout = self.create_panel("面板标题", "📊")
              layout.addWidget(some_widget)
              self.content_layout.addWidget(panel)
        """
        panel = QFrame()
        panel.setObjectName("dataCard")
        panel.setStyleSheet("""
            #dataCard {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(20, 50, 90, 0.9),
                    stop:1 rgba(10, 30, 60, 0.9)
                );
                border: 1px solid #1a4a7a;
                border-radius: 10px;
            }
            #dataCard:hover {
                border: 1px solid #2a6aaa;
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 如果有标题，添加标题栏
        if title:
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
            header_layout.setContentsMargins(15, 12, 15, 12)

            title_text = f"{icon} {title}" if icon else title
            title_label = QLabel(title_text)
            title_label.setStyleSheet("""
                color: #00d4ff;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            """)
            header_layout.addWidget(title_label)
            header_layout.addStretch()

            layout.addWidget(header)

        # 内容区域
        body = QFrame()
        body.setStyleSheet("background: transparent;")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(15, 15, 15, 15)
        body_layout.setSpacing(10)

        layout.addWidget(body)

        return panel, body_layout

    def create_row_layout(self, spacing: int = 15) -> QHBoxLayout:
        """
        创建水平行布局
        用法: row = self.create_row_layout()
              row.addWidget(widget1)
              row.addWidget(widget2)
        """
        row = QHBoxLayout()
        row.setSpacing(spacing)
        row.setContentsMargins(0, 0, 0, 0)
        return row

    def create_info_label(self, text: str, color: str = "#5588aa") -> QLabel:
        """创建信息标签"""
        label = QLabel(text)
        label.setStyleSheet(f"""
            color: {color};
            font-size: 12px;
        """)
        return label

    def create_value_label(self, value: str, size: int = 24,
                           color: str = "#00ffff") -> QLabel:
        """创建数值标签"""
        label = QLabel(value)
        label.setStyleSheet(f"""
            color: {color};
            font-size: {size}px;
            font-weight: bold;
        """)
        return label

    def send_status(self, message: str):
        """
        发送状态消息到主窗口状态栏
        用法: self.send_status("✅ 操作成功")
        """
        self.status_message.emit(message)

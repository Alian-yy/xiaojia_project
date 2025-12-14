# ui/pages/subscriber_page.py
"""
订阅界面 - B同学负责开发
"""

from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from .base_page import BasePage


class SubscriberPage(BasePage):
    """订阅界面（待B同学实现）"""

    def init_ui(self):
        """初始化UI"""
        # 标题
        self.content_layout.addWidget(
            self.create_section_title("数据订阅", "📥")
        )

        # 占位提示
        placeholder = QLabel("🚧 订阅界面开发中...\n\nB同学负责此页面开发")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                color: #5588aa;
                font-size: 18px;
                padding: 100px;
                background: rgba(20, 50, 90, 0.5);
                border: 2px dashed #1a4a7a;
                border-radius: 10px;
            }
        """)
        self.content_layout.addWidget(placeholder)
        self.content_layout.addStretch()

    def refresh_data(self):
        """刷新数据"""
        self.send_status("订阅页面已刷新")

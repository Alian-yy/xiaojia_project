# ui/pages/publisher_page.py
"""
发布界面 - A同学负责开发
"""

from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from .base_page import BasePage


class PublisherPage(BasePage):
    """发布界面（待A同学实现）"""

    def init_ui(self):
        """初始化UI"""
        # 标题
        self.content_layout.addWidget(
            self.create_section_title("消息发布", "📤")
        )

        # 占位提示
        placeholder = QLabel("🚧 发布界面开发中...\n\nA同学负责此页面开发")
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
        self.send_status("发布页面已刷新")

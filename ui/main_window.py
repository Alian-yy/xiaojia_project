# ui/main_window.py
"""
主窗口 - 组长负责
包含侧边栏导航和页面切换
"""

from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QPushButton,
    QStackedWidget, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt
from ui.base_window import BaseWindow

# 导入各个页面（由团队成员实现）
from ui.pages.publisher_page import PublisherPage
from ui.pages.subscriber_page import SubscriberPage
from ui.pages.analyzer_page import AnalyzerPage


class MainWindow(BaseWindow):
    """主窗口"""

    def __init__(self):
        super().__init__("小嘉智能环境监控系统", 1400, 900)
        self.nav_buttons = []
        self.pages = {}

        self._setup_sidebar()
        self._setup_content_area()
        self._setup_pages()

        # 默认选中第一个页面
        self.switch_page(0)

    def _setup_sidebar(self):
        """设置侧边栏"""
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebarFrame")
        self.sidebar.setFixedWidth(200)

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # 侧边栏标题
        sidebar_title = QLabel("📋 功能导航")
        sidebar_title.setObjectName("sidebarTitle")
        sidebar_layout.addWidget(sidebar_title)

        # 导航按钮配置
        nav_items = [
            ("📤 消息发布", "publisher", "A同学负责"),
            ("📥 数据订阅", "subscriber", "B同学负责"),
            ("📊 智能分析", "analyzer", "C同学负责"),
        ]

        # 创建导航按钮
        for index, (text, name, tooltip) in enumerate(nav_items):
            btn = QPushButton(text)
            btn.setProperty("class", "nav-btn")
            btn.setProperty("name", name)
            btn.setToolTip(tooltip)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, i=index: self.switch_page(i))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        # 添加分隔线
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background: #1a3a5c;")
        sidebar_layout.addWidget(separator)

        # 系统功能
        system_items = [
            ("⚙️ 系统设置", self._open_settings),
            ("🔄 刷新数据", self._refresh_current_page),
            ("❓ 帮助文档", self._open_help),
        ]

        for text, callback in system_items:
            btn = QPushButton(text)
            btn.setProperty("class", "nav-btn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(callback)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # 连接状态指示
        self.connection_status = QLabel("● MQTT 未连接")
        self.connection_status.setStyleSheet("""
            color: #ff5050;
            font-size: 11px;
            padding: 10px 15px;
            border-top: 1px solid #1a3a5c;
        """)
        sidebar_layout.addWidget(self.connection_status)

        # 底部用户信息
        bottom_info = QLabel("👤 管理员\n🕐 在线中")
        bottom_info.setStyleSheet("""
            color: #5588aa;
            font-size: 11px;
            padding: 15px;
            border-top: 1px solid #1a3a5c;
        """)
        sidebar_layout.addWidget(bottom_info)

        self.main_layout.addWidget(self.sidebar)

    def _setup_content_area(self):
        """设置内容区域"""
        self.content_area = QFrame()
        self.content_area.setStyleSheet("background: transparent;")

        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 页面堆叠容器
        self.page_stack = QStackedWidget()
        self.page_stack.setStyleSheet("background: transparent;")
        content_layout.addWidget(self.page_stack)

        self.main_layout.addWidget(self.content_area, 1)

    def _setup_pages(self):
        """初始化所有页面"""
        # 创建页面实例
        self.publisher_page = PublisherPage()
        self.subscriber_page = SubscriberPage()
        self.analyzer_page = AnalyzerPage()

        # 添加到堆叠容器
        self.page_stack.addWidget(self.publisher_page)
        self.page_stack.addWidget(self.subscriber_page)
        self.page_stack.addWidget(self.analyzer_page)

        # 保存页面引用
        self.pages = {
            0: self.publisher_page,
            1: self.subscriber_page,
            2: self.analyzer_page,
        }

        # 连接页面信号
        for page in self.pages.values():
            if hasattr(page, 'status_message'):
                page.status_message.connect(self._on_page_status)

    def switch_page(self, index: int):
        """切换页面"""
        # 更新按钮状态
        for i, btn in enumerate(self.nav_buttons):
            btn.setProperty("active", "true" if i == index else "false")
            btn.style().polish(btn)  # 刷新样式

        # 切换页面
        self.page_stack.setCurrentIndex(index)

        # 更新状态栏
        page_names = ["消息发布", "数据订阅", "智能分析"]
        self.set_status(f"当前页面：{page_names[index]}", "info")

        # 刷新页面数据
        if index in self.pages:
            page = self.pages[index]
            if hasattr(page, 'refresh_data'):
                page.refresh_data()

    def _on_page_status(self, message: str):
        """处理页面发送的状态消息"""
        if "错误" in message or "失败" in message or "❌" in message:
            self.set_status(message, "error")
        elif "警告" in message or "⚠️" in message:
            self.set_status(message, "warning")
        elif "成功" in message or "✅" in message:
            self.set_status(message, "success")
        else:
            self.set_status(message, "info")

    def _refresh_current_page(self):
        """刷新当前页面"""
        current_index = self.page_stack.currentIndex()
        if current_index in self.pages:
            page = self.pages[current_index]
            if hasattr(page, 'refresh_data'):
                page.refresh_data()
                self.set_status("数据已刷新", "success")

    def _open_settings(self):
        """打开设置"""
        QMessageBox.information(
            self, "系统设置",
            "设置功能开发中...\n\n可配置项：\n- MQTT服务器地址\n- 数据刷新频率\n- 主题配置"
        )

    def _open_help(self):
        """打开帮助"""
        QMessageBox.information(
            self, "帮助文档",
            "小嘉智能环境监控系统 v1.0\n\n"
            "功能说明：\n"
            "📤 消息发布 - 发布MQTT消息\n"
            "📥 数据订阅 - 订阅并接收消息\n"
            "📊 智能分析 - 数据分析和预测\n\n"
            "开发团队：A/B/C 同学"
        )

    def set_mqtt_connected(self, connected: bool):
        """设置MQTT连接状态"""
        if connected:
            self.connection_status.setText("● MQTT 已连接")
            self.connection_status.setStyleSheet("""
                color: #00ff88;
                font-size: 11px;
                padding: 10px 15px;
                border-top: 1px solid #1a3a5c;
            """)
        else:
            self.connection_status.setText("● MQTT 未连接")
            self.connection_status.setStyleSheet("""
                color: #ff5050;
                font-size: 11px;
                padding: 10px 15px;
                border-top: 1px solid #1a3a5c;
            """)

    def closeEvent(self, event):
        """窗口关闭事件"""
        reply = QMessageBox.question(
            self, "确认退出",
            "确定要退出系统吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # 清理资源
            for page in self.pages.values():
                if hasattr(page, 'cleanup'):
                    page.cleanup()
            event.accept()
        else:
            event.ignore()

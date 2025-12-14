# test_ui.py
"""
UI框架测试文件
运行此文件可预览整体界面效果
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.main_window import MainWindow


def main():
    # 高DPI支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    print("=" * 50)
    print("小嘉智能环境监控系统 - UI框架测试")
    print("=" * 50)
    print("✅ 框架加载成功！")
    print("")
    print("页面说明：")
    print("  📤 消息发布 - A同学负责开发")
    print("  📥 数据订阅 - B同学负责开发")
    print("  📊 智能分析 - C同学负责开发")
    print("=" * 50)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

# ui/styles/dark_theme.py
"""
工业看板深色主题样式
"""

DARK_THEME = """
/* ============ 全局样式 ============ */
QMainWindow, QWidget {
    background-color: #0a1628;
    color: #ffffff;
    font-family: "Microsoft YaHei", "Segoe UI", Arial;
}

#centralWidget {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #0a1628,
        stop:0.5 #0d1f3c,
        stop:1 #0a1628
    );
}

/* ============ 标题栏 ============ */
#headerFrame {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(0, 150, 255, 0.1),
        stop:0.5 rgba(0, 200, 255, 0.2),
        stop:1 rgba(0, 150, 255, 0.1)
    );
    border-bottom: 2px solid qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 transparent,
        stop:0.2 #00d4ff,
        stop:0.5 #00ffff,
        stop:0.8 #00d4ff,
        stop:1 transparent
    );
    min-height: 60px;
}

#titleLabel {
    color: #00ffff;
    font-size: 24px;
    font-weight: bold;
    letter-spacing: 3px;
}

#subtitleLabel {
    color: #5588aa;
    font-size: 11px;
}

#datetimeLabel {
    color: #00d4ff;
    font-size: 13px;
    font-weight: bold;
}

/* ============ 侧边栏 ============ */
#sidebarFrame {
    background: rgba(10, 30, 60, 0.95);
    border-right: 1px solid #1a3a5c;
}

#sidebarTitle {
    color: #00d4ff;
    font-size: 12px;
    font-weight: bold;
    padding: 15px 10px;
    border-bottom: 1px solid #1a3a5c;
}

/* 侧边栏导航按钮 */
QPushButton[class="nav-btn"] {
    background: transparent;
    color: #8899aa;
    border: none;
    border-left: 3px solid transparent;
    padding: 15px 20px;
    text-align: left;
    font-size: 13px;
}

QPushButton[class="nav-btn"]:hover {
    background: rgba(0, 200, 255, 0.1);
    color: #00d4ff;
    border-left: 3px solid #00d4ff;
}

QPushButton[class="nav-btn"][active="true"] {
    background: rgba(0, 200, 255, 0.15);
    color: #00ffff;
    border-left: 3px solid #00ffff;
}

/* ============ 数据卡片 ============ */
#dataCard {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(20, 50, 90, 0.9),
        stop:1 rgba(10, 30, 60, 0.9)
    );
    border: 1px solid #1a4a7a;
    border-radius: 8px;
}

#dataCard:hover {
    border: 1px solid #00d4ff;
}

#cardHeader {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(0, 150, 255, 0.3),
        stop:1 transparent
    );
    border-bottom: 1px solid #1a4a7a;
    border-radius: 8px 8px 0 0;
    padding: 10px 15px;
}

#cardTitle {
    color: #00d4ff;
    font-size: 13px;
    font-weight: bold;
}

#cardValue {
    color: #00ffff;
    font-size: 32px;
    font-weight: bold;
}

#cardUnit {
    color: #5588aa;
    font-size: 14px;
}

/* 状态指示器 */
#statusIndicator[status="normal"] {
    background: rgba(0, 255, 136, 0.2);
    color: #00ff88;
    border: 1px solid #00ff88;
    border-radius: 4px;
    padding: 2px 8px;
}

#statusIndicator[status="warning"] {
    background: rgba(255, 200, 0, 0.2);
    color: #ffc800;
    border: 1px solid #ffc800;
    border-radius: 4px;
    padding: 2px 8px;
}

#statusIndicator[status="error"] {
    background: rgba(255, 80, 80, 0.2);
    color: #ff5050;
    border: 1px solid #ff5050;
    border-radius: 4px;
    padding: 2px 8px;
}

/* ============ 按钮样式 ============ */
QPushButton {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #1a5a9a,
        stop:1 #0d3a6a
    );
    color: #ffffff;
    border: 1px solid #2a7acc;
    border-radius: 5px;
    padding: 8px 20px;
    font-weight: bold;
    font-size: 12px;
}

QPushButton:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #2a7acc,
        stop:1 #1a5a9a
    );
    border: 1px solid #00d4ff;
}

QPushButton:pressed {
    background: #0d3a6a;
}

QPushButton:disabled {
    background: #2a3a4a;
    color: #5a6a7a;
    border: 1px solid #3a4a5a;
}

/* 主要按钮 */
QPushButton[class="primary"] {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #00a0cc,
        stop:1 #0080aa
    );
    border: 1px solid #00d4ff;
}

/* 危险按钮 */
QPushButton[class="danger"] {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #aa3030,
        stop:1 #802020
    );
    border: 1px solid #ff5050;
}

/* ============ 输入框 ============ */
QLineEdit, QTextEdit, QPlainTextEdit {
    background: rgba(10, 30, 60, 0.8);
    border: 1px solid #1a4a7a;
    border-radius: 5px;
    padding: 8px 12px;
    color: #ffffff;
    selection-background-color: #00a0cc;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #00d4ff;
}

QLineEdit:disabled {
    background: rgba(30, 40, 50, 0.5);
    color: #5a6a7a;
}

/* ============ 下拉框 ============ */
QComboBox {
    background: rgba(10, 30, 60, 0.8);
    border: 1px solid #1a4a7a;
    border-radius: 5px;
    padding: 8px 12px;
    color: #ffffff;
    min-width: 120px;
}

QComboBox:hover {
    border: 1px solid #00d4ff;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #00d4ff;
    margin-right: 10px;
}

QComboBox QAbstractItemView {
    background: #0d1f3c;
    border: 1px solid #1a4a7a;
    selection-background-color: rgba(0, 200, 255, 0.3);
    color: #ffffff;
}

/* ============ 表格样式 ============ */
QTableWidget {
    background: rgba(10, 30, 60, 0.8);
    border: 1px solid #1a4a7a;
    border-radius: 8px;
    gridline-color: #1a3a5c;
}

QTableWidget::item {
    padding: 10px;
    border-bottom: 1px solid #1a3a5c;
}

QTableWidget::item:selected {
    background: rgba(0, 200, 255, 0.2);
}

QHeaderView::section {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #1a4a7a,
        stop:1 #0d2a4a
    );
    color: #00d4ff;
    padding: 12px;
    border: none;
    border-right: 1px solid #1a3a5c;
    border-bottom: 2px solid #00d4ff;
    font-weight: bold;
}

/* ============ 滚动条 ============ */
QScrollBar:vertical {
    background: #0a1628;
    width: 10px;
    border-radius: 5px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #1a4a7a;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #00d4ff;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background: #0a1628;
    height: 10px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background: #1a4a7a;
    border-radius: 5px;
    min-width: 30px;
}

/* ============ 进度条 ============ */
QProgressBar {
    background: rgba(0, 50, 100, 0.5);
    border: 1px solid #1a4a7a;
    border-radius: 5px;
    height: 10px;
    text-align: center;
    color: #ffffff;
}

QProgressBar::chunk {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #0066ff,
        stop:0.5 #00d4ff,
        stop:1 #00ffff
    );
    border-radius: 4px;
}

/* ============ 列表 ============ */
QListWidget {
    background: rgba(10, 30, 60, 0.5);
    border: 1px solid #1a4a7a;
    border-radius: 5px;
    outline: none;
}

QListWidget::item {
    padding: 10px;
    border-bottom: 1px solid #1a3a5c;
}

QListWidget::item:hover {
    background: rgba(0, 200, 255, 0.1);
}

QListWidget::item:selected {
    background: rgba(0, 200, 255, 0.2);
    color: #00ffff;
}

/* ============ 标签页 ============ */
QTabWidget::pane {
    border: 1px solid #1a4a7a;
    border-radius: 5px;
    background: rgba(10, 30, 60, 0.5);
}

QTabBar::tab {
    background: rgba(20, 50, 90, 0.8);
    color: #8899aa;
    padding: 10px 20px;
    border: 1px solid #1a4a7a;
    border-bottom: none;
    border-radius: 5px 5px 0 0;
}

QTabBar::tab:selected {
    background: rgba(0, 150, 255, 0.2);
    color: #00ffff;
    border-bottom: 2px solid #00d4ff;
}

/* ============ 状态栏 ============ */
#statusBar {
    background: rgba(10, 30, 60, 0.95);
    border-top: 1px solid #1a4a7a;
    min-height: 30px;
}

#statusBar QLabel {
    color: #5588aa;
    font-size: 11px;
    padding: 0 10px;
}

/* ============ 工具提示 ============ */
QToolTip {
    background: #0d1f3c;
    color: #ffffff;
    border: 1px solid #00d4ff;
    border-radius: 4px;
    padding: 5px 10px;
}
"""

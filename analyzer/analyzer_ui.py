# analyzer/analyzer_ui.py
"""
分析界面UI组件 - 使用已有的UI组件
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, 
    QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QComboBox, QGridLayout, QGroupBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from datetime import datetime
import numpy as np

# 使用已有的组件
from ui.widgets.gauge_widget import GaugeWidget, ProgressRing, DashboardGauge
from ui.widgets.chart_widget import LineChart, BarChart, PieChart


class ComfortGauge(DashboardGauge):
    """舒适度仪表盘 - 基于已有的DashboardGauge"""
    
    def __init__(self, title="舒适度", parent=None):
        super().__init__(title, 0, 100, "%", parent)
        # 设置舒适度阈值
        self.set_thresholds([
            (0.2, QColor(255, 80, 80), "非常不舒适"),
            (0.4, QColor(255, 120, 0), "不舒适"),
            (0.6, QColor(255, 200, 0), "一般"),
            (0.8, QColor(150, 220, 0), "舒适"),
            (1.0, QColor(0, 200, 136), "非常舒适")
        ])


class ComparisonChart(LineChart):
    """对比图表 - 基于已有的LineChart，显示实际值与上海市参考值"""
    
    def __init__(self, title="参数对比", parent=None):
        super().__init__(title, parent)
        # 可以设置不同的线颜色
        self.set_line_color(QColor(0, 200, 255))  # 实际值颜色
        self.reference_series = []  # 存储参考值
        self.actual_series = []     # 存储实际值
    
    def set_title(self, title: str):
        """设置图表标题"""
        # LineChart可能没有chart属性，所以我们需要重写这个方法
        if hasattr(self, 'title_label'):
            # 如果LineChart中有title_label，直接更新它
            self.title_label.setText(f"{title}")
        # 也可以尝试调用父类的方法
        try:
            super().set_title(title)
        except AttributeError:
            pass
    
    def update_comparison(self, actual_values: list, reference_values: list, months: list = None):
        """更新对比数据"""
        if not months:
            months = list(range(1, 13))
        
        # 暂时存储数据
        self.actual_series = list(zip(months, actual_values))
        self.reference_series = list(zip(months, reference_values))
        
        # 显示实际值（参考值需要特殊处理，因为LineChart只显示一条线）
        # 这里我们先显示实际值，参考值可以通过其他方式显示
        values = [v[1] for v in self.actual_series]
        self.set_data(values)
        
        # 更新标题 - 使用我们自己的方法
        self.set_title(f"{self.title} (实际值)")


class EventTable(QTableWidget):
    """事件表格"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["事件名称", "类型", "地点", "状态"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setStyleSheet("""
            QTableWidget {
                background: rgba(20, 40, 80, 0.8);
                gridline-color: #1a4a7a;
            }
            QTableWidget::item {
                padding: 5px;
                color: #dfe9f5;
            }
            QTableWidget::item:selected {
                background: rgba(0, 150, 255, 0.5);
            }
        """)
        
    def update_events(self, events: list):
        """更新事件列表"""
        self.setRowCount(len(events))
        
        for i, event in enumerate(events):
            self.setItem(i, 0, QTableWidgetItem(event.get("name", "")))
            self.setItem(i, 1, QTableWidgetItem(event.get("type", "")))
            self.setItem(i, 2, QTableWidgetItem(event.get("location", "")))
            
            # 状态列（根据优先级）
            priority = event.get("priority", 1)
            status_item = QTableWidgetItem()
            if priority >= 3:
                status_item.setText("高优先级")
                status_item.setForeground(QColor(255, 100, 100))
            elif priority >= 2:
                status_item.setText("进行中")
                status_item.setForeground(QColor(255, 200, 100))
            else:
                status_item.setText("正常")
                status_item.setForeground(QColor(100, 255, 100))
            self.setItem(i, 3, status_item)


class SmartAnalysisPanel(QFrame):
    """智能分析面板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("analysisPanel")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 标题
        title = QLabel("小嘉智能分析")
        title.setStyleSheet("""
            color: #00d4ff;
            font-size: 16px;
            font-weight: bold;
            padding-bottom: 10px;
            border-bottom: 1px solid #1a4a7a;
        """)
        layout.addWidget(title)
        
        # 舒适度仪表盘
        self.gauge = ComfortGauge()
        layout.addWidget(self.gauge, 0, Qt.AlignCenter)
        
        # 详细指标
        metrics_layout = QGridLayout()
        metrics_layout.setSpacing(10)
        
        self.label_thi = QLabel("THI指数: --")
        self.label_feels_like = QLabel("体感温度: --")
        self.label_score = QLabel("舒适度评分: --")
        self.label_level = QLabel("舒适等级: --")
        
        for label in [self.label_thi, self.label_feels_like, 
                     self.label_score, self.label_level]:
            label.setStyleSheet("color: #aaddff; font-size: 12px;")
        
        metrics_layout.addWidget(self.label_thi, 0, 0)
        metrics_layout.addWidget(self.label_feels_like, 0, 1)
        metrics_layout.addWidget(self.label_score, 1, 0)
        metrics_layout.addWidget(self.label_level, 1, 1)
        
        layout.addLayout(metrics_layout)
        
        # 分析建议
        self.label_suggestion = QLabel("等待分析数据...")
        self.label_suggestion.setWordWrap(True)
        self.label_suggestion.setStyleSheet("""
            color: #dfe9f5;
            font-size: 13px;
            padding: 10px;
            background: rgba(30, 60, 120, 0.5);
            border-radius: 5px;
            border: 1px solid #2a6aaa;
        """)
        layout.addWidget(self.label_suggestion)
        
        # 事件表格
        event_title = QLabel("校园事件匹配")
        event_title.setStyleSheet("color: #00d4ff; font-size: 14px; font-weight: bold;")
        layout.addWidget(event_title)
        
        self.event_table = EventTable()
        self.event_table.setMaximumHeight(150)
        layout.addWidget(self.event_table)
        
    def update_analysis(self, analysis_result: dict):
        """更新分析结果"""
        comfort = analysis_result.get("comfort_analysis", {})
        
        # 更新仪表盘
        if "comfort_score" in comfort:
            score = comfort["comfort_score"]
            self.gauge.set_value(score)
            self.gauge.set_status_text(comfort.get("comfort_level_cn", ""))
            
            # 更新指标
            self.label_thi.setText(f"THI指数: {comfort.get('thi', '--')}")
            self.label_feels_like.setText(f"体感温度: {comfort.get('feels_like', '--')}℃")
            self.label_score.setText(f"舒适度评分: {comfort.get('comfort_score', '--')}")
            self.label_level.setText(f"舒适等级: {comfort.get('comfort_level_cn', '--')}")
        
        # 更新建议
        suggestions = analysis_result.get("suggestions", [])
        if suggestions:
            self.label_suggestion.setText("建议: " + "；".join(suggestions[:3]))
        else:
            self.label_suggestion.setText("环境条件良好，无需特别调整。")
        
        # 更新事件表格
        events = analysis_result.get("matched_events", [])
        self.event_table.update_events(events)


__all__ = [
    "ComfortGauge", 
    "ComparisonChart", 
    "EventTable", 
    "SmartAnalysisPanel"
]
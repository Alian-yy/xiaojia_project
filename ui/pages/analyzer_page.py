# ui/pages/analyzer_page.py
"""
智能分析页面 - 只使用实时传感器数据，支持数据合并
适配publish_logic的消息格式，完善预测功能
"""

import sys
import os
from datetime import datetime
import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
    QPushButton, QGridLayout, QSplitter, QProgressBar,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor

from .base_page import BasePage
from ui.widgets.data_card import MiniCard, StatusCard
from ui.widgets.chart_widget import LineChart
from ui.widgets.gauge_widget import DashboardGauge


# ========== 添加分析模块路径 ==========
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
analyzer_path = os.path.join(project_root, "analyzer")

# 将analyzer模块路径添加到sys.path
if analyzer_path not in sys.path:
    sys.path.insert(0, analyzer_path)
    sys.path.insert(0, project_root)

# 尝试导入analyzer模块
try:
    from analyzer.predictor import XiaojiaBrain
    ANALYZER_AVAILABLE = True
except ImportError as e:
    ANALYZER_AVAILABLE = False


class AnalyzerWorker(QObject):
    """分析工作线程（非真正线程，只是避免在回调中更新UI）"""
    
    # 定义信号
    data_received = pyqtSignal(dict, str, str)  # 传感器数据，地点，传感器ID
    analysis_complete = pyqtSignal(dict)  # 分析完成
    
    def __init__(self):
        super().__init__()
        self.xiaojia_brain = None
        
    def init_brain(self):
        """初始化小嘉大脑"""
        try:
            self.xiaojia_brain = XiaojiaBrain()
            self.xiaojia_brain.set_realtime_callback(self._on_realtime_data)
            return True
        except Exception as e:
            return False
    
    def _on_realtime_data(self, sensor_data: dict, location: str, sensor_id: str):
        """实时数据回调 - 通过信号传递到主线程"""
        # 不在此处处理数据，只是转发信号
        self.data_received.emit(sensor_data, location, sensor_id)
    
    def process_data(self, sensor_data: dict, location: str = None, sensor_id: str = None):
        """处理数据"""
        try:
            if self.xiaojia_brain:
                result = self.xiaojia_brain.process_sensor_data(sensor_data, location, sensor_id)
                self.analysis_complete.emit(result)
        except Exception as e:
            pass


class ComfortGauge(DashboardGauge):
    """舒适度仪表盘"""
    
    def __init__(self, title="舒适度", parent=None):
        super().__init__(title, 0, 100, "%", parent)
        self.set_thresholds([
            (0.2, QColor(255, 80, 80), "非常不舒适"),
            (0.4, QColor(255, 120, 0), "不舒适"),
            (0.6, QColor(255, 200, 0), "一般"),
            (0.8, QColor(150, 220, 0), "舒适"),
            (1.0, QColor(0, 200, 136), "非常舒适")
        ])


class EnhancedLineChart(LineChart):
    """增强的折线图"""
    
    def __init__(self, title="图表", parent=None):
        super().__init__(title, parent)
        self.chart_title = title
        
    def set_title(self, title):
        self.chart_title = title
        if hasattr(self, 'title_label'):
            self.title_label.setText(f"📈 {title}")


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
        title = QLabel("🧠 小嘉智能分析")
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
            label.setStyleSheet("""
                color: #aaddff; 
                font-size: 12px;
                background: rgba(30, 60, 120, 0.3);
                padding: 6px 10px;
                border-radius: 4px;
            """)
        
        metrics_layout.addWidget(self.label_thi, 0, 0)
        metrics_layout.addWidget(self.label_feels_like, 0, 1)
        metrics_layout.addWidget(self.label_score, 1, 0)
        metrics_layout.addWidget(self.label_level, 1, 1)
        
        layout.addLayout(metrics_layout)
        
        # 分析建议
        self.label_suggestion = QLabel("等待实时传感器数据...")
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
        
        # 舒适度提示
        self.label_comfort_prompt = QLabel("")
        self.label_comfort_prompt.setWordWrap(True)
        self.label_comfort_prompt.setStyleSheet("""
            color: #ffd700;
            font-size: 14px;
            font-weight: bold;
            padding: 10px;
            background: rgba(255, 215, 0, 0.1);
            border-radius: 5px;
            border: 1px solid rgba(255, 215, 0, 0.3);
        """)
        layout.addWidget(self.label_comfort_prompt)
    
    def update_analysis(self, analysis_result: dict):
        """更新分析结果"""
        comfort = analysis_result.get("comfort_analysis", {})
        
        # 更新仪表盘
        if "comfort_score" in comfort:
            score = comfort["comfort_score"]
            self.gauge.set_value(score)
            
            # 更新指标
            self.label_thi.setText(f"THI指数: {comfort.get('thi', '--')}")
            self.label_feels_like.setText(f"体感温度: {comfort.get('feels_like', '--')}℃")
            self.label_score.setText(f"舒适度评分: {comfort.get('comfort_score', '--')}")
            self.label_level.setText(f"舒适等级: {comfort.get('comfort_level_cn', '--')}")
        
        # 更新舒适度提示
        comfort_prompt = analysis_result.get("comfort_prompt", "")
        self.label_comfort_prompt.setText(comfort_prompt)
        
        # 更新建议
        prediction_stats = analysis_result.get("prediction_stats", {})
        if prediction_stats:
            temp_count = prediction_stats.get("temperature_history", 0)
            window_size = prediction_stats.get("window_size", 20)
            prediction_ready = analysis_result.get("prediction_available", False)
            
            if prediction_ready:
                suggestion_text = "📊 预测功能已就绪，可查看未来趋势"
            else:
                suggestion_text = f"⏳ 数据收集中 ({temp_count}/{window_size})"
            
            self.label_suggestion.setText(suggestion_text)


class AnalyzerPage(BasePage):
    """分析界面 - 只使用实时数据，支持多源数据合并"""
    
    def __init__(self, parent=None):
        # 检查analyzer模块是否可用
        if not ANALYZER_AVAILABLE:
            raise ImportError("无法导入analyzer模块")
        
        # 初始化工作器
        self.worker = AnalyzerWorker()
        
        # 初始化定时器
        self.timer = QTimer()
        
        # 数据收集状态
        self.data_collection_status = {
            "temperature": False,
            "humidity": False,
            "pressure": False
        }
        
        # 数据收集计数
        self.data_collection_count = {
            "temperature": 0,
            "humidity": 0,
            "pressure": 0
        }
        
        # 预测状态
        self.prediction_ready = False
        
        # 调用父类初始化
        super().__init__(parent)
        
        # 连接信号
        self.worker.data_received.connect(self._on_data_received)
        self.worker.analysis_complete.connect(self._on_analysis_complete)
        
        # 设置定时器
        self.timer.timeout.connect(self._on_timer)
        
        # 初始化工作器
        success = self.worker.init_brain()
        if not success:
            raise RuntimeError("无法初始化分析引擎")
    
    @pyqtSlot(dict, str, str)
    def _on_data_received(self, sensor_data: dict, location: str, sensor_id: str):
        """接收到实时数据（在主线程中执行）"""
        # 更新数据收集状态
        if "temperature" in sensor_data:
            self.data_collection_status["temperature"] = True
            self.data_collection_count["temperature"] += 1
        if "humidity" in sensor_data:
            self.data_collection_status["humidity"] = True
            self.data_collection_count["humidity"] += 1
        if "pressure" in sensor_data:
            self.data_collection_status["pressure"] = True
            self.data_collection_count["pressure"] += 1
        
        # 更新数据收集状态显示
        self._update_data_collection_status()
        
        # 处理数据
        self.worker.process_data(sensor_data, location, sensor_id)
    
    @pyqtSlot(dict)
    def _on_analysis_complete(self, analysis_result: dict):
        """分析完成（在主线程中执行）"""
        # 更新UI
        self._update_ui_with_analysis(analysis_result)
        
        # 检查预测状态
        prediction_available = analysis_result.get("prediction_available", False)
        if not self.prediction_ready and prediction_available:
            self.prediction_ready = True
            self.send_status("🎯 已收集足够数据，预测功能已激活！")
    
    def _update_data_collection_status(self):
        """更新数据收集状态显示"""
        if hasattr(self, 'source_status_label') and self.source_status_label:
            # 计算已收集的数据类型
            collected = [k for k, v in self.data_collection_status.items() if v]
            
            if len(collected) == 3:
                status_text = "🟢 数据收集完成"
                status_style = """
                    QLabel {
                        color: #00ff88;
                        font-size: 13px;
                        padding: 5px 15px;
                        background: rgba(0, 255, 136, 0.1);
                        border-radius: 5px;
                        border: 1px solid rgba(0, 255, 136, 0.3);
                    }
                """
            elif len(collected) >= 2:
                status_text = "🟡 数据收集中"
                status_style = """
                    QLabel {
                        color: #ffaa00;
                        font-size: 13px;
                        padding: 5px 15px;
                        background: rgba(255, 170, 0, 0.1);
                        border-radius: 5px;
                        border: 1px solid rgba(255, 170, 0, 0.3);
                    }
                """
            else:
                status_text = "🔴 等待数据"
                status_style = """
                    QLabel {
                        color: #ff5555;
                        font-size: 13px;
                        padding: 5px 15px;
                        background: rgba(255, 85, 85, 0.1);
                        border-radius: 5px;
                        border: 1px solid rgba(255, 85, 85, 0.3);
                    }
                """
            
            # 添加详细状态和计数
            details = []
            for key in ["temperature", "humidity", "pressure"]:
                if self.data_collection_status[key]:
                    icon = "🌡️" if key == "temperature" else "💧" if key == "humidity" else "🌪️"
                    details.append(f"{icon}{self.data_collection_count[key]}")
                else:
                    details.append("❌")
            
            status_text += f" [{' '.join(details)}]"
            self.source_status_label.setText(status_text)
            self.source_status_label.setStyleSheet(status_style)
    
    def _on_timer(self):
        """定时器槽函数 - 检查是否有实时数据"""
        # 尝试获取最新的实时数据
        try:
            if hasattr(self.worker.xiaojia_brain, 'get_realtime_data'):
                realtime_data = self.worker.xiaojia_brain.get_realtime_data()
                if realtime_data:
                    # 更新数据收集状态
                    if "temperature" in realtime_data:
                        self.data_collection_status["temperature"] = True
                    if "humidity" in realtime_data:
                        self.data_collection_status["humidity"] = True
                    if "pressure" in realtime_data:
                        self.data_collection_status["pressure"] = True
                    
                    self._update_data_collection_status()
                    
                    self.worker.process_data(realtime_data)
        except Exception as e:
            # 忽略数据不完整的错误，定时器只是尝试处理
            if "传感器数据不完整" not in str(e):
                pass
    
    def init_ui(self):
        """初始化UI"""
        # 标题
        self.content_layout.addWidget(
            self.create_section_title("智能分析", "📊")
        )
        
        # 数据源状态指示
        source_status = QLabel("🟡 正在连接实时数据源...")
        source_status.setStyleSheet("""
            QLabel {
                color: #ffaa00;
                font-size: 13px;
                padding: 5px 15px;
                background: rgba(255, 170, 0, 0.1);
                border-radius: 5px;
                border: 1px solid rgba(255, 170, 0, 0.3);
            }
        """)
        self.content_layout.addWidget(source_status)
        self.source_status_label = source_status
        
        # 状态卡片行
        status_row = self.create_row_layout()
        
        # 创建状态卡片
        self.comfort_card = StatusCard("当前舒适度", "等待数据", "offline", "⏳")
        self.trend_card = MiniCard("温度趋势", "--")
        self.data_count_card = MiniCard("数据点数", "0")
        self.prediction_card = MiniCard("预测置信度", "--")
        
        status_row.addWidget(self.comfort_card)
        status_row.addWidget(self.trend_card)
        status_row.addWidget(self.data_count_card)
        status_row.addWidget(self.prediction_card)
        
        self.content_layout.addLayout(status_row)
        
        # 主要分析区域（左右分割）
        splitter = QSplitter(Qt.Horizontal)
        
        # ===== 左侧面板 =====
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        # 智能分析面板
        self.analysis_panel = SmartAnalysisPanel()
        left_layout.addWidget(self.analysis_panel)
        
        # 预测图表
        pred_panel, pred_layout = self.create_panel("趋势预测", "🔮")
        self.prediction_chart = EnhancedLineChart("温度预测")
        self.prediction_chart.setStyleSheet("background: rgba(20, 40, 80, 0.5); border-radius: 8px;")
        pred_layout.addWidget(self.prediction_chart)
        
        # 预测状态指示器
        pred_status_layout = QHBoxLayout()
        self.label_pred_status = QLabel("📊 数据收集中...")
        self.label_pred_status.setStyleSheet("color: #ffaa00; font-size: 12px;")
        pred_status_layout.addWidget(self.label_pred_status)
        pred_status_layout.addStretch()
        pred_layout.addLayout(pred_status_layout)
        
        # 上海参考值标签
        self.label_shanghai_ref = QLabel("📍 上海市本月参考温度: --")
        self.label_shanghai_ref.setStyleSheet("color: #aaddff; font-size: 12px; padding: 5px;")
        pred_layout.addWidget(self.label_shanghai_ref)
        
        left_layout.addWidget(pred_panel)
        
        splitter.addWidget(left_panel)
        
        # ===== 右侧面板 =====
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        
        # 历史数据对比图表
        comp_panel, comp_layout = self.create_panel("历史数据对比", "📈")
        
        # 对比图表控制
        control_row = QHBoxLayout()
        control_row.setSpacing(5)
        
        self.btn_temp = QPushButton("🌡️ 温度")
        self.btn_humid = QPushButton("💧 湿度")
        self.btn_pressure = QPushButton("🌪️ 气压")
        
        # 连接按钮信号
        self.btn_temp.clicked.connect(lambda: self._update_comparison_chart("temperature"))
        self.btn_humid.clicked.connect(lambda: self._update_comparison_chart("humidity"))
        self.btn_pressure.clicked.connect(lambda: self._update_comparison_chart("pressure"))
        
        # 设置按钮样式
        button_style = """
            QPushButton {
                background: rgba(0, 100, 200, 0.7);
                color: white;
                border: 1px solid #1a4a7a;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
                min-width: 60px;
            }
            QPushButton:hover {
                background: rgba(0, 150, 255, 0.9);
                border: 1px solid #2a6aaa;
            }
            QPushButton:pressed {
                background: rgba(0, 80, 160, 1.0);
            }
        """
        
        for btn in [self.btn_temp, self.btn_humid, self.btn_pressure]:
            btn.setStyleSheet(button_style)
        
        control_row.addWidget(self.btn_temp)
        control_row.addWidget(self.btn_humid)
        control_row.addWidget(self.btn_pressure)
        control_row.addStretch()
        
        comp_layout.addLayout(control_row)
        
        # 对比图表
        self.comparison_chart = EnhancedLineChart("历史数据")
        self.comparison_chart.setStyleSheet("background: rgba(20, 40, 80, 0.5); border-radius: 8px;")
        comp_layout.addWidget(self.comparison_chart)
        
        # 图表说明
        chart_info = QLabel("📊 图表显示最近30个数据点（采样显示），虚线为上海参考值")
        chart_info.setStyleSheet("color: #aaddff; font-size: 11px; padding: 5px;")
        comp_layout.addWidget(chart_info)
        
        right_layout.addWidget(comp_panel)
        
        # 详细统计
        stats_panel, stats_layout = self.create_panel("详细统计", "📊")
        
        # 统计网格
        stats_grid = QGridLayout()
        stats_grid.setSpacing(10)
        
        # 创建统计标签
        self.label_avg_temp = self._create_stat_label("平均温度", "--")
        self.label_std_temp = self._create_stat_label("温度标准差", "--")
        self.label_avg_humid = self._create_stat_label("平均湿度", "--")
        self.label_std_humid = self._create_stat_label("湿度标准差", "--")
        self.label_avg_pressure = self._create_stat_label("平均气压", "--")
        self.label_std_pressure = self._create_stat_label("气压标准差", "--")
        
        # 添加到网格
        stats_grid.addWidget(self.label_avg_temp, 0, 0)
        stats_grid.addWidget(self.label_std_temp, 0, 1)
        stats_grid.addWidget(self.label_avg_humid, 1, 0)
        stats_grid.addWidget(self.label_std_humid, 1, 1)
        stats_grid.addWidget(self.label_avg_pressure, 2, 0)
        stats_grid.addWidget(self.label_std_pressure, 2, 1)
        
        stats_layout.addLayout(stats_grid)
        right_layout.addWidget(stats_panel)
        
        # 上海市参考值
        ref_panel, ref_layout = self.create_panel("上海市参考值（本月）", "📍")
        ref_layout.setSpacing(8)
        
        # 参考值标签
        self.label_ref_temp = QLabel("🌡️ 参考温度: --")
        self.label_ref_humid = QLabel("💧 参考湿度: --")
        self.label_ref_pressure = QLabel("🌪️ 参考气压: --")
        
        for label in [self.label_ref_temp, self.label_ref_humid, self.label_ref_pressure]:
            label.setStyleSheet("""
                color: #aaddff; 
                font-size: 13px; 
                padding: 6px 10px;
                background: rgba(30, 60, 120, 0.3);
                border-radius: 4px;
            """)
        
        ref_layout.addWidget(self.label_ref_temp)
        ref_layout.addWidget(self.label_ref_humid)
        ref_layout.addWidget(self.label_ref_pressure)
        
        right_layout.addWidget(ref_panel)
        right_layout.addStretch()
        
        splitter.addWidget(right_panel)
        
        # 设置分割比例
        splitter.setSizes([600, 400])
        self.content_layout.addWidget(splitter)
        
        # 控制面板
        control_panel, control_layout = self.create_panel("分析控制", "🎮")
        ctrl_row = self.create_row_layout()
        ctrl_row.setSpacing(10)
        
        self.btn_start = QPushButton("▶ 开始分析")
        self.btn_stop = QPushButton("⏸ 暂停分析")
        self.btn_reset = QPushButton("🔄 重置数据")
        self.btn_manual_predict = QPushButton("📊 手动预测")
        
        # 连接按钮信号
        self.btn_start.clicked.connect(self._start_analysis)
        self.btn_stop.clicked.connect(self._stop_analysis)
        self.btn_reset.clicked.connect(self._reset_data)
        self.btn_manual_predict.clicked.connect(self._manual_predict)
        
        # 设置控制按钮样式
        ctrl_button_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 120, 220, 0.8),
                    stop:1 rgba(0, 80, 160, 0.9));
                color: white;
                border: 1px solid #1a4a7a;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                min-height: 35px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 150, 255, 0.9),
                    stop:1 rgba(0, 100, 200, 1.0));
                border: 1px solid #2a6aaa;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 80, 160, 1.0),
                    stop:1 rgba(0, 50, 120, 1.0));
            }
            QPushButton:disabled {
                background: rgba(100, 100, 100, 0.5);
                color: rgba(255, 255, 255, 0.5);
            }
        """
        
        for btn in [self.btn_start, self.btn_stop, self.btn_reset, self.btn_manual_predict]:
            btn.setStyleSheet(ctrl_button_style)
        
        ctrl_row.addWidget(self.btn_start)
        ctrl_row.addWidget(self.btn_stop)
        ctrl_row.addWidget(self.btn_reset)
        ctrl_row.addWidget(self.btn_manual_predict)
        ctrl_row.addStretch()
        
        control_layout.addLayout(ctrl_row)
        self.content_layout.addWidget(control_panel)
        self.content_layout.addStretch()
        
        # 初始化数据
        self._update_reference_values()
        self._update_comparison_chart("temperature")
        
        # 更新数据源状态
        self._update_data_collection_status()
        
        self.send_status("✅ 分析界面已初始化完成，等待传感器数据...")
        
        # 启动分析
        self._start_analysis()
    
    def _create_stat_label(self, name: str, value: str) -> QLabel:
        """创建统计标签"""
        label = QLabel(f"{name}: {value}")
        label.setStyleSheet("""
            QLabel {
                color: #aaddff;
                font-size: 12px;
                padding: 6px 10px;
                background: rgba(30, 60, 120, 0.3);
                border-radius: 4px;
                border: 1px solid rgba(40, 80, 160, 0.5);
            }
        """)
        label.setAlignment(Qt.AlignCenter)
        return label
    
    def _update_reference_values(self):
        """更新上海市参考值"""
        try:
            if hasattr(self.worker.xiaojia_brain, 'get_shanghai_reference'):
                ref_data = self.worker.xiaojia_brain.get_shanghai_reference()
                if ref_data:
                    self.label_ref_temp.setText(f"🌡️ 参考温度: {ref_data.get('temperature', 0):.1f}℃")
                    self.label_ref_humid.setText(f"💧 参考湿度: {ref_data.get('humidity', 0):.1f}%")
                    self.label_ref_pressure.setText(f"🌪️ 参考气压: {ref_data.get('pressure', 0):.1f}hPa")
                    
                    # 更新预测图表的参考值标签
                    self.label_shanghai_ref.setText(f"📍 上海市本月参考温度: {ref_data.get('temperature', 0):.1f}℃")
        except Exception as e:
            pass
    
    def _update_comparison_chart(self, data_type: str):
        """更新对比图表 - 显示实际数据和上海参考数据"""
        try:
            if hasattr(self.worker.xiaojia_brain, 'get_historical_data'):
                history = self.worker.xiaojia_brain.get_historical_data(data_type)
                if history and data_type in history:
                    data = history[data_type]
                    if data:
                        # 获取上海参考数据
                        ref_data = self.worker.xiaojia_brain.get_shanghai_reference()
                        
                        # 确定参考值
                        if data_type == "temperature":
                            ref_value = ref_data.get("temperature", 20.0)
                        elif data_type == "humidity":
                            ref_value = ref_data.get("humidity", 70.0)
                        elif data_type == "pressure":
                            ref_value = ref_data.get("pressure", 1013.0)
                        else:
                            ref_value = 0
                        
                        # 创建混合数据显示：实际数据 + 上海参考线
                        # 这里使用折线图的现有功能显示两条线
                        # 假设折线图支持显示参考线
                        mixed_data = []
                        
                        # 添加实际数据
                        for i, val in enumerate(data):
                            mixed_data.append(val)
                        
                        # 更新图表数据
                        self.comparison_chart.set_data(mixed_data)
                        
                        # 设置参考线（如果折线图支持）
                        try:
                            # 尝试设置参考线
                            if hasattr(self.comparison_chart, 'set_reference_line'):
                                self.comparison_chart.set_reference_line(ref_value)
                        except:
                            pass
                        
                        # 更新标题
                        titles = {
                            "temperature": "温度历史数据",
                            "humidity": "湿度历史数据", 
                            "pressure": "气压历史数据"
                        }
                        title = titles.get(data_type, f"{data_type}历史数据")
                        
                        # 添加参考值信息到标题
                        if data_type == "temperature":
                            unit = "℃"
                        elif data_type == "humidity":
                            unit = "%"
                        elif data_type == "pressure":
                            unit = "hPa"
                        else:
                            unit = ""
                        
                        self.comparison_chart.set_title(f"{title} (上海参考: {ref_value:.1f}{unit})")
                        
                        # 更新按钮状态
                        self._update_button_state(data_type, True)
                    else:
                        self.comparison_chart.set_data([])
                        self.comparison_chart.set_title(f"{data_type}历史数据 (无数据)")
                        self._update_button_state(data_type, False)
        except Exception as e:
            self._update_button_state(data_type, False)
    
    def _update_button_state(self, active_type: str, has_data: bool):
        """更新按钮状态"""
        buttons = {
            "temperature": self.btn_temp,
            "humidity": self.btn_humid,
            "pressure": self.btn_pressure
        }
        
        for data_type, button in buttons.items():
            if data_type == active_type:
                button.setStyleSheet("""
                    QPushButton {
                        background: rgba(0, 200, 255, 0.9);
                        color: white;
                        border: 1px solid #00d4ff;
                        padding: 6px 12px;
                        border-radius: 4px;
                        font-size: 12px;
                        min-width: 60px;
                    }
                """)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        background: rgba(0, 100, 200, 0.7);
                        color: white;
                        border: 1px solid #1a4a7a;
                        padding: 6px 12px;
                        border-radius: 4px;
                        font-size: 12px;
                        min-width: 60px;
                    }
                    QPushButton:hover {
                        background: rgba(0, 150, 255, 0.9);
                        border: 1px solid #2a6aaa;
                    }
                """)
            
            if not has_data and data_type == active_type:
                button.setStyleSheet("""
                    QPushButton {
                        background: rgba(255, 100, 100, 0.7);
                        color: white;
                        border: 1px solid #ff5555;
                        padding: 6px 12px;
                        border-radius: 4px;
                        font-size: 12px;
                        min-width: 60px;
                    }
                """)
    
    def _update_ui_with_analysis(self, analysis_result: dict):
        """使用分析结果更新UI"""
        try:
            # 1. 更新智能分析面板
            if hasattr(self, 'analysis_panel') and self.analysis_panel:
                self.analysis_panel.update_analysis(analysis_result)
            
            # 2. 更新状态卡片
            comfort = analysis_result.get("comfort_analysis", {})
            if comfort and "comfort_score" in comfort:
                score = comfort["comfort_score"]
                level = comfort.get("comfort_level_cn", "一般")
                
                # 根据分数确定状态
                if score >= 80:
                    status = "online"
                    display_text = f"😊 {score:.1f}分"
                elif score >= 60:
                    status = "online"
                    display_text = f"🙂 {score:.1f}分"
                elif score >= 40:
                    status = "warning"
                    display_text = f"😐 {score:.1f}分"
                else:
                    status = "error"
                    display_text = f"😟 {score:.1f}分"
                
                # 更新舒适度卡片
                self.comfort_card.set_status(display_text, status)
            
            # 3. 更新趋势卡片
            try:
                if hasattr(self.worker.xiaojia_brain, 'get_trend_analysis'):
                    trend = self.worker.xiaojia_brain.get_trend_analysis()
                    trend_text = trend.get("temperature_trend", "stable")
                    if trend_text == "rising":
                        self.trend_card.set_value("↗ 上升")
                    elif trend_text == "falling":
                        self.trend_card.set_value("↘ 下降")
                    else:
                        self.trend_card.set_value("→ 稳定")
            except:
                self.trend_card.set_value("→ 稳定")
            
            # 4. 更新数据点数卡片
            prediction_stats = analysis_result.get("prediction_stats", {})
            temp_count = prediction_stats.get("temperature_history", 0)
            self.data_count_card.set_value(str(temp_count))
            
            # 5. 更新预测卡片和图表
            prediction_result = analysis_result.get("prediction_result", {})
            if prediction_result:
                confidence = prediction_result.get("confidence", 0) * 100
                self.prediction_card.set_value(f"{confidence:.0f}%")
                
                # 更新预测状态标签
                has_sufficient_data = prediction_result.get("has_enough_data", False)
                prediction_type = prediction_result.get("prediction_type", "简单预测")
                
                if has_sufficient_data:
                    self.label_pred_status.setText(f"📊 {prediction_type} | 置信度: {confidence:.0f}%")
                    self.label_pred_status.setStyleSheet("color: #00ff88; font-size: 12px;")
                else:
                    data_count = prediction_stats.get("temperature_history", 0)
                    window_size = prediction_stats.get("window_size", 20)
                    self.label_pred_status.setText(f"⏳ {prediction_type} ({data_count}/{window_size})")
                    self.label_pred_status.setStyleSheet("color: #ffaa00; font-size: 12px;")
                
                # 更新预测图表
                if "predictions" in prediction_result and self.prediction_chart:
                    pred_data = prediction_result["predictions"]
                    if pred_data:
                        self.prediction_chart.set_data(pred_data)
                        
                        # 获取上海参考值
                        shanghai_ref = prediction_result.get("shanghai_reference", 20.0)
                        
                        # 设置图表标题
                        self.prediction_chart.set_title(f"温度预测 (基于20个历史点)")
                        
                        # 更新上海参考标签
                        self.label_shanghai_ref.setText(f"📍 上海参考温度: {shanghai_ref:.1f}℃")
                        
                        # 尝试设置参考线
                        try:
                            if hasattr(self.prediction_chart, 'set_reference_line'):
                                self.prediction_chart.set_reference_line(shanghai_ref)
                        except:
                            pass
            
            # 6. 更新统计信息
            try:
                if hasattr(self.worker.xiaojia_brain, 'get_comfort_statistics'):
                    stats = self.worker.xiaojia_brain.get_comfort_statistics()
                    if stats:
                        self.label_avg_temp.setText(f"平均温度: {stats.get('temperature_avg', 0):.1f}℃")
                        self.label_std_temp.setText(f"温度标准差: {stats.get('temperature_std', 0):.2f}")
                        self.label_avg_humid.setText(f"平均湿度: {stats.get('humidity_avg', 0):.1f}%")
                        self.label_std_humid.setText(f"湿度标准差: {stats.get('humidity_std', 0):.2f}")
                        self.label_avg_pressure.setText(f"平均气压: {stats.get('pressure_avg', 0):.1f}hPa")
                        self.label_std_pressure.setText(f"气压标准差: {stats.get('pressure_std', 0):.2f}")
            except Exception as e:
                pass
            
            # 7. 发送状态消息
            comfort_prompt = analysis_result.get("comfort_prompt", "")
            if comfort_prompt:
                self.send_status(f"🤖 {comfort_prompt}")
            
            # 8. 更新对比图表
            self._update_comparison_chart("temperature")
            
        except Exception as e:
            pass
    
    def _start_analysis(self):
        """开始分析"""
        if not self.timer.isActive():
            self.timer.start(5000)  # 5秒更新一次
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
            self.send_status("▶ 开始实时分析")
    
    def _stop_analysis(self):
        """暂停分析"""
        if self.timer.isActive():
            self.timer.stop()
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.send_status("⏸ 暂停实时分析")
    
    def _reset_data(self):
        """重置数据"""
        # 重置小嘉大脑
        if hasattr(self.worker.xiaojia_brain, 'reset_predictor'):
            self.worker.xiaojia_brain.reset_predictor()
        
        # 重置UI
        self.comfort_card.set_status("等待数据", "offline")
        self.trend_card.set_value("--")
        self.data_count_card.set_value("0")
        self.prediction_card.set_value("--")
        self.label_pred_status.setText("📊 数据收集中...")
        self.label_pred_status.setStyleSheet("color: #ffaa00; font-size: 12px;")
        self.label_shanghai_ref.setText("📍 上海市本月参考温度: --")
        
        # 重置图表数据
        if hasattr(self, 'prediction_chart'):
            try:
                self.prediction_chart.set_data([])
                self.prediction_chart.set_title("温度预测")
            except:
                pass
        
        if hasattr(self, 'comparison_chart'):
            try:
                self.comparison_chart.set_data([])
                self.comparison_chart.set_title("温度历史")
            except:
                pass
        
        # 重置统计信息为默认值
        self.label_avg_temp.setText("平均温度: --")
        self.label_std_temp.setText("温度标准差: --")
        self.label_avg_humid.setText("平均湿度: --")
        self.label_std_humid.setText("湿度标准差: --")
        self.label_avg_pressure.setText("平均气压: --")
        self.label_std_pressure.setText("气压标准差: --")
        
        # 重置数据收集状态
        self.data_collection_status = {
            "temperature": False,
            "humidity": False,
            "pressure": False
        }
        
        self.data_collection_count = {
            "temperature": 0,
            "humidity": 0,
            "pressure": 0
        }
        
        self.prediction_ready = False
        
        # 更新参考值
        self._update_reference_values()
        
        # 重置数据接收标志
        self._update_data_collection_status()
        
        self.send_status("🔄 分析数据已重置")
    
    def _manual_predict(self):
        """手动触发预测"""
        try:
            if hasattr(self.worker.xiaojia_brain, 'predict_next'):
                prediction = self.worker.xiaojia_brain.predict_next(5)
                
                # 显示预测结果
                confidence = prediction.get("confidence", 0) * 100
                pred_values = prediction.get("predictions", [])
                timestamps = prediction.get("timestamps", [])
                prediction_type = prediction.get("prediction_type", "手动预测")
                
                if pred_values and timestamps:
                    pred_text = f"📊 {prediction_type}结果 (置信度: {confidence:.0f}%):\n"
                    for i, (ts, temp) in enumerate(zip(timestamps, pred_values)):
                        pred_text += f"  {ts}: {temp:.1f}℃\n"
                    
                    self.send_status(pred_text.strip())
                    
                    # 更新图表
                    if hasattr(self, 'prediction_chart') and self.prediction_chart:
                        self.prediction_chart.set_data(pred_values)
                        self.prediction_chart.set_title(f"手动预测 ({prediction_type})")
                else:
                    self.send_status("⚠️ 预测数据不完整")
        except Exception as e:
            self.send_status(f"❌ 手动预测失败")
    
    def refresh_data(self):
        """刷新数据"""
        self._update_reference_values()
        self._update_comparison_chart("temperature")
        self.send_status("✅ 分析页面已刷新")
    
    def cleanup(self):
        """清理资源"""
        if self.timer and self.timer.isActive():
            self.timer.stop()
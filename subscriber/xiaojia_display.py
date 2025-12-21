# subscriber/xiaojia_display.py
# "小嘉播报"小组件 - 增强版

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer


class XiaojiaDisplay(QFrame):
    """显示小嘉提示与表情的区域 - 增强版，更显眼更美观"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("xiaojiaDisplay")
        self.current_mood = "normal"
        self._glow_opacity = 0.5
        self._setup_ui()
        self._setup_anim()
        self._setup_glow_timer()

    def _setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        # 顶部标题栏
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)
        
        self.title_icon = QLabel("🤖")
        self.title_icon.setStyleSheet("font-size: 24px; background: transparent;")
        self.title_icon.setAlignment(Qt.AlignCenter)
        
        self.title = QLabel("小嘉智能助手")
        self.title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.title.setStyleSheet("""
            color: #00d4ff;
            font-size: 16px;
            font-weight: bold;
            background: transparent;
            letter-spacing: 1px;
        """)
        
        title_layout.addWidget(self.title_icon)
        title_layout.addWidget(self.title)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        # 头像和状态区域（水平布局）
        avatar_layout = QHBoxLayout()
        avatar_layout.setSpacing(15)

        # 左侧：大号头像区域
        self.avatar_frame = QFrame()
        self.avatar_frame.setObjectName("avatarFrame")
        self.avatar_frame.setFixedSize(80, 80)
        avatar_inner_layout = QVBoxLayout(self.avatar_frame)
        avatar_inner_layout.setContentsMargins(0, 0, 0, 0)
        avatar_inner_layout.setAlignment(Qt.AlignCenter)
        
        self.avatar_label = QLabel("🤖")
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.avatar_label.setStyleSheet("font-size: 48px; background: transparent;")
        avatar_inner_layout.addWidget(self.avatar_label)
        
        avatar_layout.addWidget(self.avatar_frame)

        # 右侧：状态信息
        status_layout = QVBoxLayout()
        status_layout.setSpacing(8)
        
        self.mood_label = QLabel("🙂 状态正常")
        self.mood_label.setStyleSheet("""
            color: #00ff88;
            font-size: 18px;
            font-weight: bold;
            background: transparent;
        """)
        
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("""
            color: #00ff88;
            font-size: 12px;
            background: transparent;
        """)
        self.status_indicator.setAlignment(Qt.AlignLeft)
        
        status_layout.addWidget(self.mood_label)
        status_layout.addWidget(self.status_indicator)
        status_layout.addStretch()
        
        avatar_layout.addLayout(status_layout, 1)
        layout.addLayout(avatar_layout)

        # 提示信息区域
        tip_frame = QFrame()
        tip_frame.setObjectName("tipFrame")
        tip_layout = QVBoxLayout(tip_frame)
        tip_layout.setContentsMargins(12, 10, 12, 10)
        
        self.tip_label = QLabel("等待订阅数据...")
        self.tip_label.setWordWrap(True)
        self.tip_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.tip_label.setStyleSheet("""
            color: #dfe9f5;
            font-size: 13px;
            line-height: 1.5;
            background: transparent;
        """)
        
        tip_layout.addWidget(self.tip_label)
        layout.addWidget(tip_frame)

        # 初始样式
        self._update_style("normal")

    def _setup_anim(self):
        """设置动画效果"""
        # 提示文字淡入动画
        self._fade = QPropertyAnimation(self.tip_label, b"windowOpacity")
        self._fade.setDuration(400)
        self._fade.setEasingCurve(QEasingCurve.OutCubic)
        
        # 头像缩放动画
        self._avatar_scale = QPropertyAnimation(self.avatar_frame, b"geometry")
        self._avatar_scale.setDuration(300)
        self._avatar_scale.setEasingCurve(QEasingCurve.OutBack)

    def _setup_glow_timer(self):
        """设置呼吸灯效果定时器"""
        self._glow_timer = QTimer()
        self._glow_timer.timeout.connect(self._update_glow)
        self._glow_timer.start(50)  # 每50ms更新一次
        self._glow_direction = 1

    def _update_glow(self):
        """更新发光效果"""
        if self.current_mood == "normal":
            # 正常状态：缓慢呼吸
            self._glow_opacity += 0.02 * self._glow_direction
            if self._glow_opacity >= 0.7:
                self._glow_direction = -1
            elif self._glow_opacity <= 0.3:
                self._glow_direction = 1
        elif self.current_mood in ["hot", "humid", "cold"]:
            # 警告状态：快速闪烁
            self._glow_opacity += 0.05 * self._glow_direction
            if self._glow_opacity >= 0.9:
                self._glow_direction = -1
            elif self._glow_opacity <= 0.4:
                self._glow_direction = 1
        
        self._update_style(self.current_mood)

    def _update_style(self, mood: str):
        """根据状态更新样式"""
        self.current_mood = mood
        
        # 计算当前发光颜色
        glow_alpha = int(self._glow_opacity * 255)
        
        # 状态配置
        mood_configs = {
            "normal": {
                "bg": "rgba(0, 150, 100, 0.15)",
                "border": "#00ff88",
                "glow_rgb": (0, 255, 136),
                "avatar": "🤖",
                "mood_text": "🙂 状态正常",
                "mood_color": "#00ff88",
                "tip_bg": "rgba(0, 100, 80, 0.2)",
            },
            "hot": {
                "bg": "rgba(255, 150, 0, 0.2)",
                "border": "#ff8800",
                "glow_rgb": (255, 136, 0),
                "avatar": "🥵",
                "mood_text": "🥵 温度偏高",
                "mood_color": "#ff8800",
                "tip_bg": "rgba(150, 80, 0, 0.25)",
            },
            "humid": {
                "bg": "rgba(100, 150, 255, 0.2)",
                "border": "#6496ff",
                "glow_rgb": (100, 150, 255),
                "avatar": "🌧️",
                "mood_text": "🌧️ 湿度过高",
                "mood_color": "#6496ff",
                "tip_bg": "rgba(50, 80, 150, 0.25)",
            },
            "cold": {
                "bg": "rgba(100, 180, 255, 0.2)",
                "border": "#64b4ff",
                "glow_rgb": (100, 180, 255),
                "avatar": "🥶",
                "mood_text": "🥶 温度偏低",
                "mood_color": "#64b4ff",
                "tip_bg": "rgba(50, 100, 150, 0.25)",
            },
        }
        
        config = mood_configs.get(mood, mood_configs["normal"])
        r, g, b = config["glow_rgb"]
        glow_color = f"rgba({r}, {g}, {b}, {glow_alpha})"
        
        # 更新主容器样式（带发光边框）
        self.setStyleSheet(f"""
            #xiaojiaDisplay {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 {config['bg']},
                    stop:1 rgba(20, 50, 90, 0.85)
                );
                border: 2px solid {config['border']};
                border-radius: 15px;
            }}
            #xiaojiaDisplay::hover {{
                border: 2px solid {glow_color};
            }}
            #avatarFrame {{
                background: qradialgradient(
                    cx:0.5, cy:0.5,
                    radius:1.0,
                    stop:0 {glow_color},
                    stop:0.5 rgba(0, 0, 0, 0),
                    stop:1 rgba(0, 0, 0, 0)
                );
                border: 2px solid {config['border']};
                border-radius: 40px;
            }}
            #tipFrame {{
                background: {config['tip_bg']};
                border: 1px solid {config['border']};
                border-radius: 8px;
            }}
        """)
        
        # 更新头像
        self.avatar_label.setText(config["avatar"])
        
        # 更新状态文字
        self.mood_label.setText(config["mood_text"])
        self.mood_label.setStyleSheet(f"""
            color: {config['mood_color']};
            font-size: 18px;
            font-weight: bold;
            background: transparent;
        """)
        
        # 更新状态指示器
        self.status_indicator.setStyleSheet(f"""
            color: {config['mood_color']};
            font-size: 12px;
            background: transparent;
        """)
        
        # 更新标题图标颜色
        self.title_icon.setText(config["avatar"])

    def set_tip(self, text: str, mood: str = "normal"):
        """设置提示信息"""
        # 更新状态样式
        self._update_style(mood)
        
        # 更新提示文字
        self.tip_label.setText(text)
        
        # 触发头像缩放动画
        current_geom = self.avatar_frame.geometry()
        self._avatar_scale.stop()
        self._avatar_scale.setStartValue(current_geom)
        # 轻微放大再恢复
        expanded = current_geom.adjusted(-5, -5, 5, 5)
        self._avatar_scale.setKeyValueAt(0.5, expanded)
        self._avatar_scale.setEndValue(current_geom)
        self._avatar_scale.start()
        
        # 提示文字淡入动画
        self._fade.stop()
        self.tip_label.setWindowOpacity(0.0)
        self._fade.setStartValue(0.0)
        self._fade.setEndValue(1.0)
        self._fade.start()


__all__ = ["XiaojiaDisplay"]

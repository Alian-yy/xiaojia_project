# subscriber/xiaojia_display.py
# “小嘉播报”小组件

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QPropertyAnimation, QByteArray


class XiaojiaDisplay(QFrame):
    """显示小嘉提示与表情的区域。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("xiaojiaDisplay")
        self._setup_ui()
        self._setup_anim()

    def _setup_ui(self):
        self.setStyleSheet("""
            #xiaojiaDisplay {
                background: rgba(20, 50, 90, 0.85);
                border: 1px solid #1a4a7a;
                border-radius: 10px;
            }
            #xiaojiaDisplay QLabel {
                background: transparent;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(6)

        self.title = QLabel("🤖 小嘉播报")
        self.title.setAlignment(Qt.AlignLeft)
        self.title.setStyleSheet("color: #00d4ff; font-size: 14px; font-weight: bold;")

        self.mood_label = QLabel("🙂 正常")
        self.mood_label.setStyleSheet("color: #aaddff; font-size: 12px;")

        self.tip_label = QLabel("等待订阅数据...")
        self.tip_label.setWordWrap(True)
        self.tip_label.setStyleSheet("color: #dfe9f5; font-size: 12px;")

        layout.addWidget(self.title)
        layout.addWidget(self.mood_label)
        layout.addWidget(self.tip_label)
        layout.addStretch()

    def _setup_anim(self):
        self._fade = QPropertyAnimation(self.tip_label, b"windowOpacity")
        self._fade.setDuration(300)

    def set_tip(self, text: str, mood: str = "normal"):
        mood_map = {
            "hot": "🥵 炎热",
            "humid": "🌧️ 潮湿",
            "cold": "🥶 偏冷",
            "normal": "🙂 正常",
        }
        mood_text = mood_map.get(mood, "🙂 正常")
        self.mood_label.setText(mood_text)
        self.tip_label.setText(text)

        # 轻微淡入效果
        self._fade.stop()
        self.tip_label.setWindowOpacity(0.0)
        self._fade.setStartValue(0.0)
        self._fade.setEndValue(1.0)
        self._fade.start()


__all__ = ["XiaojiaDisplay"]

# publisher/publish_logic.py
# MQTT 发布端逻辑封装，供 GUI 调用

import json
import threading
import time
from pathlib import Path
from typing import Callable, Optional

import paho.mqtt.client as mqtt


class PublisherLogic:
    """封装 paho-mqtt 发布端，提供数据发布接口"""

    def __init__(self,
                 broker: str = "127.0.0.1",
                 port: int = 1883,
                 keepalive: int = 60):
        self.broker = broker
        self.port = port
        self.keepalive = keepalive

        # 数据文件路径
        self.base_dir = Path(__file__).parent
        self.files = {
            "temperature": self.base_dir / "temperature.txt",
            "humidity": self.base_dir / "humidity.txt",
            "pressure": self.base_dir / "pressure.txt",
        }

        # 传感器配置
        self.sensor_id = "JX_Teach_01"
        self.location = "教学楼A"
        self.extra = "三楼301教室"

        self._client: Optional[mqtt.Client] = None
        self._publish_thread: Optional[threading.Thread] = None
        self._stop_flag = False
        self._connected = False
        self._lock = threading.Lock()

        # 发布过滤：默认发布全部类型，可通过控制主题动态调整
        self.enabled_types = {"temperature", "humidity", "pressure"}

        # 回调
        self._on_message_cb: Optional[Callable[[str, dict], None]] = None
        self._on_connection_cb: Optional[Callable[[bool], None]] = None
        self._on_publish_complete_cb: Optional[Callable, None] = None

    # -------- 对外接口 --------
    def set_on_message(self, callback: Callable[[str, dict], None]):
        """设置消息发布回调，参数为 (topic, payload_dict)"""
        self._on_message_cb = callback

    def set_on_connection(self, callback: Callable[[bool], None]):
        """设置连接状态回调，参数为 True/False"""
        self._on_connection_cb = callback

    def set_on_publish_complete(self, callback: Callable):
        """设置发布完成回调"""
        self._on_publish_complete_cb = callback

    def set_sensor_config(self, sensor_id: str, location: str, extra: str = ""):
        """设置传感器配置"""
        self.sensor_id = sensor_id
        self.location = location
        self.extra = extra

    def connect(self) -> bool:
        """连接到 MQTT Broker"""
        try:
            with self._lock:
                if self._connected:
                    return True
                self._client = mqtt.Client()
                self._client.on_connect = self._on_connect
                self._client.on_disconnect = self._on_disconnect
                self._client.on_message = self._on_message
                self._client.connect(self.broker, self.port, self.keepalive)
                self._client.loop_start()
                return True
        except Exception as e:
            print(f"连接失败: {e}")
            return False

    def disconnect(self):
        """断开连接"""
        with self._lock:
            self._stop_flag = True
            if self._client and self._connected:
                self._client.loop_stop()
                self._client.disconnect()
                self._connected = False

    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._connected

    def publish_single(self, data_type: str, value: float, timestamp: str = None) -> bool:
        """发布单条消息"""
        if not self._connected:
            return False

        # 过滤未启用的数据类型
        if data_type not in self.enabled_types:
            return True  # 视为成功但不实际发布，便于统一流程

        if timestamp is None:
            from datetime import datetime
            timestamp = datetime.now().isoformat()

        payload = {
            "timestamp": timestamp,
            "value": value,
            "sensor_id": self.sensor_id,
            "location": self.location,
            "extra": self.extra,
            "type": data_type,
        }
        topic = f"sensor/{data_type}"
        
        try:
            self._client.publish(topic, json.dumps(payload, ensure_ascii=False))
            if self._on_message_cb:
                self._on_message_cb(topic, payload)
            return True
        except Exception as e:
            print(f"发布失败: {e}")
            return False

    def start_publish_from_files(self, interval: float = 0.2):
        """从文件读取数据并开始发布（后台线程）"""
        if self._publish_thread and self._publish_thread.is_alive():
            return False

        self._stop_flag = False
        self._publish_thread = threading.Thread(
            target=self._publish_worker,
            args=(interval,),
            daemon=True
        )
        self._publish_thread.start()
        return True

    def stop_publish(self):
        """停止发布"""
        self._stop_flag = True
        if self._publish_thread:
            self._publish_thread.join(timeout=2)

    def is_publishing(self) -> bool:
        """检查是否正在发布"""
        return self._publish_thread and self._publish_thread.is_alive()

    def load_records(self):
        """加载并排序所有数据记录"""
        all_items = []
        for dtype, path in self.files.items():
            if not path.exists():
                continue
            with path.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        for ts, val in data.items():
                            all_items.append((ts, dtype, val))
                    except json.JSONDecodeError:
                        continue
        # 按时间排序
        all_items.sort(key=lambda x: x[0])
        return all_items

    # -------- 内部方法 --------
    def _publish_worker(self, interval: float):
        """后台发布线程"""
        records = self.load_records()
        total = len(records)
        published = 0

        for ts, dtype, val in records:
            if self._stop_flag:
                break

            try:
                num_val = float(val)
            except (TypeError, ValueError):
                continue

            # 根据启用的类型进行过滤
            if dtype not in self.enabled_types:
                time.sleep(interval)
                continue

            if self.publish_single(dtype, num_val, ts):
                published += 1

            time.sleep(interval)

        # 发布完成
        if self._on_publish_complete_cb:
            self._on_publish_complete_cb()

    def _on_connect(self, client, userdata, flags, rc):
        """MQTT 连接回调"""
        self._connected = True
        try:
            # 订阅控制主题，用于接收订阅端的发布过滤指令
            self._client.subscribe("control/publish_filter")
        except Exception:
            pass
        if self._on_connection_cb:
            self._on_connection_cb(True)

    def _on_disconnect(self, client, userdata, rc):
        """MQTT 断开回调"""
        self._connected = False
        if self._on_connection_cb:
            self._on_connection_cb(False)

    # ---- 控制通道处理 ----
    def _on_message(self, client, userdata, msg):
        """处理控制主题消息：更新 enabled_types
        支持两种载荷格式：
        1) {"enabled": ["temperature", "humidity"]}
        2) {"temperature": true, "humidity": false, "pressure": true}
        """
        try:
            topic = getattr(msg, "topic", "")
            if topic != "control/publish_filter":
                return
            payload_text = msg.payload.decode("utf-8", errors="ignore").strip()
            data = json.loads(payload_text) if payload_text else {}

            new_enabled = set()
            if isinstance(data, dict):
                if "enabled" in data and isinstance(data["enabled"], (list, tuple, set)):
                    for t in data["enabled"]:
                        if t in {"temperature", "humidity", "pressure"}:
                            new_enabled.add(t)
                else:
                    for t in ("temperature", "humidity", "pressure"):
                        if bool(data.get(t, False)):
                            new_enabled.add(t)

            self.enabled_types = new_enabled
        except Exception:
            pass

    # ---- 外部设置过滤 ----
    def set_enabled_types(self, enabled):
        """直接设置启用的发布类型（list/tuple/set）"""
        try:
            enabled_set = {t for t in enabled if t in {"temperature", "humidity", "pressure"}}
            if enabled_set:
                self.enabled_types = enabled_set
        except Exception:
            pass


__all__ = ["PublisherLogic"]

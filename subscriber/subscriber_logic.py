# subscriber/subscriber_logic.py
# MQTT 订阅端逻辑封装，供 GUI 调用

import json
import threading
from typing import Callable, Dict, Optional

import paho.mqtt.client as mqtt


class SubscriberLogic:
    """封装 paho-mqtt，提供基础的连接、订阅与回调接口。"""

    def __init__(self,
                 broker: str = "127.0.0.1",
                 port: int = 1883,
                 keepalive: int = 60):
        self.broker = broker
        self.port = port
        self.keepalive = keepalive

        self._client = mqtt.Client()
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message

        self._on_message_cb: Optional[Callable[[Dict], None]] = None
        self._on_connection_cb: Optional[Callable[[bool], None]] = None

        self._lock = threading.Lock()
        self._subscriptions = set()
        self._connected = False
        self._auto_reconnect = True  # 自动重连标志
        self._last_connect_attempt = 0  # 上次连接尝试时间

    # -------- 对外接口 --------
    def set_on_message(self, callback: Callable[[Dict], None]):
        """设置消息回调，参数为解析后的 dict。"""
        self._on_message_cb = callback

    def set_on_connection(self, callback: Callable[[bool], None]):
        """设置连接状态回调，参数为 True/False。"""
        self._on_connection_cb = callback

    def connect(self):
        """连接到 MQTT Broker 并启动循环线程。"""
        import time
        with self._lock:
            if self._connected:
                return
            
            # 避免频繁连接尝试（至少间隔1秒）
            current_time = time.time()
            if current_time - self._last_connect_attempt < 1.0:
                return
            self._last_connect_attempt = current_time
            
            try:
                # 如果之前连接失败，需要重新创建客户端
                try:
                    # 检查客户端是否处于错误状态
                    if hasattr(self._client, '_sock') and self._client._sock is None:
                        # 客户端可能处于错误状态，重新创建
                        self._client = mqtt.Client()
                        self._client.on_connect = self._on_connect
                        self._client.on_disconnect = self._on_disconnect
                        self._client.on_message = self._on_message
                except Exception:
                    # 如果客户端有问题，重新创建
                    self._client = mqtt.Client()
                    self._client.on_connect = self._on_connect
                    self._client.on_disconnect = self._on_disconnect
                    self._client.on_message = self._on_message
                
                self._client.connect(self.broker, self.port, self.keepalive)
                self._client.loop_start()
            except Exception as e:
                # 连接失败时触发断开回调
                self._connected = False
                if self._on_connection_cb:
                    self._on_connection_cb(False)

    def disconnect(self):
        """断开连接并停止循环线程。"""
        with self._lock:
            if not self._connected:
                return
            try:
                self._client.loop_stop()
                self._client.disconnect()
            except Exception:
                pass
            finally:
                self._connected = False
                # 确保触发断开回调
                if self._on_connection_cb:
                    self._on_connection_cb(False)

    def _valid_filter(self, topic: str) -> bool:
        """简单校验订阅过滤器是否合法。"""
        if not topic:
            return False
        # '#' 必须单独作为最后一级
        if topic.count("#") > 1:
            return False
        if "#" in topic and topic != "#" and not topic.endswith("/#"):
            return False
        # '+' 必须单独占用一个层级
        if "+" in topic:
            levels = topic.split("/")
            for lv in levels:
                if "+" in lv and lv != "+":
                    return False
        return True

    def subscribe(self, topic: str) -> bool:
        """订阅主题，返回是否成功。"""
        topic = topic.strip()
        if not self._valid_filter(topic):
            return False
        self.connect()
        try:
            self._client.subscribe(topic)
            self._subscriptions.add(topic)
            return True
        except ValueError:
            return False

    def unsubscribe(self, topic: str):
        """取消订阅主题。"""
        topic = topic.strip()
        if not topic:
            return
        if topic in self._subscriptions:
            self._client.unsubscribe(topic)
            self._subscriptions.discard(topic)

    def list_subscriptions(self):
        return sorted(list(self._subscriptions))
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._connected

    def publish(self, topic: str, payload) -> bool:
        """发布控制类消息（用于与发布端通信）。payload 可为 str 或 dict。"""
        try:
            if not self._connected:
                self.connect()
            if isinstance(payload, dict):
                import json as _json
                payload = _json.dumps(payload, ensure_ascii=False)
            self._client.publish(topic, payload)
            return True
        except Exception:
            return False

    # -------- paho 回调 --------
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT 连接回调"""
        if rc == 0:  # 连接成功
            self._connected = True
            if self._on_connection_cb:
                self._on_connection_cb(True)
        else:
            # 连接失败
            self._connected = False
            if self._on_connection_cb:
                self._on_connection_cb(False)

    def _on_disconnect(self, client, userdata, rc):
        """MQTT 断开回调"""
        was_connected = self._connected
        self._connected = False
        if self._on_connection_cb:
            self._on_connection_cb(False)
        
        # 如果之前已连接，现在断开，且启用了自动重连，尝试重新连接
        if was_connected and self._auto_reconnect:
            # 延迟重连，避免频繁尝试
            threading.Timer(2.0, self._try_reconnect).start()
    
    def _try_reconnect(self):
        """尝试重新连接"""
        if not self._connected:
            try:
                self.connect()
            except Exception:
                pass

    def _on_message(self, client, userdata, msg):
        payload_text = msg.payload.decode("utf-8", errors="ignore").strip()
        parsed: Dict = {
            "topic": msg.topic,
            "payload": payload_text,
        }
        # 尝试解析 JSON
        try:
            data = json.loads(payload_text)
            if isinstance(data, dict):
                parsed.update(data)
        except json.JSONDecodeError:
            pass

        if self._on_message_cb:
            self._on_message_cb(parsed)


__all__ = ["SubscriberLogic"]

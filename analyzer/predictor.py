# analyzer/predictor.py
"""预测与智能分析引擎 - 只使用实时传感器数据
支持MQTT多主题数据合并，适配publish_logic的消息格式
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import numpy as np
import json
from sklearn.linear_model import LinearRegression
import warnings
import threading
warnings.filterwarnings('ignore')

from .comfort_model import ComfortModel
from .event_context import EventContext


class XiaojiaBrain:
    """小嘉智能大脑（规则引擎），只使用实时数据，支持多主题数据合并"""
    
    def __init__(self):
        self.comfort_model = ComfortModel()
        self.event_context = EventContext()
        self.location = "JX_Teach"
        self.sensor_id = "JX_Teach_01"
        
        # 预测器相关 - 修改为基于20个点预测
        self.window_size = 20  # 基于20个点进行预测
        self.temp_history = []
        self.humidity_history = []
        self.pressure_history = []
        self.timestamps = []
        self.max_history = 100
        
        # MQTT订阅器
        self.subscriber = None
        self._mqtt_connected = False
        self.realtime_data = None
        self.realtime_callback = None
        
        # 数据缓存，用于合并来自不同主题的数据
        self.data_cache = {
            "temperature": None,
            "humidity": None, 
            "pressure": None,
            "last_updated": {
                "temperature": None,
                "humidity": None,
                "pressure": None
            },
            "raw_messages": {
                "temperature": None,
                "humidity": None,
                "pressure": None
            }
        }
        
        # 数据同步窗口（秒）
        self.sync_window = 5
        
        # 线程锁确保线程安全
        self.data_lock = threading.Lock()
        
        # 舒适度语言提示
        self.comfort_messages = {
            "very_comfortable": [
                "😊 当前环境非常舒适！温度湿度都刚刚好，继续保持哦！",
                "🌟 舒适度极佳！现在是学习和工作的绝佳环境！",
                "💫 环境条件完美！身心舒畅，效率倍增！"
            ],
            "comfortable": [
                "😊 环境舒适宜人，让人心情愉悦！",
                "🌤️ 舒适度良好，非常适合专注学习和工作！",
                "👍 环境条件不错，继续保持当前状态！"
            ],
            "moderate": [
                "😐 环境条件一般，可以考虑微调一下！",
                "🌥️ 舒适度中等，部分人群可能感觉不太舒适！",
                "⚠️ 环境有改善空间，建议适当调整！"
            ],
            "uncomfortable": [
                "😟 环境不太舒适，建议采取措施改善！",
                "🌧️ 舒适度较低，可能会影响学习和工作效率！",
                "❗ 请注意，当前环境条件需要调整！"
            ],
            "very_uncomfortable": [
                "😰 环境非常不舒适！请立即采取措施改善！",
                "🌩️ 舒适度极差！可能对健康造成影响！",
                "🚨 警告！环境条件恶劣，需要紧急处理！"
            ]
        }
        
        # 初始化MQTT订阅
        self._init_mqtt_subscriber()
        
        # 情绪状态映射
        self.mood_map = {
            "very_comfortable": "happy",
            "comfortable": "normal",
            "moderate": "neutral",
            "uncomfortable": "sad",
            "very_uncomfortable": "angry"
        }
        
        # 表情符号映射
        self.emoji_map = {
            "happy": "😊",
            "normal": "🙂",
            "neutral": "😐",
            "sad": "😟",
            "angry": "😠"
        }
        
        # 历史对话记录
        self.conversation_history = []
        self.max_history_dialog = 50
    
    def _init_mqtt_subscriber(self):
        """初始化MQTT订阅器"""
        try:
            from subscriber.subscriber_logic import SubscriberLogic
            
            self.subscriber = SubscriberLogic(
                broker="127.0.0.1",
                port=1883,
                keepalive=60
            )
            
            # 设置消息回调
            self.subscriber.set_on_message(self._on_mqtt_message)
            
        except ImportError as e:
            raise
        except Exception as e:
            raise

    def connect_mqtt(self):
        """按需连接MQTT，避免在发布端未连接前抢先连接"""
        if not self.subscriber:
            return False
        if self._mqtt_connected:
            return True
        try:
            self.subscriber.connect()
            self.subscriber.subscribe("sensor/temperature")
            self.subscriber.subscribe("sensor/humidity")
            self.subscriber.subscribe("sensor/pressure")
            self.subscriber.subscribe("sensor/#")  # 通配符订阅
            self._mqtt_connected = True
            return True
        except Exception:
            return False

    def disconnect_mqtt(self):
        """断开按需连接的MQTT订阅"""
        if self.subscriber and self._mqtt_connected:
            try:
                self.subscriber.disconnect()
            except Exception:
                pass
        self._mqtt_connected = False
    
    def _on_mqtt_message(self, mqtt_data: Dict):
        """处理MQTT消息 - 适配publish_logic的消息格式"""
        try:
            # 使用线程锁确保线程安全
            with self.data_lock:
                # 解析payload
                payload = mqtt_data.get("payload", "")
                topic = mqtt_data.get("topic", "")
                
                # 解析JSON payload
                try:
                    if isinstance(payload, str):
                        sensor_data = json.loads(payload)
                    else:
                        sensor_data = payload if isinstance(payload, dict) else {}
                except json.JSONDecodeError:
                    return
                
                # 根据publish_logic的格式解析数据
                self._parse_mqtt_message(topic, sensor_data)
                
        except Exception:
            pass
    
    def _parse_mqtt_message(self, topic: str, payload: Dict):
        """解析MQTT消息，适配publish_logic格式"""
        current_time = datetime.now()
        
        # 提取消息中的关键信息
        data_type = payload.get("type", "")
        value = payload.get("value", None)
        sensor_id = payload.get("sensor_id", "")
        location = payload.get("location", "")
        timestamp_str = payload.get("timestamp", "")
        
        # 更新传感器ID和位置（如果提供了）
        if sensor_id:
            self.sensor_id = sensor_id
        if location:
            self.location = location
        
        # 如果没有明确类型，尝试从主题推断
        if not data_type and "temperature" in topic.lower():
            data_type = "temperature"
        elif not data_type and "humidity" in topic.lower():
            data_type = "humidity"
        elif not data_type and "pressure" in topic.lower():
            data_type = "pressure"
        
        # 处理不同类型的数据
        if data_type == "temperature" and value is not None:
            try:
                temp_value = float(value)
                self.data_cache["temperature"] = temp_value
                self.data_cache["last_updated"]["temperature"] = current_time
                self.data_cache["raw_messages"]["temperature"] = payload
            except (ValueError, TypeError):
                pass
        
        elif data_type == "humidity" and value is not None:
            try:
                humid_value = float(value)
                self.data_cache["humidity"] = humid_value
                self.data_cache["last_updated"]["humidity"] = current_time
                self.data_cache["raw_messages"]["humidity"] = payload
            except (ValueError, TypeError):
                pass
        
        elif data_type == "pressure" and value is not None:
            try:
                pressure_value = float(value)
                self.data_cache["pressure"] = pressure_value
                self.data_cache["last_updated"]["pressure"] = current_time
                self.data_cache["raw_messages"]["pressure"] = payload
            except (ValueError, TypeError):
                pass
        else:
            return
        
        # 检查是否收集到完整的数据集
        self._check_and_process_complete_data(current_time)
    
    def _check_and_process_complete_data(self, current_time: datetime):
        """检查是否收集到完整的数据并进行处理"""
        # 检查是否有温度和湿度数据（必需）
        has_temp = self.data_cache["temperature"] is not None
        has_humid = self.data_cache["humidity"] is not None
        has_pressure = self.data_cache["pressure"] is not None
        
        if not (has_temp and has_humid):
            return
        
        # 检查数据时间是否在同步窗口内
        temp_time = self.data_cache["last_updated"]["temperature"]
        humid_time = self.data_cache["last_updated"]["humidity"]
        pressure_time = self.data_cache["last_updated"]["pressure"]
        
        # 计算时间差
        time_diffs = []
        if temp_time:
            time_diffs.append(abs((temp_time - current_time).total_seconds()))
        if humid_time:
            time_diffs.append(abs((humid_time - current_time).total_seconds()))
        if pressure_time:
            time_diffs.append(abs((pressure_time - current_time).total_seconds()))
        
        # 检查最大时间差
        if time_diffs and max(time_diffs) > self.sync_window:
            return
        
        # 构建完整传感器数据
        complete_data = {
            "temperature": self.data_cache["temperature"],
            "humidity": self.data_cache["humidity"],
            "pressure": self.data_cache["pressure"] if has_pressure else 1013.0,
            "topic": "sensor/combined",
            "timestamp": current_time.isoformat(),
            "sensor_id": self.sensor_id,
            "location": self.location
        }
        
        # 更新实时数据
        self.realtime_data = complete_data
        
        # 如果有回调函数，调用它
        if self.realtime_callback and self.realtime_data:
            # 注意：在Qt中，回调可能会在非主线程中被调用
            # 我们不在回调中直接处理UI更新，而是通过信号槽机制
            try:
                self.realtime_callback(complete_data, self.location, self.sensor_id)
            except Exception:
                # 这可能是线程问题，我们可以记录但不中断程序
                pass
    
    def set_realtime_callback(self, callback):
        """设置实时数据回调"""
        self.realtime_callback = callback
    
    def get_realtime_data(self) -> Optional[Dict]:
        """获取最新的实时数据"""
        with self.data_lock:
            return self.realtime_data
    
    def process_sensor_data(self, sensor_data: Dict = None, location: str = None, sensor_id: str = None) -> Dict:
        """
        处理传感器数据，生成综合响应
        如果没有传入sensor_data，使用实时数据
        """
        try:
            with self.data_lock:
                if location:
                    self.location = location
                if sensor_id:
                    self.sensor_id = sensor_id
                
                # 如果没有传入数据，使用实时数据
                if not sensor_data:
                    if not self.realtime_data:
                        # 尝试从缓存构建数据
                        cache_data = self._get_data_from_cache()
                        if cache_data:
                            sensor_data = cache_data
                        else:
                            return self._create_empty_response("没有可用的传感器数据")
                    else:
                        sensor_data = self.realtime_data
                
                # 检查数据完整性
                if "temperature" not in sensor_data or "humidity" not in sensor_data:
                    return self._create_empty_response("传感器数据不完整")
                
                # 1. 计算舒适度
                comfort_result = self.comfort_model.calculate_comfort_index(
                    sensor_data["temperature"],
                    sensor_data["humidity"],
                    sensor_data.get("pressure", 1013.0)
                )
                self.comfort_model.add_historical_data(comfort_result)
                
                # 2. 获取舒适度语言提示
                comfort_level = comfort_result.get("comfort_level", "moderate")
                comfort_messages = self.comfort_messages.get(comfort_level, ["环境数据正常"])
                comfort_prompt = comfort_messages[0]  # 使用第一个提示
                
                # 3. 更新预测器数据
                self._add_prediction_data(sensor_data)
                
                # 4. 获取预测结果
                prediction_result = self._get_prediction_result()
                
                # 5. 获取历史数据用于对比
                history_data = self._get_history_data()
                
                # 6. 构建响应
                response = {
                    "timestamp": datetime.now().isoformat(),
                    "sensor_id": self.sensor_id,
                    "location": self.location,
                    "raw_data": sensor_data,
                    "comfort_analysis": comfort_result,
                    "comfort_prompt": comfort_prompt,
                    "prediction_result": prediction_result,
                    "history_data": history_data,
                    "prediction_available": len(self.temp_history) >= self.window_size,
                    "data_source": "realtime",
                    "prediction_stats": {
                        "temperature_history": len(self.temp_history),
                        "humidity_history": len(self.humidity_history),
                        "pressure_history": len(self.pressure_history),
                        "window_size": self.window_size
                    }
                }
                
                return response
                
        except Exception as e:
            return self._create_empty_response(f"数据处理错误: {str(e)}")
    
    def _create_empty_response(self, message: str) -> Dict:
        """创建空响应"""
        return {
            "timestamp": datetime.now().isoformat(),
            "error": message,
            "comfort_analysis": {
                "temperature": 0,
                "humidity": 0,
                "pressure": 1013,
                "thi": 0,
                "feels_like": 0,
                "comfort_score": 0,
                "comfort_level": "moderate",
                "comfort_level_cn": "未知",
                "timestamp": datetime.now().isoformat()
            },
            "comfort_prompt": "⚠️ " + message,
            "prediction_available": False,
            "prediction_stats": {
                "temperature_history": len(self.temp_history),
                "humidity_history": len(self.humidity_history),
                "pressure_history": len(self.pressure_history),
                "window_size": self.window_size
            }
        }
    
    def _get_data_from_cache(self) -> Optional[Dict]:
        """从缓存获取数据"""
        if (self.data_cache["temperature"] is not None and 
            self.data_cache["humidity"] is not None):
            return {
                "temperature": self.data_cache["temperature"],
                "humidity": self.data_cache["humidity"],
                "pressure": self.data_cache["pressure"] if self.data_cache["pressure"] is not None else 1013.0,
                "timestamp": datetime.now().isoformat(),
                "sensor_id": self.sensor_id,
                "location": self.location
            }
        return None
    
    def _add_prediction_data(self, data: Dict):
        """添加数据点到预测历史"""
        current_time = datetime.now()
        
        # 从数据中提取数值
        temp = data.get("temperature")
        humidity = data.get("humidity")
        pressure = data.get("pressure", 1013.0)
        
        # 添加到历史记录
        if temp is not None:
            self.temp_history.append(float(temp))
        if humidity is not None:
            self.humidity_history.append(float(humidity))
        if pressure is not None:
            self.pressure_history.append(float(pressure))
        self.timestamps.append(current_time)
        
        # 限制历史数据大小
        if len(self.temp_history) > self.max_history:
            self.temp_history = self.temp_history[-self.max_history:]
        if len(self.humidity_history) > self.max_history:
            self.humidity_history = self.humidity_history[-self.max_history:]
        if len(self.pressure_history) > self.max_history:
            self.pressure_history = self.pressure_history[-self.max_history:]
        if len(self.timestamps) > self.max_history:
            self.timestamps = self.timestamps[-self.max_history:]
    
    def _get_prediction_result(self) -> Dict:
        """获取预测结果 - 基于20个点进行预测"""
        # 获取上海市参考数据
        shanghai_ref = self.get_shanghai_reference()
        shanghai_ref_temp = shanghai_ref.get("temperature", 20.0)
        
        if len(self.temp_history) < self.window_size:
            # 不足20个点，使用简单预测
            predictions = self._simple_predict_without_enough_data()
            return {
                "predictions": predictions,
                "shanghai_reference": shanghai_ref_temp,
                "confidence": 0.3,
                "has_enough_data": False,
                "timestamps": self._generate_future_timestamps(len(predictions)),
                "trend": self._get_trend(),
                "prediction_type": f"简单平均（数据不足 {len(self.temp_history)}/{self.window_size}）"
            }
        
        # 使用最近20个点进行线性回归预测
        predictions = self._linear_regression_predict(5)
        
        # 计算置信度（基于数据量）
        confidence = min(0.95, len(self.temp_history) / 100)
        
        return {
            "predictions": predictions,
            "shanghai_reference": shanghai_ref_temp,
            "confidence": confidence,
            "has_enough_data": True,
            "timestamps": self._generate_future_timestamps(len(predictions)),
            "trend": self._get_trend(),
            "prediction_type": f"线性回归（基于最近{self.window_size}个点）"
        }
    
    def _simple_predict_without_enough_data(self) -> List[float]:
        """数据不足时的简单预测"""
        if not self.temp_history:
            return [20.0, 20.0, 20.0, 20.0, 20.0]
        
        # 使用最近几个点的平均值
        recent = self.temp_history[-min(5, len(self.temp_history)):]
        avg = sum(recent) / len(recent)
        return [round(avg, 1)] * 5
    
    def _linear_regression_predict(self, steps: int) -> List[float]:
        """基于最近20个点的线性回归预测"""
        try:
            # 使用最近20个点
            X = np.arange(min(self.window_size, len(self.temp_history))).reshape(-1, 1)
            y = self.temp_history[-self.window_size:] if len(self.temp_history) >= self.window_size else self.temp_history
            
            # 训练线性回归模型
            model = LinearRegression()
            model.fit(X, y)
            
            # 预测未来steps个点
            X_pred = np.arange(len(y), len(y) + steps).reshape(-1, 1)
            predictions = model.predict(X_pred)
            
            # 确保预测值在合理范围内
            predictions = np.clip(predictions, -10, 45)
            
            return [round(pred, 1) for pred in predictions]
        except Exception:
            # 回退到简单平均
            if self.temp_history:
                avg = sum(self.temp_history[-self.window_size:]) / min(self.window_size, len(self.temp_history))
                return [round(avg, 1)] * steps
            return [20.0] * steps
    
    def _generate_future_timestamps(self, steps: int) -> List[str]:
        """生成未来时间戳"""
        timestamps = []
        current_time = datetime.now()
        
        for i in range(steps):
            future_time = current_time + timedelta(minutes=10 * i)
            timestamps.append(future_time.strftime("%H:%M"))
        
        return timestamps
    
    def _get_trend(self) -> str:
        """获取温度趋势"""
        if len(self.temp_history) < 3:
            return "stable"
        
        # 使用最近3个点判断趋势
        recent = self.temp_history[-3:]
        if recent[2] > recent[0] + 0.5:
            return "rising"
        elif recent[2] < recent[0] - 0.5:
            return "falling"
        else:
            return "stable"
    
    def _get_history_data(self) -> Dict:
        """获取历史数据用于对比"""
        # 限制显示的点数，让图表更宽松
        history_count = min(30, len(self.temp_history))
        
        # 如果数据太多，进行采样
        temp_data = []
        humid_data = []
        pressure_data = []
        
        if self.temp_history:
            step = max(1, len(self.temp_history) // history_count)
            temp_data = self.temp_history[-history_count*step::step][:history_count]
        
        if self.humidity_history:
            step = max(1, len(self.humidity_history) // history_count)
            humid_data = self.humidity_history[-history_count*step::step][:history_count]
        
        if self.pressure_history:
            step = max(1, len(self.pressure_history) // history_count)
            pressure_data = self.pressure_history[-history_count*step::step][:history_count]
        
        return {
            "temperature": temp_data,
            "humidity": humid_data,
            "pressure": pressure_data,
            "count": history_count
        }
    
    # ===== 公共API =====
    def predict_next(self, steps: int = 5) -> Dict:
        """预测未来steps个时间点的数值"""
        return self._get_prediction_result()
    
    def get_trend_analysis(self) -> Dict:
        """获取趋势分析"""
        return {"temperature_trend": self._get_trend()}
    
    def get_historical_data(self, data_type: str = "temperature") -> Dict:
        """获取历史数据"""
        history_data = self._get_history_data()
        
        if data_type in ["temperature", "humidity", "pressure"]:
            return {
                data_type: history_data[data_type],
                "count": len(history_data[data_type])
            }
        
        return history_data
    
    def get_comfort_statistics(self) -> Dict:
        """获取舒适度统计"""
        stats = self.comfort_model.get_statistics()
        
        # 添加预测数据统计
        stats.update({
            "prediction_data_count": len(self.temp_history),
            "prediction_window_size": self.window_size,
            "prediction_ready": len(self.temp_history) >= self.window_size
        })
        
        return stats
    
    def get_shanghai_reference(self) -> Dict:
        """获取上海市参考值"""
        return self.comfort_model.get_shanghai_reference()
    
    def reset_predictor(self):
        """重置预测器数据"""
        with self.data_lock:
            self.temp_history = []
            self.humidity_history = []
            self.pressure_history = []
            self.timestamps = []
            
            # 同时重置数据缓存
            self.data_cache = {
                "temperature": None,
                "humidity": None, 
                "pressure": None,
                "last_updated": {
                    "temperature": None,
                    "humidity": None,
                    "pressure": None
                },
                "raw_messages": {
                    "temperature": None,
                    "humidity": None,
                    "pressure": None
                }
            }


__all__ = ["XiaojiaBrain"]
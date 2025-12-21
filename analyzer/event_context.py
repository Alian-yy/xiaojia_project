# analyzer/event_context.py
"""
校园事件匹配 - 根据时间、地点、数据匹配校园事件
"""

from datetime import datetime, time
from typing import Dict, List, Optional


class CampusEvent:
    """校园事件定义"""
    
    def __init__(self, name: str, event_type: str, 
                 time_range: tuple, location: str, 
                 trigger_conditions: Dict, 
                 description: str, suggestions: List[str]):
        self.name = name
        self.type = event_type
        self.time_range = time_range  # (start_hour, end_hour)
        self.location = location
        self.trigger_conditions = trigger_conditions
        self.description = description
        self.suggestions = suggestions
        self.priority = 1


class EventContext:
    """校园事件上下文匹配引擎"""
    
    def __init__(self):
        self.events = self._init_events()
        self.current_events = []
        
    def _init_events(self) -> List[CampusEvent]:
        """初始化校园事件库"""
        return [
            CampusEvent(
                name="课堂教学",
                event_type="academic",
                time_range=(8, 12),
                location="JX_Teach",
                trigger_conditions={"temperature": (20, 26), "humidity": (40, 60)},
                description="教学楼上课时间，需要良好的学习环境",
                suggestions=["保持教室通风", "注意调节空调温度", "适当使用加湿器"]
            ),
            CampusEvent(
                name="午间休息",
                event_type="rest",
                time_range=(12, 14),
                location="JX_Teach",
                trigger_conditions={},
                description="午休时间，需要安静舒适的环境",
                suggestions=["拉上窗帘减少光照", "保持适宜温度", "避免噪音干扰"]
            ),
            CampusEvent(
                name="体育课",
                event_type="sports",
                time_range=(14, 17),
                location="Playground",
                trigger_conditions={"temperature": (15, 28)},
                description="体育课期间，注意运动安全",
                suggestions=["注意补水", "避免高温时段剧烈运动", "运动前热身"]
            ),
            CampusEvent(
                name="篮球比赛",
                event_type="competition",
                time_range=(15, 18),
                location="Basketball_Court",
                trigger_conditions={"humidity": (30, 70)},
                description="篮球比赛进行中",
                suggestions=["场地保持干燥", "注意运动员补水", "检查场地安全"]
            ),
            CampusEvent(
                name="高温预警",
                event_type="weather_warning",
                time_range=(0, 24),
                location="*",
                trigger_conditions={"temperature": (30, 100)},
                description="高温天气，注意防暑降温",
                suggestions=["减少户外活动", "多喝水", "使用遮阳设备"]
            ),
            CampusEvent(
                name="高湿天气",
                event_type="weather_warning",
                time_range=(0, 24),
                location="*",
                trigger_conditions={"humidity": (80, 100)},
                description="高湿度天气，注意防潮",
                suggestions=["开启除湿设备", "注意电器防潮", "保持通风"]
            ),
            CampusEvent(
                name="低压天气",
                event_type="weather_warning",
                time_range=(0, 24),
                location="*",
                trigger_conditions={"pressure": (0, 1000)},
                description="低气压天气，可能影响舒适度",
                suggestions=["注意通风", "避免剧烈运动", "关注空气质量"]
            )
        ]
    
    def match_events(self, sensor_data: Dict, location: str = None) -> List[Dict]:
        """匹配当前可能发生的校园事件"""
        current_hour = datetime.now().hour
        matched_events = []
        
        for event in self.events:
            # 检查时间范围
            if not (event.time_range[0] <= current_hour <= event.time_range[1]):
                continue
            
            # 检查地点匹配
            if event.location != "*" and location and event.location != location:
                continue
            
            # 检查触发条件
            conditions_met = True
            for key, (min_val, max_val) in event.trigger_conditions.items():
                if key in sensor_data:
                    value = sensor_data[key]
                    if not (min_val <= value <= max_val):
                        conditions_met = False
                        break
            
            if conditions_met:
                matched_events.append({
                    "name": event.name,
                    "type": event.type,
                    "description": event.description,
                    "suggestions": event.suggestions,
                    "priority": event.priority,
                    "time_range": event.time_range,
                    "location": event.location
                })
        
        # 按优先级排序
        matched_events.sort(key=lambda x: x["priority"], reverse=True)
        self.current_events = matched_events
        return matched_events
    
    def generate_natural_language(self, sensor_data: Dict, events: List[Dict]) -> str:
        """根据传感器数据和匹配的事件生成自然语言提示"""
        if not events:
            temp = sensor_data.get("temperature", 0)
            humidity = sensor_data.get("humidity", 0)
            return f"当前环境温度{temp}℃，湿度{humidity}%，一切正常。"
        
        # 取优先级最高的事件
        event = events[0]
        
        # 根据事件类型生成不同的提示语
        if event["type"] == "weather_warning":
            if "temperature" in sensor_data and sensor_data["temperature"] > 30:
                return f"🌡️ 高温预警！当前温度{sensor_data['temperature']}℃，{event['description']}。建议：{'；'.join(event['suggestions'][:2])}"
            elif "humidity" in sensor_data and sensor_data["humidity"] > 80:
                return f"💦 高湿预警！当前湿度{sensor_data['humidity']}%，{event['description']}。建议：{'；'.join(event['suggestions'][:2])}"
        elif event["type"] == "academic":
            return f"📚 {event['name']}进行中。{event['description']}建议：{'；'.join(event['suggestions'][:2])}"
        elif event["type"] == "sports":
            return f"🏀 {event['name']}进行中。{event['description']}建议：{'；'.join(event['suggestions'][:2])}"
        
        return f"🔔 {event['name']}：{event['description']}建议：{'；'.join(event['suggestions'][:2])}"
    
    def get_current_events(self) -> List[Dict]:
        """获取当前正在发生的事件"""
        return self.current_events


__all__ = ["EventContext", "CampusEvent"]
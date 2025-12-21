# analyzer/comfort_model.py
"""
舒适度模型 - 基于温度、湿度、气压计算舒适度指数
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple


class ComfortModel:
    """舒适度计算模型"""
    
    # 上海市参考气候数据（月平均） - 更新为更准确的数据
    SHANGHAI_REFERENCE = {
        "temperature": [6.8, 8.2, 12.1, 17.3, 22.1, 25.6, 29.5, 29.2, 25.6, 20.6, 15.0, 9.3],
        "humidity": [73, 74, 76, 74, 75, 82, 80, 80, 78, 73, 71, 70],
        "pressure": [1026.5, 1024.5, 1019.8, 1014.5, 1010.8, 1006.2, 1004.0, 1004.7, 1011.0, 1017.3, 1022.2, 1025.4]
    }
    
    # 上海全年温度范围（用于折线图显示）
    SHANGHAI_YEARLY_TEMPS = [6.8, 8.2, 12.1, 17.3, 22.1, 25.6, 29.5, 29.2, 25.6, 20.6, 15.0, 9.3]
    
    def __init__(self):
        self.history_data = []
        self.max_history = 1000
        
    def calculate_comfort_index(self, temp: float, humidity: float, pressure: float) -> Dict:
        """计算综合舒适度指数"""
        # THI（温湿指数）
        thi = 0.8 * temp + humidity * 0.01 * (0.8 * temp - 14.3) + 46.3
        
        # 体感温度（简化）
        feels_like = temp + 0.3 * humidity * 0.01 - 2.7
        
        # 压力舒适度
        current_month = datetime.now().month - 1
        pressure_ref = self.SHANGHAI_REFERENCE["pressure"][current_month]
        pressure_comfort = 100 - abs(pressure - pressure_ref) * 0.5
        
        # 综合舒适度（0-100）
        comfort_score = (
            0.5 * self._temp_score(temp) +
            0.3 * self._humidity_score(humidity) +
            0.2 * min(pressure_comfort, 100)
        )
        
        # 舒适度等级
        if comfort_score >= 80:
            level = "very_comfortable"
            level_cn = "非常舒适"
        elif comfort_score >= 60:
            level = "comfortable"
            level_cn = "舒适"
        elif comfort_score >= 40:
            level = "moderate"
            level_cn = "一般"
        elif comfort_score >= 20:
            level = "uncomfortable"
            level_cn = "不舒适"
        else:
            level = "very_uncomfortable"
            level_cn = "非常不舒适"
        
        return {
            "temperature": temp,
            "humidity": humidity,
            "pressure": pressure,
            "thi": round(thi, 1),
            "feels_like": round(feels_like, 1),
            "comfort_score": round(comfort_score, 1),
            "comfort_level": level,
            "comfort_level_cn": level_cn,
            "timestamp": datetime.now().isoformat()
        }
    
    def _temp_score(self, temp: float) -> float:
        """温度评分（18-26℃为最佳）"""
        if 18 <= temp <= 26:
            return 100
        elif temp < 18:
            return max(0, 100 - (18 - temp) * 5)
        else:
            return max(0, 100 - (temp - 26) * 5)
    
    def _humidity_score(self, humidity: float) -> float:
        """湿度评分（40-60%为最佳）"""
        if 40 <= humidity <= 60:
            return 100
        elif humidity < 40:
            return max(0, 100 - (40 - humidity) * 2)
        else:
            return max(0, 100 - (humidity - 60) * 1.5)
    
    def add_historical_data(self, data: Dict):
        """添加历史数据"""
        self.history_data.append(data)
        if len(self.history_data) > self.max_history:
            self.history_data = self.history_data[-self.max_history:]
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        if not self.history_data:
            return {}
        
        temps = [d.get("temperature", 0) for d in self.history_data]
        hums = [d.get("humidity", 0) for d in self.history_data]
        pressures = [d.get("pressure", 0) for d in self.history_data]
        
        # 过滤有效数据
        temps = [t for t in temps if t != 0]
        hums = [h for h in hums if h != 0]
        pressures = [p for p in pressures if p != 0]
        
        return {
            "temperature_avg": np.mean(temps) if temps else 0,
            "temperature_std": np.std(temps) if temps else 0,
            "humidity_avg": np.mean(hums) if hums else 0,
            "humidity_std": np.std(hums) if hums else 0,
            "pressure_avg": np.mean(pressures) if pressures else 0,
            "pressure_std": np.std(pressures) if pressures else 0,
            "data_count": len(self.history_data)
        }
    
    def get_shanghai_reference(self) -> Dict:
        """获取上海市参考值"""
        current_month = datetime.now().month - 1
        return {
            "temperature": self.SHANGHAI_REFERENCE["temperature"][current_month],
            "humidity": self.SHANGHAI_REFERENCE["humidity"][current_month],
            "pressure": self.SHANGHAI_REFERENCE["pressure"][current_month],
            "month": current_month + 1,
            "yearly_temperatures": self.SHANGHAI_YEARLY_TEMPS
        }


__all__ = ["ComfortModel"]
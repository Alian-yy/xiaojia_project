# scripts/publish_sample.py
# 将数据文件通过 MQTT 逐条发布，便于本地调试订阅端

import json
import time
from pathlib import Path

import paho.mqtt.client as mqtt

# 数据文件路径
BASE_DIR = Path(r"E:\IoT\2025_2026_1_Data_MQTT\2025_2026_1_IoTData")
FILES = {
    "temperature": BASE_DIR / "temperature.txt",
    "humidity": BASE_DIR / "humidity.txt",
    "pressure": BASE_DIR / "pressure.txt",
}

BROKER = "127.0.0.1"
PORT = 1883
SENSOR_ID = "JX_Teach"
LOCATION = "教学楼A"
SLEEP_SEC = 0.2  # 每条间隔


def iter_records():
    """按时间排序输出三类数据的记录。"""
    all_items = []
    for dtype, path in FILES.items():
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


def main():
    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)

    for ts, dtype, val in iter_records():
        # 跳过空值/无法转换的记录
        try:
            num_val = float(val)
        except (TypeError, ValueError):
            continue

        payload = {
            "timestamp": ts,
            "value": num_val,
            "sensor_id": SENSOR_ID,
            "location": LOCATION,
            "type": dtype,
        }
        topic = f"sensor/{dtype}"
        client.publish(topic, json.dumps(payload, ensure_ascii=False))
        print(f"-> {topic} {payload}")
        time.sleep(SLEEP_SEC)

    client.disconnect()


if __name__ == "__main__":
    main()

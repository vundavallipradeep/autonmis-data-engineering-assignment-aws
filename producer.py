# producer.py
from kafka import KafkaProducer
import json, time, uuid, random
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers='44.212.0.235:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

while True:
    event = {
        "event_id": str(uuid.uuid4()),
        "user_id": random.choice(["user_789", "user_456"]),
        "event_type": "product_view",
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {
            "product_id": "prod_456",
            "price": random.choice([499, 1299, 999]),
            "category": "electronics"
        }
    }
    print(f"Sending event: {event}")
    producer.send("raw-events", event)
    time.sleep(1)

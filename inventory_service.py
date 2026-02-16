# inventory_service.py
import json
import random
from kafka import KafkaConsumer, KafkaProducer

consumer = KafkaConsumer(
    'OrderPlaced',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    group_id='inventory_group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("Inventory Service Listening...")

for message in consumer:
    order = message.value
    
    # Random failure logic (e.g., 5% failure rate)
    status = "SUCCESS" if random.random() > 0.05 else "FAILURE"
    
    inventory_event = {
        "order_id": order['order_id'],
        "status": status,
        "timestamp": order['timestamp'] # Preserve original event time if needed
    }
    
    producer.send('InventoryEvents', inventory_event)
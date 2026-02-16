# producer.py
import json
import time
import random
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

EVENTS_TO_PRODUCE = 10000

print(f"Producing {EVENTS_TO_PRODUCE} events...")
for i in range(EVENTS_TO_PRODUCE):
    event = {
        "order_id": i,
        "item": random.choice(["Apple", "Banana", "Cherry"]),
        "quantity": random.randint(1, 5),
        "timestamp": time.time() # Event Time
    }
    producer.send('OrderPlaced', event)
    
    # Simulate slight delay to spread events over time (optional but good for realism)
    if i % 100 == 0: 
        time.sleep(0.1)

producer.flush()
print("Done.")
# analytics.py
import json
import time
from collections import defaultdict
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'InventoryEvents', # listening to the output of Inventory
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    group_id='analytics_group_v1', # Change this ID to trigger a full replay naturally
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

total_orders = 0
failed_orders = 0
# Bucket orders by minute (timestamp // 60)
orders_per_minute = defaultdict(int)

print("Analytics Service Started...")

try:
    for message in consumer:
        time.sleep(0.01)
        event = message.value
        total_orders += 1
        
        
        if event['status'] == 'FAILURE':
            failed_orders += 1
            
        # Metrics Calculation
        event_minute = int(event['timestamp'] // 60)
        orders_per_minute[event_minute] += 1
        
        # Periodic printing (don't print every line for 10k events)
        if total_orders % 1000 == 0:
            print(f"Processed: {total_orders}")
            print(f"Failure Rate: {(failed_orders/total_orders)*100:.2f}%")

except KeyboardInterrupt:
    # Final Report
    print("\n--- FINAL REPORT ---")
    print(f"Total Orders: {total_orders}")
    print(f"Failure Rate: {(failed_orders/total_orders)*100:.2f}%")
    print("Orders Per Minute distribution:")
    for minute, count in sorted(orders_per_minute.items()):
        print(f"Minute {minute}: {count}")
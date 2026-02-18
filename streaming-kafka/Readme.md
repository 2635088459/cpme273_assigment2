# Part C: Streaming (Kafka) Implementation

This project implements an Event-Driven Architecture using Apache Kafka to process order events and generate real-time analytics. It demonstrates producer-consumer decoupling, stream processing, and consumer group replay capabilities.

## Project Structure

streaming-kafka/
|-- docker-compose.yml       # Infrastructure (Zookeeper + Kafka)
|-- producer_order/          # Service: Publishes OrderEvents (OrderPlaced)
|-- inventory_consumer/      # Service: Consumes orders, emits InventoryEvents
|-- analytics_consumer/      # Service: Computes orders/min and failure rate
|-- run1.txt                 # Evidence: Baseline metrics output (10k events)
|-- run2.txt                 # Evidence: Replay metrics output (10k events)
|-- tests/                   # Screenshots and test scripts

## Implementation Details

1. Producer:
   - Publishes 'OrderPlaced' events to the 'OrderEvents' topic.
   - Generates 10,000 mock events with random items and timestamps.

2. Inventory Service:
   - Consumes 'OrderEvents'.
   - Simulates stock checks (mock 5% failure rate).
   - Emits result events to the 'InventoryEvents' topic.

3. Analytics Service:
   - Consumes 'InventoryEvents'.
   - Computes real-time metrics based on event timestamps:
     - Orders Per Minute
     - Failure Rate

## How to Run

1. Start Infrastructure
   docker-compose up -d

2. Start Services
   Open three separate terminal windows in this directory:

   Terminal 1 (Inventory):
   python -u inventory_consumer/main.py

   Terminal 2 (Analytics):
   python -u analytics_consumer/main.py

   Terminal 3 (Producer):
   python producer_order/main.py

## Testing Requirements & Evidence

### Requirement 1: Produce 10k Events
The producer successfully generated 10,000 events. The Analytics service processed these and generated a metrics report.

Evidence File: [run1.txt](./run1.txt)

### Requirement 2: Demonstrate Replay
To demonstrate replay capability, the consumer group offset was reset to the earliest position. The Analytics service re-processed the entire history of 10,000 events.

Command used for reset:
docker-compose exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 --group analytics_group_v1 --topic InventoryEvents --reset-offsets --to-earliest --execute

Evidence File: [run2.txt](./run2.txt)

Comparison Screenshot (Before vs After):
<img width="1470" height="857" alt="Screenshot 2026-02-17 at 6 03 33 PM" src="https://github.com/user-attachments/assets/da631cc1-6e13-482d-b252-9d286f4aaf85" />

*(Note: The metrics in run1.txt and run2.txt are identical, proving deterministic replay).*

### Requirement 3: Consumer Lag under Throttling
To demonstrate flow control and backpressure, a processing delay (sleep) was introduced in the Analytics consumer. The producer continued to publish at a high rate, causing a backlog (lag) in the Kafka topic.

Lag Screenshot:
<img width="1470" height="197" alt="Screenshot 2026-02-17 at 1 17 40 PM" src="https://github.com/user-attachments/assets/7c663b99-186d-4bcd-bf13-a9926c6f0942" />


## Student Information
Name: Sakshat Patil
Course: CMPE 273 Distributed Systems
Assignment: Lab 2, Part C

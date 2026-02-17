# CMPE 273 Assignment 2: Communication Models

This repository contains the implementation for Assignment 2, demonstrating three different architectural patterns for a "campus food ordering" workflow:
1. Part A: Synchronous REST
2. Part B: Asynchronous Messaging (RabbitMQ)
3. Part C: Streaming (Kafka)

## Repository Structure

cmpe273-comm-models-lab/
|-- common/                  # Shared utilities
|   |-- ids.py
|   |-- README.md
|
|-- sync-rest/               # Part A: Synchronous Implementation
    |-- docker-compose.yml   # Infrastructure
    |-- order_service/
    |-- inventory_service/
    |-- notification_service/
    |-- tests/
|
|-- async-rabbitmq/          # Part B: Async Implementation
    |-- docker-compose.yml   # Infrastructure (RabbitMQ)
    |-- order_service/
    |-- inventory_service/
    |-- notification_service/
    |-- broker/
    |-- tests/
|
|-- streaming-kafka/         # Part C: Streaming Implementation
    |-- docker-compose.yml   # Infrastructure (Zookeeper + Kafka)
    |-- producer_order/
    |-- inventory_consumer/
    |-- analytics_consumer/
    |-- tests/

---

## Part A: Synchronous (REST)

A synchronous microservices implementation where the Order Service directly calls downstream services via HTTP.

### Implementation Details
* Flow: POST /order (OrderService) -> POST /reserve (Inventory) -> POST /send (Notification).
* Behavior: If Inventory reservation succeeds, the notification is sent. If it fails, the order is rejected.

### How to Run
1. Start Infrastructure:
   cd sync-rest
   docker-compose up --build

2. Run Tests:
   python tests/run_tests.py

### Testing Requirements Covered
* Baseline Latency: Measured N requests under normal load.
* Fault Injection:
  * 2s Delay: Injected into Inventory to measure impact on total Order latency.
  * Failure: Injected Inventory errors to verify OrderService timeout/error handling.

---

## Part B: Async (RabbitMQ)

An asynchronous messaging implementation using RabbitMQ to decouple services.



### Implementation Details
* Flow: OrderService writes to local store and publishes OrderPlaced.
* InventoryService consumes OrderPlaced, reserves stock, and publishes InventoryReserved (or InventoryFailed).
* NotificationService consumes InventoryReserved and sends confirmation.

### How to Run
1. Start Infrastructure:
   cd async-rabbitmq
   docker-compose up --build

2. Run Workload:
   python tests/generate_orders.py

### Testing Requirements Covered
* Backlog & Recovery: Demonstrated by killing InventoryService for 60s while publishing continues, then restarting to show backlog drain.
* Idempotency: Verified by re-delivering the same OrderPlaced message twice; Inventory ensures no double reservation.
* Poison Message: Handling of malformed events via Dead Letter Queue (DLQ).

---

## Part C: Streaming (Kafka)

An event-driven streaming implementation using Apache Kafka for high-throughput processing and analytics.

### Implementation Details
* Producer: Publishes OrderPlaced events to the OrderEvents stream.
* Inventory: Consumes OrderEvents, applies logic, and emits InventoryEvents.
* Analytics: Consumes streams to compute real-time metrics (Orders per Minute, Failure Rate).

### How to Run
1. Start Infrastructure:
   cd streaming-kafka
   docker-compose up -d

2. Run Services (in separate terminals):
   python -u streaming-kafka/inventory_consumer/main.py
   python -u streaming-kafka/analytics_consumer/main.py
   python streaming-kafka/producer_order/main.py

### Testing Requirements Covered
* Volume: Production of 10,000 events.
* Replay: Demonstrated by resetting the consumer offset in the Analytics service to recompute metrics from history.
  * Command: docker-compose exec kafka kafka-consumer-groups ... --reset-offsets --to-earliest
* Consumer Lag: Demonstrated by throttling the consumer to show lag accumulation under load.

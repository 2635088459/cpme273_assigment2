Part B – Asynchronous Messaging (RabbitMQ)

This folder contains the asynchronous event-driven implementation of the campus food ordering workflow using RabbitMQ.

**Architecture**

This implementation replaces synchronous REST calls with event-based messaging.

**Workflow:**

1.Order Service

-Endpoint: POST /order

-Publishes OrderPlaced event to queue order_placed

-Returns immediately (non-blocking)

2.Inventory Service

-Consumes order_placed

-Reserves inventory

-Publishes inventory_reserved

3.Notification Service

-Consumes inventory_reserved

-Sends confirmation

-RabbitMQ acts as the message broker between services.

Services

1.Order Service:

-Endpoint: POST /order

-Publishes to queue: order_placed

2.Inventory Service:

-Consumes: order_placed

-Publishes: inventory_reserved

3.Notification Service:

-Consumes: inventory_reserved

4.RabbitMQ:

-AMQP port: 5672

-Management UI: http://localhost:15672

**Start the Stack**
docker compose up -d --build
Verify containers:

docker ps

Normal Request
curl -X POST localhost:8000/order


Expected:

{"order_id":"<uuid>","status":"order placed"}


Order returns immediately without waiting for Inventory or Notification.

Failure Injection – Backlog Demonstration
1️⃣ Stop Inventory
docker stop async-rabbitmq-inventory_service-1

2️⃣ Send Multiple Orders
for i in {1..5}; do curl -X POST localhost:8000/order; done

**Observed Behavior**

RabbitMQ → order_placed queue shows:

Ready > 0

Consumers = 0

This demonstrates:

OrderService continues operating

Messages accumulate in the queue

System is decoupled

Messages are durable
Recovery Demonstration
3️⃣ Restart Inventory
docker start async-rabbitmq-inventory_service-1

Observed Behavior

RabbitMQ → order_placed queue shows:

Ready = 0

Consumers = 1

This demonstrates:

Inventory reconnects

Backlog is processed automatically

System achieves eventual consistency
<img width="2940" height="1912" alt="image" src="https://github.com/user-attachments/assets/da1b5933-252e-402e-8d7f-1aa3b4545700" />

Idempotency Strategy

RabbitMQ guarantees at-least-once delivery, meaning duplicate messages may occur.

To prevent duplicate processing, InventoryService maintains a set of processed order IDs:

processed_orders = set()


Before processing a message:

If order_id already exists → skip processing

Otherwise → process and store the order_id

This ensures inventory is not double-reserved even if the same message is delivered more than once.
**Stop the Stack**
docker compose down

**Conclusion**

The asynchronous RabbitMQ implementation provides:

Loose coupling between services

Durable message persistence

Automatic backlog recovery

Improved fault tolerance

Event-driven scalability

This architecture handles service failures more gracefully than synchronous REST.

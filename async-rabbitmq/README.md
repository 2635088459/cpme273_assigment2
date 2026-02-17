Part B – Asynchronous Messaging (RabbitMQ)

This folder contains the asynchronous event-driven implementation of the campus food ordering workflow using RabbitMQ.

Architecture

This implementation replaces synchronous REST calls with event-based messaging.

Workflow:

Order Service

Endpoint: POST /order

Publishes OrderPlaced event to queue order_placed

Returns immediately (non-blocking)

Inventory Service

Consumes order_placed

Reserves inventory

Publishes inventory_reserved

Notification Service

Consumes inventory_reserved

Sends confirmation

RabbitMQ acts as the message broker between services.

Services

Order Service:

Endpoint: POST /order

Publishes to queue: order_placed

Inventory Service:

Consumes: order_placed

Publishes: inventory_reserved

Notification Service:

Consumes: inventory_reserved

RabbitMQ:

AMQP port: 5672

Management UI: http://localhost:15672

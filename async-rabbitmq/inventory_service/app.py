import json
import pika
import time

processed_orders = set()

def connect_with_retry():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='rabbitmq')
            )
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("RabbitMQ not ready, retrying in 5 seconds...")
            time.sleep(5)

def callback(ch, method, properties, body):
    message = json.loads(body)
    order_id = message["order_id"]

    if order_id in processed_orders:
        print("Duplicate order ignored:", order_id)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    processed_orders.add(order_id)

    print("Processing order:", order_id)
    time.sleep(1)

    channel.basic_publish(
        exchange='',
        routing_key='inventory_reserved',
        body=json.dumps({"order_id": order_id}),
        properties=pika.BasicProperties(delivery_mode=2)
    )

    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = connect_with_retry()
channel = connection.channel()

channel.queue_declare(queue='order_placed', durable=True)
channel.queue_declare(queue='inventory_reserved', durable=True)

channel.basic_consume(
    queue='order_placed',
    on_message_callback=callback,
    auto_ack=False
)

print("Inventory service waiting for orders...")
channel.start_consuming()

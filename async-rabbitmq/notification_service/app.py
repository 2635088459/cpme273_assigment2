import json
import pika
import time

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
    print("Notification sent for order:", message["order_id"])
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = connect_with_retry()
channel = connection.channel()

channel.queue_declare(queue='inventory_reserved', durable=True)

channel.basic_consume(
    queue='inventory_reserved',
    on_message_callback=callback,
    auto_ack=False
)

print("Notification service waiting...")
channel.start_consuming()

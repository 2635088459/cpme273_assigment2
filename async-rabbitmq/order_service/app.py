import json
import uuid
import pika
from flask import Flask, jsonify

app = Flask(__name__)

def publish_order(order_id):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq')
    )
    channel = connection.channel()

    channel.queue_declare(queue='order_placed', durable=True)

    message = {
        "order_id": order_id,
        "item_id": "burger",
        "quantity": 1
    }

    channel.basic_publish(
        exchange='',
        routing_key='order_placed',
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2)
    )

    connection.close()

@app.route("/order", methods=["POST"])
def create_order():
    order_id = str(uuid.uuid4())
    publish_order(order_id)
    return jsonify({"status": "order placed", "order_id": order_id})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

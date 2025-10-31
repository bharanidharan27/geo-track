from confluent_kafka import Producer
import json

producer_conf = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(producer_conf)

def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Delivery failed: {err}")
    # optional: print(f"Produced to {msg.topic()} partition [{msg.partition()}]")

def send_event(topic: str, key: str, value: dict):
    """Send a single ScanEvent JSON to Kafka."""
    producer.produce(
        topic=topic,
        key=key.encode(),
        value=json.dumps(value).encode(),
        on_delivery=delivery_report
    )

def flush():
    """Flush all pending messages to Kafka."""
    producer.flush()

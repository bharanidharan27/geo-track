import json
import os

from kafka import KafkaProducer
from dotenv import load_dotenv

try:
    from utils.logistics_config import get_supported_regions
except ImportError:
    from generator.utils.logistics_config import get_supported_regions

load_dotenv()

KAFKA_TOPIC_LIST = get_supported_regions()


def create_producer():
    return KafkaProducer(
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
        security_protocol="SASL_SSL",
        sasl_mechanism=os.getenv("KAFKA_SASL_MECHANISM"),
        sasl_plain_username=os.getenv("KAFKA_USER"),
        sasl_plain_password=os.getenv("KAFKA_PASSWORD"),
        acks="all",
        linger_ms=10,
        retries=100,
        key_serializer=lambda k: str(k).encode() if k is not None else None,
        value_serializer=lambda v: json.dumps(v).encode(),
    )


def on_success(metadata):
    print(f"Sent to topic '{metadata.topic}' partition {metadata.partition} at offset {metadata.offset}")


def on_error(error):
    print(f"Error sending message: {error}")


def enqueue_message(producer, msg, topic):
    if topic not in KAFKA_TOPIC_LIST:
        print(f"Invalid topic: {topic}. Message not sent.")
        return

    future = producer.send(
        topic=topic,
        key=msg["tracking_id"],
        value=msg,
    )
    future.add_callback(on_success)
    future.add_errback(on_error)


def enqueue_batch_messages(producer, msgs):
    for msg in msgs:
        topic = msg["facility_region"]
        if not topic:
            print("Message missing 'facility_region' field. Skipped:", msg)
            continue
        enqueue_message(producer, msg, topic)

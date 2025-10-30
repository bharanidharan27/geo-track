from kafka import KafkaConsumer
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

KAFKA_TOPIC = "us-west"

consumer = KafkaConsumer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    security_protocol="SASL_SSL",
    sasl_mechanism=os.getenv("KAFKA_SASL_MECHANISM"),
    sasl_plain_username=os.getenv("KAFKA_USER"),
    sasl_plain_password=os.getenv("KAFKA_PASSWORD"),
    group_id=os.getenv("KAFKA_CONSUMER_GROUP_ID"),
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    consumer_timeout_ms=10000
)
consumer.subscribe([KAFKA_TOPIC])

try:
    for message in consumer:
        topic_info = f"topic: {message.topic} ({message.partition}|{message.offset})"
        key = message.key.decode() if message.key else None
        val = message.value.decode() if message.value else None
        message_info = f"key: {key}, value={val}"
        print(f"{topic_info}, {message_info}")

    consumer.commit()
finally:
    consumer.close()
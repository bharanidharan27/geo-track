from kafka import KafkaConsumer
import os
from dotenv import load_dotenv

from db.db_utils import insert_scanned_events_batch
from generator.kafka_dlq_producer import send_to_dlq

# Load environment variables from .env file
load_dotenv()

KAFKA_TOPIC_LIST = ["aws-us-west-2", "aws-us-east-1", "aws-us-east-2", "aws-ap-south-1", "aws-ap-southeast-1", "dead-letter-q"]

consumer = KafkaConsumer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    security_protocol="SASL_SSL",
    sasl_mechanism=os.getenv("KAFKA_SASL_MECHANISM"),
    sasl_plain_username=os.getenv("KAFKA_USER"),
    sasl_plain_password=os.getenv("KAFKA_PASSWORD"),
    group_id=os.getenv("KAFKA_CONSUMER_GROUP_ID"),
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    # consumer_timeout_ms=10000
)

# TODO: Implementation of each consumer thread handling specific topic
consumer.subscribe(KAFKA_TOPIC_LIST)

try:
    print("Starting Kafka Consumer...")

    while True:
        records = consumer.poll(timeout_ms=500, max_records=200)
        if not records:
            continue

        batch_values = []

        for tp, msgs in records.items():
            for msg in msgs:
                topic_info = f"topic: {msg.topic} ({msg.partition}|{msg.offset})"
                key = msg.key.decode() if msg.key else None
                val = msg.value.decode() if msg.value else None
                message_info = f"key: {key}, value={val}"
                print(f"{topic_info}, {message_info}")

                if not val:
                    send_to_dlq(None, "Empty message received")
                    continue

                batch_values.append(val)
        
        if batch_values:
            insert_scanned_events_batch(batch_values)
        
        consumer.commit()
except Exception as e:
    print(f"[FATAL] Consumer failure: {str(e)}")
finally:
    consumer.close()
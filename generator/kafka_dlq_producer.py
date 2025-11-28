import socket, os, json
from kafka import KafkaProducer
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

KAFKA_DLQ_TOPIC = "dead-letter-q"

dlq_producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    security_protocol="SASL_SSL",
    sasl_mechanism=os.getenv("KAFKA_SASL_MECHANISM"),
    sasl_plain_username=os.getenv("KAFKA_USER"),
    sasl_plain_password=os.getenv("KAFKA_PASSWORD"),
    key_serializer=lambda k: str(k).encode() if k else None,
    value_serializer=lambda v: json.dumps(v).encode(),
    acks="all",
    retries=100
)

def on_success(metadata):
    print(f"[DLQ] Sent message to DLQ topic '{metadata.topic}' partition {metadata.partition} offset {metadata.offset}")

def on_error(e):
    print(f"[DLQ ERROR] Failed to send message to DLQ: {e}")

def send_to_dlq(original_msg, error_msg):
    dlq_record = {
        "error": error_msg,
        "original_message": original_msg
    }

    key = None
    if isinstance(original_msg, dict):
        key = original_msg.get("tracking_id")

    future = dlq_producer.send(
        topic="dead-letter-q", 
        key=key,
        value=dlq_record)
    
    future.add_callback(on_success)
    future.add_errback(on_error)

    dlq_producer.flush()
    print(f"[DLQ] Moving message to DLQ due to error: {error_msg}")
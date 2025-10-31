import socket, os, json
from kafka import KafkaProducer
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

KAFKA_TOPIC_LIST = ["scans.us-west", "scans.us-east", "scans.us-central", "scans.us-south"]

producer = KafkaProducer(
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
hostname = socket.gethostname().encode()

def on_success(metadata):
    print(f"Sent to topic '{metadata.topic}' partition {metadata.partition} at offset {metadata.offset}")

def on_error(e):
    print(f"Error sending message: {e}")

def enqueue_message(msg, topic):
    if topic not in KAFKA_TOPIC_LIST:
        print(f"Invalid topic: {topic}. Message not sent.")
        return
    key = msg["tracking_id"]
    future = producer.send(
        topic=topic,
        key=key,
        value=msg
    )
    future.add_callback(on_success)
    future.add_errback(on_error)
    
def enqueue_batch_messages(msgs):
    for msg in msgs:
        topic = msg["region"]
        if not topic:
            print("Message missing 'region' field. Skipped:", msg)
            continue
        enqueue_message(msg, topic)
    producer.flush()
    print("✅ Producer finished successfully.")

# enqueue_batch_messages([
#     {"tracking_id": 12345, "region": "scans.us-west", "event": "login", "user_id": 123, "timestamp": "2024-10-01T12:00:00Z"},
#     {"tracking_id": 23456, "region": "scans.us-east", "event": "purchase", "user_id": 456, "amount": 99.99, "timestamp": "2024-10-01T12:05:00Z"},
#     {"tracking_id": 34567, "region": "scans.us-central", "event": "logout", "user_id": 123, "timestamp": "2024-10-01T12:10:00Z"},
#     {"tracking_id": 45678, "region": "scans.us-south", "event": "purchase", "user_id": 789, "amount": 49.99, "timestamp": "2024-10-01T12:15:00Z" }
# ])

producer.close()
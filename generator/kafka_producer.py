import socket, os, json
from kafka import KafkaProducer
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

KAFKA_TOPIC_LIST = ["aws-us-west-2", "aws-us-east-1", "aws-us-east-2", "aws-ap-south-1", "aws-ap-southeast-1"]

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
        topic = msg["facility_region"]
        if not topic:
            print("Message missing 'region' field. Skipped:", msg)
            continue
        enqueue_message(msg, topic)
    producer.flush()
    print("✅ Producer finished successfully.")

enqueue_batch_messages([
    {"event_id": "8e1d5f7c-6b88-4c02-9b68-91af8b9358e9", "tracking_id": "PKG11111", "account_id": 101, "carrier_id": 201, "facility_region": "aws-us-west-2", "event_type": "ARRIVAL", "event_ts": "2024-10-01T10:00:00Z", "notes": "Arrived at facility"},
    {"event_id": "d4c217fa-76f0-4f92-8f88-2229b3f19f95", "tracking_id": "PKG22222", "account_id": 102, "carrier_id": 202, "facility_region": "aws-us-east-1", "event_type": "DEPARTURE", "event_ts": "2024-10-01T10:10:00Z", "notes": "Departed from facility"},
    {"event_id": "3ba8c624-96c2-4ff0-8bd2-7282a132d5ae", "tracking_id": "PKG33333", "account_id": 103, "carrier_id": 203, "facility_region": "aws-us-east-2", "event_type": "IN_TRANSIT", "event_ts": "2024-10-01T10:20:00Z", "notes": "In transit to next hub"},
    {"event_id": "a2f4b2a0-4b51-4e5f-b4df-53e820c90e34", "tracking_id": "PKG44444", "account_id": 104, "carrier_id": 204, "facility_region": "aws-ap-south-1", "event_type": "DELIVERED", "event_ts": "2024-10-01T10:30:00Z", "notes": "Package delivered"}
])

producer.close()
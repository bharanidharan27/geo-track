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
    print("Producer finished successfully.")
# How to batch queue

enqueue_batch_messages([
    {"tracking_id": "TRK00000004", "account_id": "ffb2d85a-0915-46c4-abdd-79db475d2b9e", "carrier_id": "78ec7a3e-4ec6-4b19-8b96-a3e177b79d92", "facility_region": "aws-ap-south-1", "event_type": "out_for_delivery", "event_ts": "2025-11-09T06:18:56Z", "notes": "Arrived at facility"},
    {"tracking_id": "TRK00000006", "account_id": "24cef2ee-6ce4-46e7-985b-bdf7acecaeec", "carrier_id": "725731db-38b3-448f-92e7-cd6bbdd38cab", "facility_region": "aws-us-east-2", "event_type": "out_for_delivery", "event_ts": "2025-11-21T13:22:35Z", "notes": "Departed from facility"},
    # {"tracking_id": "TRK00000002", "account_id": "d1022aa5-3b69-47c7-a53c-48a92fa9fcf3", "carrier_id": "d0eb1769-79c2-4e35-bd3a-84a8bd4ccfe4", "facility_region": "aws-ap-southeast-1", "event_type": "created", "event_ts": "2025-11-10T23:04:15Z", "notes": "In transit to next hub"},
    # {"tracking_id": "TRK00000003", "account_id": "71e08387-a2ba-4a2a-a45e-e2156dd3b971", "carrier_id": "b12f940b-d921-4657-bcc3-1d487dc53864", "facility_region": "aws-ap-southeast-1", "event_type": "in_transit", "event_ts": "2025-11-13T02:01:09Z", "notes": "Package delivered"}
])

producer.close()
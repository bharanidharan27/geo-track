import socket
from kafka import KafkaProducer
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

KAFKA_TOPIC = "us-west"

producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    security_protocol="SASL_SSL",
    sasl_mechanism=os.getenv("KAFKA_SASL_MECHANISM"),
    sasl_plain_username=os.getenv("KAFKA_USER"),
    sasl_plain_password=os.getenv("KAFKA_PASSWORD"),
)
hostname = socket.gethostname().encode()

def on_success(metadata):
    print(f"Sent to topic '{metadata.topic}' partition {metadata.partition} at offset {metadata.offset}")

def on_error(e):
    print(f"Error sending message: {e}")

def enqueue_message(msg):
    future = producer.send(
        KAFKA_TOPIC,
        key=hostname,
        value=msg.encode()
    )
    future.add_callback(on_success)
    future.add_errback(on_error)
    
def enqueue_batch_messages(msgs):
    for msg in msgs:
        enqueue_message(msg)
    producer.flush()
    producer.close()
    print("✅ Producer finished successfully.")
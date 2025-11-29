from kafka import KafkaConsumer
import os, sys, json
from dotenv import load_dotenv

from db.db_utils import insert_scanned_events_batch
from generator.kafka_dlq_producer import send_to_dlq

# Load environment variables from .env file
load_dotenv()

DLQ_TOPIC = "dead-letter-q"

consumer = KafkaConsumer(
    DLQ_TOPIC,
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    security_protocol="SASL_SSL",
    sasl_mechanism=os.getenv("KAFKA_SASL_MECHANISM"),
    sasl_plain_username=os.getenv("KAFKA_USER"),
    sasl_plain_password=os.getenv("KAFKA_PASSWORD"),
    group_id=os.getenv("KAFKA_DLQ_CONSUMER_GROUP_ID"),
    auto_offset_reset="earliest",
    enable_auto_commit=False
)

print("[INFO] DLQ Consumer started. Listening on:", DLQ_TOPIC)

try:
    while True:
        records = consumer.poll(timeout_ms=1000, max_records=50)

        if not records:
            continue

        for tp, msgs in records.items():
            for msg in msgs:
                try :
                    topic_info = f"topic: {msg.topic} ({msg.partition}|{msg.offset})"
                    key = msg.key.decode() if msg.key else None
                    val = msg.value.decode() if msg.value else None

                    dlq_data = json.loads(val)
                    original = dlq_data.get("original_message")
                    error_msg = dlq_data.get("error")
                    print("\n---------------\n")
                    message_info = f"[DLQ] Error: {error_msg}, [DLQ] Original: {original}"
                    print(f"{topic_info},\n{message_info}")

                    if not original:
                        print("[WARN] No original_message. Skipping.")
                        consumer.commit()
                        continue

                    insert_scanned_events_batch([json.dumps(original)])

                    consumer.commit()
                    print("[SUCCESS] Message reprocessed successfully.")
                    
                except Exception as e:
                    print("[DLQ ERROR] Failed to process DLQ message:", str(e))
                    consumer.commit()

except KeyboardInterrupt:
    print("\n[INFO] Shutting down DLQ consumer...")
finally:
    consumer.close()
    print("[INFO] DLQ Consumer closed.")
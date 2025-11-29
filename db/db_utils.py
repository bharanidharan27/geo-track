import time, os, json
import psycopg2, psycopg2.extras
from dotenv import load_dotenv

from generator.kafka_dlq_producer import send_to_dlq
from db.db_validator import validate_scan_event

# Load environment variables from .env file
load_dotenv()
COCKROACH_URL = os.getenv("COCKROACH_URL")

def build_db_tuple(msg_value_json):
    data = json.loads(msg_value_json)

    return (
        data["account_id"],
        data["carrier_id"],
        data["tracking_id"],
        data["event_ts"],
        data["facility_region"],
        data["facility_location"],
        data["event_type"],
        data["notes"],
        data["created_at"],
    )

UPSERT_SQL = """
INSERT INTO public.scan_events (
    account_id, carrier_id, tracking_id, event_ts, facility_region, facility_location, event_type, notes, created_at
) VALUES %s
ON CONFLICT (tracking_id, event_ts, event_type) 
DO NOTHING;
"""

def insert_scanned_events_batch(batch_records):
    valid_records = []
    for record in batch_records:
        try:
            data = validate_scan_event(record)
            valid_records.append(build_db_tuple(data))
        except Exception as e:
            send_to_dlq(data, f"Validation error: {str(e)}")
    
    if not valid_records:
        return

    while True:
        try:
            with psycopg2.connect(COCKROACH_URL) as conn:
                with conn.cursor() as cur:
                    psycopg2.extras.execute_values(
                        cur,
                        UPSERT_SQL,
                        batch_records,
                        page_size=len(batch_records),
                    )
            break
        except psycopg2.Error as e:
            if e.pgcode == "40001":
                print("Retrying transaction (serialization failure)...")
                time.sleep(0.2)
                continue
            else:
                # DB error → send whole batch to DLQ
                for record in batch_records:
                    send_to_dlq(raw, f"DB error: {str(e)}")
                return
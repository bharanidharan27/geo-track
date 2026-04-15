import time
import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

from generator.kafka_dlq_producer import send_to_dlq
from db.db_validator import validate_scan_event

load_dotenv()
COCKROACH_URL = os.getenv("COCKROACH_URL")


def build_db_tuple(data):
    return (
        data["account_id"],
        data["carrier_id"],
        data["tracking_id"],
        data["event_ts"],
        data["facility_region"],
        data.get("facility_location"),
        data["event_type"],
        data.get("facility_id"),
        data.get("facility_type"),
        data.get("sequence_no"),
        data.get("journey_stage"),
        data.get("event_message"),
    )


UPSERT_SQL = """
INSERT INTO public.scan_events (
    account_id,
    carrier_id,
    tracking_id,
    event_ts,
    facility_region,
    facility_location,
    event_type,
    facility_id,
    facility_type,
    sequence_no,
    journey_stage,
    event_message
) VALUES %s
ON CONFLICT (tracking_id, event_ts, event_type, facility_region)
DO NOTHING;
"""


def insert_scanned_events_batch(batch_records):
    valid_records = []
    for record in batch_records:
        try:
            data = validate_scan_event(record)
            valid_records.append(build_db_tuple(data))
        except Exception as exc:
            send_to_dlq(record, f"Validation error: {str(exc)}")

    if not valid_records:
        return

    while True:
        try:
            with psycopg2.connect(COCKROACH_URL) as conn:
                with conn.cursor() as cur:
                    psycopg2.extras.execute_values(
                        cur,
                        UPSERT_SQL,
                        valid_records,
                        page_size=len(valid_records),
                    )
                print(f"\n[DB] Inserted batch of {len(valid_records)} records to CockroachDB successfully.\n")
            break
        except psycopg2.Error as exc:
            if exc.pgcode == "40001":
                print("Retrying transaction (serialization failure)...")
                time.sleep(0.2)
                continue

            for record in batch_records:
                send_to_dlq(record, f"DB error: {str(exc)}")
            return

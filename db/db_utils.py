import time, os, json
from datetime import datetime
import psycopg2, psycopg2.extras
from psycopg2.errors import SerializationFailure
from psycopg.rows import tuple_row
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
COCKROACH_URL = os.getenv("COCKROACH_URL")

def build_db_tuple(msg_value_json):
    data = json.loads(msg_value_json)

    return (
        data["event_id"],
        data["account_id"],
        data["carrier_id"],
        data["tracking_id"],
        data["event_ts"],
        data["facility_region"],
        data["event_type"],
        data["notes"],
        data["event_ts"],
    )

UPSERT_SQL = """
INSERT INTO public.scan_events (
    event_id, account_id, carrier_id, tracking_id, event_ts, facility_region, event_type, notes, created_at
) VALUES %s
ON CONFLICT (event_id) DO NOTHING;
"""

def insert_scanned_events_batch(batch_records):
    batch_records = [build_db_tuple(v) for v in batch_records]
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
                raise
from faker import Faker
from uuid import uuid4
import random
from datetime import datetime, timedelta, timezone

fake = Faker()

regions = ["aws-us-west-2", "aws-us-east-1", "aws-us-east-2", "aws-ap-south-1", "aws-ap-southeast-1"]
event_types = ["handoff", "arrival", "departure", "out_for_delivery", "delivered", "exception", "rts"]

def generate_fake_ids(num_accounts=1000, num_carriers=50):
    """Generate reusable fake account and carrier UUIDs."""
    accounts = [str(uuid4()) for _ in range(num_accounts)]
    carriers = [str(uuid4()) for _ in range(num_carriers)]
    return accounts, carriers

def generate_scan_event(tracking_id: str, account_id: str, carrier_id: str):
    """Generate one synthetic ScanEvent matching DB schema."""
    region = random.choice(regions)
    event = {
        "event_id": str(uuid4()),
        "account_id": account_id,
        "carrier_id": carrier_id,
        "tracking_id": tracking_id,
        "event_ts": (datetime.now(timezone.utc) - timedelta(minutes=random.randint(0, 60*24*10))).isoformat(),
        "facility_region": region,
        "event_type": random.choice(event_types),
        "notes": fake.sentence(),
    }
    return region, event

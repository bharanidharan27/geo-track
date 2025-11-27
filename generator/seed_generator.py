from faker import Faker
from uuid import uuid4
import random
from utils.region_mapper import list_supported_regions

fake = Faker()

def generate_accounts(n=1000):
    regions = list_supported_regions()
    accounts = []
    for _ in range(n):
        accounts.append({
            "id": str(uuid4()),
            "name": fake.company(),
            "tier": random.choice(["free", "pro", "enterprise"]),
            "active": True,
            "home_region": random.choice(regions),
            "created_at": fake.date_time_this_year().isoformat()
        })
    return accounts

def generate_carriers(n=50):
    carriers = []
    for _ in range(n):
        carriers.append({
            "id": str(uuid4()),
            "name": fake.company(),
            "scac": fake.unique.bothify(text="??##").upper(),
            "contact_email": fake.company_email(),
            "active": True,
            "created_at": fake.date_time_this_year().isoformat()
        })
    return carriers

def generate_parcels(accounts, carriers, n=1_000_000):
    regions = list_supported_regions()
    parcels = []
    for i in range(n):
        account = random.choice(accounts)
        carrier = random.choice(carriers)
        origin = random.choice(regions)
        dest = random.choice(regions)
        parcels.append({
            "tracking_id": f"TRK{i:08d}",
            "account_id": account["id"],
            "carrier_id": carrier["id"],
            "origin_region": origin,
            "destination_region": dest,
            "status": random.choice(["created", "in_transit", "out_for_delivery", "delivered"]),
            "last_event_ts": fake.date_time_this_month().isoformat(),
            "created_at": fake.date_time_this_month().isoformat(),
            "updated_at": fake.date_time_this_month().isoformat()
        })
    return parcels

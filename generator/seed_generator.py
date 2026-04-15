from faker import Faker
from uuid import uuid4
import random

try:
    from utils.logistics_config import get_supported_regions, list_lane_catalog
except ImportError:
    from generator.utils.logistics_config import get_supported_regions, list_lane_catalog

fake = Faker()


def generate_accounts(n=1000):
    regions = get_supported_regions()
    accounts = []
    for _ in range(n):
        accounts.append(
            {
                "id": str(uuid4()),
                "name": fake.company(),
                "tier": random.choice(["free", "pro", "enterprise"]),
                "active": True,
                "home_region": random.choice(regions),
                "created_at": fake.date_time_this_year().isoformat(),
            }
        )
    return accounts


def generate_carriers(n=50):
    carriers = []
    for _ in range(n):
        carriers.append(
            {
                "id": str(uuid4()),
                "name": fake.company(),
                "scac": fake.unique.bothify(text="??##").upper(),
                "contact_email": fake.company_email(),
                "active": True,
                "created_at": fake.date_time_this_year().isoformat(),
            }
        )
    return carriers


def generate_parcels(accounts, carriers, n=3_000_000):
    """
    Generate parcels from a supported domestic lane catalog.

    Each parcel chooses a predeclared route template so the downstream
    route planner can emit a contiguous facility path with deterministic
    timing and no impossible hops.
    """
    parcels = []
    lanes = list_lane_catalog()

    for i in range(n):
        account = random.choice(accounts)
        carrier = random.choice(carriers)
        lane = random.choice(lanes)

        parcels.append(
            {
                "tracking_id": f"TRK{i:08d}",
                "account_id": account["id"],
                "carrier_id": carrier["id"],
                "source_location": lane["origin_location"],
                "destination_location": lane["destination_location"],
                "origin_region": lane["origin_region"],
                "destination_region": lane["destination_region"],
                "status": random.choice(["created", "in_transit", "out_for_delivery", "delivered"]),
                "last_event_ts": fake.date_time_this_month().isoformat(),
                "created_at": fake.date_time_this_month().isoformat(),
                "updated_at": fake.date_time_this_month().isoformat(),
            }
        )
    return parcels

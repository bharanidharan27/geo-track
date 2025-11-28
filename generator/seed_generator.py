from faker import Faker
from uuid import uuid4
import random
from utils.region_mapper import list_supported_regions
from utils.geo_config import (
    REGION_TO_COUNTRY,
    CITY_ROUTE_ORDER,
    REGIONS_BY_COUNTRY,
    random_city_for_country,
    random_region_for_country,
)

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
    """
    Generate parcels with logically consistent source/destination locations and regions.

    - Choose a country first (IN, SG, US).
    - Pick origin/destination regions from that country's regions.
    - Pick origin/destination cities from that country's ordered corridor.
    - Store both locations and regions on the parcel record.
    """
    parcels = []

    # Only countries that we have configured
    countries = list(CITY_ROUTE_ORDER.keys())

    for i in range(n):
        account = random.choice(accounts)
        carrier = random.choice(carriers)

        country = random.choice(countries)

        origin_region = random_region_for_country(country)
        dest_region   = random_region_for_country(country)

        src_city = random_city_for_country(country)
        dst_city = random_city_for_country(country)

        source_location      = f"{src_city}, {country}"
        destination_location = f"{dst_city}, {country}"

        parcels.append({
            "tracking_id": f"TRK{i:08d}",
            "account_id": account["id"],
            "carrier_id": carrier["id"],

            # NEW
            "source_location": source_location,
            "destination_location": destination_location,

            # keep regions, but now they logically match the country
            "origin_region": origin_region,
            "destination_region": dest_region,

            "status": random.choice(["created", "in_transit", "out_for_delivery", "delivered"]),
            "last_event_ts": fake.date_time_this_month().isoformat(),
            "created_at": fake.date_time_this_month().isoformat(),
            "updated_at": fake.date_time_this_month().isoformat(),
        })
    return parcels

import multiprocessing as mp
from tqdm import tqdm
import os, sys
import random, json
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from kafka_producer import create_producer, enqueue_batch_messages

from faker import Faker

from utils.region_mapper import get_topic_for_region, list_supported_regions
from utils.geo_config import (
    REGION_TO_COUNTRY,
    CITY_ROUTE_ORDER,
    REGIONS_BY_COUNTRY,
    build_city_route,
    random_region_for_country,
)
# from event_producer import send_event, flush
from seed_generator import generate_accounts, generate_carriers, generate_parcels

fake = Faker()

def city_from_location(location: str) -> str:
    # "Delhi, IN" -> "Delhi"
    return location.split(",")[0].strip()

def country_from_location(location: str) -> str:
    # "Delhi, IN" -> "IN"
    return location.split(",")[-1].strip()

def advance_timestamp(last_ts: datetime, event_type: str) -> datetime:
    """
    Move the timestamp forward by a realistic amount depending on event_type.
    """
    if event_type in ("handoff", "arrival"):
        gap_min, gap_max = 30, 4 * 60      # 30 min – 4 hours
    elif event_type == "departure":
        gap_min, gap_max = 60, 12 * 60     # 1 – 12 hours
    elif event_type in ("out_for_delivery", "delivered"):
        gap_min, gap_max = 30, 6 * 60      # 30 min – 6 hours
    elif event_type in ("exception", "rts"):
        gap_min, gap_max = 10, 2 * 60      # 10 min – 2 hours
    else:
        gap_min, gap_max = 30, 6 * 60

    minutes = random.randint(gap_min, gap_max)
    return last_ts + timedelta(minutes=minutes)

def generate_events_for_parcel(parcel: dict, max_events_per_parcel: int = 10):
    """
    Build a logical journey for a single parcel:

    - Uses source_location / destination_location to derive origin/dest cities.
    - Builds a sequential city route inside the same country (no backtracking).
    - For each city, emits a logical sequence of event_types:
      * first city: handoff, arrival, (departure if more cities)
      * middle cities: arrival, departure
      * last city: arrival, out_for_delivery, delivered (with rare exception/rts)
    - facility_location: "<City>, <Country>"
    - facility_region: some region for that country
    """
    tracking_id = parcel["tracking_id"]
    account_id  = parcel["account_id"]
    carrier_id  = parcel["carrier_id"]

    origin_loc = parcel["source_location"]       # "Delhi, IN"
    dest_loc   = parcel["destination_location"]  # e.g. "Bengaluru, IN"

    origin_city    = city_from_location(origin_loc)
    dest_city      = city_from_location(dest_loc)
    origin_country = country_from_location(origin_loc)

    # For now we assume same-country routes (because generate_parcels enforces that)
    city_route = build_city_route(
        country=origin_country,
        origin_city=origin_city,
        dest_city=dest_city,
        max_stops=5,
    )

    # Start time: sometime in the last 10 days
    current_ts = datetime.now(timezone.utc) - timedelta(
        days=random.randint(0, 10),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )

    events = []

    for idx, city in enumerate(city_route):
        is_first = (idx == 0)
        is_last  = (idx == len(city_route) - 1)

        # region for this city: any region belonging to that country
        facility_region = random_region_for_country(origin_country)
        facility_location = f"{city}, {origin_country}"

        # Logical sequence of event types in this city
        if is_first:
            seq = ["handoff", "arrival"]
            if not is_last:
                seq.append("departure")
        elif is_last:
            seq = ["arrival"]

            # small chance of exception before delivery
            if random.random() < 0.05:
                seq.append("exception")
                if random.random() < 0.3:
                    seq.append("rts")
                    # Journey ends here
                    for ev_type in seq:
                        current_ts = advance_timestamp(current_ts, ev_type)
                        events.append(_build_event(
                            tracking_id, account_id, carrier_id,
                            current_ts, facility_location, facility_region, ev_type
                        ))
                    return events[:max_events_per_parcel]

            seq.extend(["out_for_delivery", "delivered"])
        else:
            seq = ["arrival", "departure"]

        for ev_type in seq:
            current_ts = advance_timestamp(current_ts, ev_type)
            events.append(_build_event(
                tracking_id, account_id, carrier_id,
                current_ts, facility_location, facility_region, ev_type
            ))
            if len(events) >= max_events_per_parcel:
                return events

    return events[:max_events_per_parcel]


def _build_event(tracking_id, account_id, carrier_id,
                 event_ts_dt, facility_location, facility_region, ev_type):
    return {
        "account_id": account_id,
        "carrier_id": carrier_id,
        "tracking_id": tracking_id,
        "event_ts": event_ts_dt.isoformat(),
        "facility_location": facility_location,
        "facility_region": facility_region,
        "event_type": ev_type,
    }

def build_logical_event_sequence(max_events: int) -> list[str]:
    """
    Build a logical sequence of event_types for a single parcel journey.

    Rough pattern:
      handoff -> (arrival, departure)* for 1–3 legs -> arrival -> out_for_delivery -> delivered
    with small chances of exception / rts.

    max_events is treated as an approximate upper bound.
    """
    # For a "normal" journey with n legs, events ~ 2*n + 2 (handoff + arrivals/departures + final out/delivered)
    # Bound number of legs so we don't explode past max_events.
    # Also clamp to [1, 3] to keep journeys sensible.
    max_legs_by_events = max(1, (max_events - 2) // 2) if max_events >= 4 else 1
    max_legs = min(3, max_legs_by_events)
    num_legs = random.randint(1, max_legs)

    seq: list[str] = []

    for leg in range(num_legs):
        is_first = leg == 0
        is_last = leg == num_legs - 1

        if is_first:
            seq.append("handoff")

        # Arrival at this leg's facility
        seq.append("arrival")

        if not is_last:
            # Leaving this hub
            seq.append("departure")
        else:
            # Final destination region
            # Small chance of an exception
            if random.random() < 0.05:
                seq.append("exception")
                # Some exceptions lead to RTS and end the journey
                if random.random() < 0.3:
                    seq.append("rts")
                    # End here (no out_for_delivery / delivered)
                    return seq

            # Usual out for delivery + delivered path
            seq.append("out_for_delivery")
            seq.append("delivered")

    # Just in case we overshot slightly, trim to max_events
    return seq[:max_events] if len(seq) > max_events else seq


def advance_timestamp(last_ts: datetime, event_type: str) -> datetime:
    """
    Move the timestamp forward by a realistic amount depending on event_type.
    """
    if event_type in ("handoff", "arrival"):
        # Scans inside / near facilities – shorter gaps
        gap_min, gap_max = 30, 4 * 60      # 30 min – 4 hours
    elif event_type == "departure":
        # Travel between facilities – longer gaps
        gap_min, gap_max = 60, 12 * 60     # 1 – 12 hours
    elif event_type in ("out_for_delivery", "delivered"):
        # Last mile
        gap_min, gap_max = 30, 6 * 60      # 30 min – 6 hours
    elif event_type in ("exception", "rts"):
        gap_min, gap_max = 10, 2 * 60      # 10 min – 2 hours
    else:
        gap_min, gap_max = 30, 6 * 60

    minutes = random.randint(gap_min, gap_max)
    return last_ts + timedelta(minutes=minutes)


def produce_region_events(region, parcels, events_per_parcel=10):
    """
    Each worker starts with parcels whose origin_region == region.

    For each parcel:
      - Generate a logical sequence of scan events (city route inside a country).
      - Add facility_location and facility_region.
    Events for different parcels are then interleaved so one tracking_id
    doesn't get all its scans back-to-back.
    """
    if not parcels:
        print(f"[{region}] No parcels; skipping.")
        return

    print(f"[{region}] Preparing events for {len(parcels):,} parcels...")

    # Pre-generate per-parcel event lists
    parcel_events = {}
    total_events = 0

    for parcel in tqdm(parcels, desc=f"{region}-build"):
        events = generate_events_for_parcel(parcel, max_events_per_parcel=events_per_parcel)
        if not events:
            continue
        parcel_events[parcel["tracking_id"]] = events
        total_events += len(events)
    if not parcel_events:
        print(f"[{region}] No events to produce after filtering.")
        return

    print(f"[{region}] Producing {total_events:,} events with interleaved parcels...")

    # Interleave events across parcels
    active_ids = list(parcel_events.keys())
    produced = 0
    producer = create_producer()

    events = []
    while active_ids:
        idx = random.randint(0, len(active_ids) - 1)
        tracking_id = active_ids[idx]
        events_list = parcel_events[tracking_id]

        event = events_list.pop(0)
        
        topic = get_topic_for_region(event["facility_region"])

        # send_event(topic, tracking_id, event)
        produced += 1

        if not events_list:
            active_ids.pop(idx)

        events.append(event)
        if produced % 10000 == 0:
            # flush()
            # print(json.dump(events, sys.stdout, indent=2))
            # break
            enqueue_batch_messages(producer, events)
            producer.flush()
            events = []
            print(f"[{region}] Flushed at {produced:,} events...")
    # flush()

    if events:
        enqueue_batch_messages(producer, events)
        producer.flush()
        print(f"[{region}] Final flush, total {produced} events")

    producer.close()

    print("Producer closed.")



def run_pipeline(total_parcels=3_000_000, events_per_parcel=10):
    """Generate seeds only if not already created, then spawn region processes."""
    print("🔹 Checking for existing seed files...")

    files = {
        "./data/accounts.json": generate_accounts,
        "./data/carriers.json": generate_carriers,
        "./data/parcels.json": lambda: generate_parcels(accounts, carriers, total_parcels)
    }

    # Load or generate accounts & carriers first
    if os.path.exists("./data/accounts.json"):
        print("accounts.json already exists. Skipping generation.")
        with open("./data/accounts.json", "r") as f:
            accounts = json.load(f)
    else:
        accounts = generate_accounts()
        with open("./data/accounts.json", "w") as f:
            json.dump(accounts, f)
        print("✅ accounts.json generated.")

    if os.path.exists("./data/carriers.json"):
        print("carriers.json already exists. Skipping generation.")
        with open("./data/carriers.json", "r") as f:
            carriers = json.load(f)
    else:
        carriers = generate_carriers()
        with open("./data/carriers.json", "w") as f:
            json.dump(carriers, f)
        print("✅ carriers.json generated.")

    # Parcels depend on accounts and carriers
    if os.path.exists("./data/parcels.json"):
        print("parcels.json already exists. Skipping generation.")
        with open("./data/parcels.json", "r") as f:
            parcels = json.load(f)
    else:
        parcels = generate_parcels(accounts, carriers, total_parcels)
        with open("./data/parcels.json", "w") as f:
            json.dump(parcels, f)
        print("✅ parcels.json generated.")

    print("✅ Seed data ready for pipeline.")

    # Split parcels by region (origin_region → same as scan locality)
    regions = list_supported_regions()
    grouped = {r: [] for r in regions}
    for p in parcels:
        grouped[p["origin_region"]].append(p)

    # Spawn processes
    print("Starting regional event producers...")
    procs = []
    for region, subset in grouped.items():
        p = mp.Process(target=produce_region_events, args=(region, subset, events_per_parcel))
        p.start()
        procs.append(p)

    for p in procs:
        p.join()
    print("All region producers completed.")

if __name__ == "__main__":
    run_pipeline(total_parcels=3_000_000, events_per_parcel=10)

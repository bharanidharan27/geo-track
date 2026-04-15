import multiprocessing as mp
import os
import json

from tqdm import tqdm
try:
    from kafka_producer import create_producer, enqueue_batch_messages
    from utils.region_mapper import list_supported_regions
    from seed_generator import generate_accounts, generate_carriers, generate_parcels
    from route_engine import build_timeline, interleave_parcel_events
except ImportError:
    from generator.kafka_producer import create_producer, enqueue_batch_messages
    from generator.utils.region_mapper import list_supported_regions
    from generator.seed_generator import generate_accounts, generate_carriers, generate_parcels
    from generator.route_engine import build_timeline, interleave_parcel_events


def generate_events_for_parcel(parcel: dict, max_events_per_parcel: int = 16):
    _, events = build_timeline(parcel, max_events_per_parcel=max_events_per_parcel)
    return events


def produce_region_events(region, parcels, events_per_parcel=16):
    """
    Each worker starts with parcels whose origin_region == region.

    For each parcel:
      - Compute a deterministic route from the lane catalog.
      - Build a chronological shipment timeline over that facility path.
    Events for different parcels are then interleaved so one tracking_id
    does not emit all scans back-to-back.
    """
    if not parcels:
        print(f"[{region}] No parcels; skipping.")
        return

    print(f"[{region}] Preparing events for {len(parcels):,} parcels...")

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

    interleaved_events = interleave_parcel_events(parcel_events, seed_key=region)
    produced = 0
    producer = create_producer()

    batch = []
    for event in interleaved_events:
        produced += 1
        batch.append(event)
        if produced % 10000 == 0:
            enqueue_batch_messages(producer, batch)
            producer.flush()
            batch = []
            print(f"[{region}] Flushed at {produced:,} events...")

    if batch:
        enqueue_batch_messages(producer, batch)
        producer.flush()
        print(f"[{region}] Final flush, total {produced} events")

    producer.close()
    print("Producer closed.")


def run_pipeline(total_parcels=3_000_000, events_per_parcel=16):
    """Generate seeds only if not already created, then spawn region processes."""
    print("Checking for existing seed files...")

    if os.path.exists("./data/accounts.json"):
        print("accounts.json already exists. Skipping generation.")
        with open("./data/accounts.json", "r", encoding="utf-8") as f:
            accounts = json.load(f)
    else:
        accounts = generate_accounts()
        with open("./data/accounts.json", "w", encoding="utf-8") as f:
            json.dump(accounts, f)
        print("accounts.json generated.")

    if os.path.exists("./data/carriers.json"):
        print("carriers.json already exists. Skipping generation.")
        with open("./data/carriers.json", "r", encoding="utf-8") as f:
            carriers = json.load(f)
    else:
        carriers = generate_carriers()
        with open("./data/carriers.json", "w", encoding="utf-8") as f:
            json.dump(carriers, f)
        print("carriers.json generated.")

    if os.path.exists("./data/parcels.json"):
        print("parcels.json already exists. Skipping generation.")
        with open("./data/parcels.json", "r", encoding="utf-8") as f:
            parcels = json.load(f)
    else:
        parcels = generate_parcels(accounts, carriers, total_parcels)
        with open("./data/parcels.json", "w", encoding="utf-8") as f:
            json.dump(parcels, f)
        print("parcels.json generated.")

    print("Seed data ready for pipeline.")

    regions = list_supported_regions()
    grouped = {region: [] for region in regions}
    for parcel in parcels:
        grouped[parcel["origin_region"]].append(parcel)

    print("Starting regional event producers...")
    procs = []
    for region, subset in grouped.items():
        process = mp.Process(target=produce_region_events, args=(region, subset, events_per_parcel))
        process.start()
        procs.append(process)

    for process in procs:
        process.join()

    print("All region producers completed.")


if __name__ == "__main__":
    run_pipeline(total_parcels=3_000_000, events_per_parcel=16)

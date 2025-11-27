import multiprocessing as mp
from tqdm import tqdm
import os
from utils.faker_utils import generate_scan_event
from utils.region_mapper import get_topic_for_region, list_supported_regions
# from event_producer import send_event, flush
from seed_generator import generate_accounts, generate_carriers, generate_parcels
import random, json

def produce_region_events(region, parcels, events_per_parcel=10):
    """Each worker handles ScanEvents for a specific US region."""
    total_events = len(parcels) * events_per_parcel
    print(f"[{region}] Generating {total_events:,} events...")

    for parcel in tqdm(parcels, desc=f"{region}"):
        tracking_id = parcel["tracking_id"]
        acc = parcel["account_id"]
        car = parcel["carrier_id"]

        for _ in range(events_per_parcel):
            _, event = generate_scan_event(tracking_id, acc, car)
            event["facility_region"] = region
            topic = get_topic_for_region(region)
            # send_event(topic, tracking_id, event)
        if random.randint(0, 5000) == 1:
            # flush()
            print(f"[{region}] Flushing...")
    # flush()
    print(f"✅ [{region}] Done producing {total_events:,} events.")

def run_pipeline(total_parcels=1_000_000, events_per_parcel=10):
    """Generate seeds only if not already created, then spawn region processes."""
    print("🔹 Checking for existing seed files...")

    files = {
        "./data/accounts.json": generate_accounts,
        "./data/carriers.json": generate_carriers,
        "./data/parcels.json": lambda: generate_parcels(accounts, carriers, total_parcels)
    }

    # Load or generate accounts & carriers first
    if os.path.exists("./data/accounts.json"):
        print("⚙️ accounts.json already exists. Skipping generation.")
        with open("./data/accounts.json", "r") as f:
            accounts = json.load(f)
    else:
        accounts = generate_accounts()
        with open("./data/accounts.json", "w") as f:
            json.dump(accounts, f)
        print("✅ accounts.json generated.")

    if os.path.exists("./data/carriers.json"):
        print("⚙️ carriers.json already exists. Skipping generation.")
        with open("./data/carriers.json", "r") as f:
            carriers = json.load(f)
    else:
        carriers = generate_carriers()
        with open("./data/carriers.json", "w") as f:
            json.dump(carriers, f)
        print("✅ carriers.json generated.")

    # Parcels depend on accounts and carriers
    if os.path.exists("./data/parcels.json"):
        print("⚙️ parcels.json already exists. Skipping generation.")
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
    print("🚀 Starting regional event producers...")
    procs = []
    for region, subset in grouped.items():
        p = mp.Process(target=produce_region_events, args=(region, subset, events_per_parcel))
        p.start()
        procs.append(p)

    for p in procs:
        p.join()
    print("🎯 All region producers completed.")

if __name__ == "__main__":
    run_pipeline(total_parcels=1_000_000, events_per_parcel=10)

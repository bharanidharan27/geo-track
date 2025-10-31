import multiprocessing as mp
from tqdm import tqdm
from generator.utils.faker_utils import generate_fake_ids, generate_scan_event
from generator.utils.region_mapper import get_topic_for_region, list_supported_regions
# from generator.event_producer import send_event, flush
# from event_producer import send_event, flush
import random

def produce_region_events(region, n_parcels=10000, events_per_parcel=10):
    """Worker: generates events only for a specific region."""
    accounts, carriers = generate_fake_ids()
    total_events = n_parcels * events_per_parcel
    print(f"[{region}] Generating {total_events:,} events...")

    for i in tqdm(range(n_parcels), desc=f"{region}", position=0):
        tracking_id = f"{region[:2].upper()}_TRK{i:08d}"
        account_id = random.choice(accounts)
        carrier_id = random.choice(carriers)

        for _ in range(events_per_parcel):
            # region is fixed here (no random region choice)
            _, event = generate_scan_event(tracking_id, account_id, carrier_id)
            event["facility_region"] = region
            topic = get_topic_for_region(region)
            # send_event(topic, tracking_id, event)

        if i % 5000 == 0:
            # flush()
            print(f"✅ [{region}] Produced {i:,} events.")
    # flush()
    print(f"✅ [{region}] Done producing {total_events:,} events.")

def run_parallel_generation(total_parcels=40000, events_per_parcel=10):
    """Spawn one process per region."""
    regions = list_supported_regions()
    parcels_per_region = total_parcels // len(regions)
    print(f"Spawning {len(regions)} workers → {parcels_per_region:,} parcels/region")

    procs = []
    for region in regions:
        p = mp.Process(target=produce_region_events, args=(region, parcels_per_region, events_per_parcel))
        p.start()
        procs.append(p)

    for p in procs:
        p.join()
    print("🎯 All region producers completed.")

if __name__ == "__main__":
    run_parallel_generation(total_parcels=40000, events_per_parcel=10)

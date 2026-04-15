import unittest

from generator.route_engine import build_timeline, interleave_parcel_events, plan_route, validate_route_contiguity
from generator.utils.logistics_config import FACILITIES


def make_parcel(tracking_id, source_location, destination_location):
    return {
        "tracking_id": tracking_id,
        "account_id": "account-1",
        "carrier_id": "carrier-1",
        "source_location": source_location,
        "destination_location": destination_location,
        "origin_region": source_location.split(",")[-1].strip(),
        "destination_region": destination_location.split(",")[-1].strip(),
    }


class RouteEngineTests(unittest.TestCase):
    def test_timeline_is_strictly_chronological(self):
        parcel = make_parcel("TRK-CHRONO", "New York, US", "Seattle, US")
        _, events = build_timeline(parcel)
        timestamps = [event["event_ts"] for event in events]
        self.assertEqual(timestamps, sorted(timestamps))

    def test_planned_route_is_contiguous(self):
        parcel = make_parcel("TRK-ROUTE", "Delhi, IN", "Bengaluru, IN")
        _, facilities = plan_route(parcel)
        facility_ids = [facility["facility_id"] for facility in facilities]
        self.assertTrue(validate_route_contiguity(facility_ids))

    def test_delivered_shipments_include_out_for_delivery(self):
        parcel = make_parcel("TRK-FINAL", "Singapore, SG", "Singapore, SG")
        _, events = build_timeline(parcel)
        event_types = [event["event_type"] for event in events]
        if "delivered" in event_types:
            self.assertIn("out_for_delivery", event_types)

    def test_facility_metadata_matches_catalog(self):
        parcel = make_parcel("TRK-FACILITY", "Columbus, US", "Dallas, US")
        _, events = build_timeline(parcel)
        for event in events:
            facility = FACILITIES[event["facility_id"]]
            self.assertEqual(event["facility_region"], facility["region"])
            self.assertEqual(event["facility_location"], facility["location"])
            self.assertEqual(event["facility_type"], facility["facility_type"])

    def test_interleave_preserves_intra_tracking_order(self):
        parcel_one = make_parcel("TRK-INT-1", "Mumbai, IN", "Delhi, IN")
        parcel_two = make_parcel("TRK-INT-2", "New York, US", "Chicago, US")
        _, events_one = build_timeline(parcel_one)
        _, events_two = build_timeline(parcel_two)
        merged = interleave_parcel_events(
            {
                "TRK-INT-1": events_one,
                "TRK-INT-2": events_two,
            },
            seed_key="merge-check",
        )

        by_tracking = {}
        for event in merged:
            by_tracking.setdefault(event["tracking_id"], []).append(event["sequence_no"])

        self.assertEqual(by_tracking["TRK-INT-1"], sorted(by_tracking["TRK-INT-1"]))
        self.assertEqual(by_tracking["TRK-INT-2"], sorted(by_tracking["TRK-INT-2"]))

    def test_rts_is_terminal_when_present(self):
        found_rts = False
        for index in range(200):
            parcel = make_parcel(f"TRK-RTS-{index}", "Chicago, US", "Seattle, US")
            _, events = build_timeline(parcel)
            event_types = [event["event_type"] for event in events]
            if "rts" in event_types:
                found_rts = True
                self.assertEqual(event_types[-1], "rts")
                break
        self.assertTrue(found_rts)


if __name__ == "__main__":
    unittest.main()

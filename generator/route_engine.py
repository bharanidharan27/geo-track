from __future__ import annotations

import hashlib
import random
from datetime import datetime, timedelta, timezone

try:
    from utils.logistics_config import (
        EVENT_MESSAGE_TEMPLATES,
        FACILITIES,
        LANE_CATALOG,
        STATUS_BY_EVENT_TYPE,
        TIMING_RULES,
        get_lane_for_locations,
    )
except ImportError:
    from generator.utils.logistics_config import (
        EVENT_MESSAGE_TEMPLATES,
        FACILITIES,
        LANE_CATALOG,
        STATUS_BY_EVENT_TYPE,
        TIMING_RULES,
        get_lane_for_locations,
    )


def deterministic_rng(tracking_id: str) -> random.Random:
    seed = int(hashlib.sha256(tracking_id.encode("utf-8")).hexdigest()[:16], 16)
    return random.Random(seed)


def choose_lane(parcel: dict, rng: random.Random):
    try:
        return get_lane_for_locations(parcel["source_location"], parcel["destination_location"])
    except Exception:
        country = parcel["source_location"].split(",")[-1].strip()
        candidates = [lane for lane in LANE_CATALOG.values() if lane["country"] == country]
        return rng.choice(candidates)


def plan_route(parcel: dict, rng: random.Random | None = None):
    rng = rng or deterministic_rng(parcel["tracking_id"])
    lane = choose_lane(parcel, rng)
    facilities = [FACILITIES[facility_id] for facility_id in lane["path"]]
    return lane, facilities


def journey_stage_for_event(event_type: str) -> str:
    if event_type in {"order_submitted", "label_created"}:
        return "order"
    if event_type == "picked_up":
        return "pickup"
    if event_type in {"arrived_origin_hub", "departed_origin_hub"}:
        return "origin_processing"
    if event_type in {"in_transit", "arrived_destination_hub"}:
        return "linehaul"
    if event_type == "arrived_delivery_station":
        return "destination_processing"
    if event_type in {"out_for_delivery", "delivered"}:
        return "last_mile"
    return "exception"


def parcel_status_from_event(event_type: str) -> str:
    return STATUS_BY_EVENT_TYPE.get(event_type, "in_transit")


def _advance_timestamp(last_ts: datetime, event_type: str, rng: random.Random, span_multiplier: int = 1):
    low, high = TIMING_RULES[event_type]
    minutes = rng.randint(low * span_multiplier, high * span_multiplier)
    next_ts = last_ts + timedelta(minutes=minutes)

    if event_type == "out_for_delivery" and next_ts.hour < 7:
        next_ts = next_ts.replace(hour=7, minute=rng.randint(0, 45), second=0, microsecond=0)
    elif event_type == "delivered" and next_ts.hour < 9:
        next_ts = next_ts.replace(hour=9, minute=rng.randint(0, 50), second=0, microsecond=0)

    return next_ts


def _append_event(events: list[dict], parcel: dict, facility: dict, event_type: str, event_ts: datetime):
    events.append(
        {
            "account_id": parcel["account_id"],
            "carrier_id": parcel["carrier_id"],
            "tracking_id": parcel["tracking_id"],
            "event_ts": event_ts.isoformat(),
            "facility_region": facility["region"],
            "facility_location": facility["location"],
            "facility_id": facility["facility_id"],
            "facility_type": facility["facility_type"],
            "sequence_no": len(events) + 1,
            "journey_stage": journey_stage_for_event(event_type),
            "event_type": event_type,
            "event_message": EVENT_MESSAGE_TEMPLATES.get(event_type),
        }
    )


def _build_base_timeline(parcel: dict, facilities: list[dict], rng: random.Random):
    pickup = facilities[0]
    hubs = facilities[1:-1]
    station = facilities[-1]
    is_local_delivery = len(hubs) == 1

    current_ts = datetime.now(timezone.utc) - timedelta(
        days=rng.randint(1, 14),
        hours=rng.randint(0, 23),
        minutes=rng.randint(0, 59),
    )

    events = []

    for event_type in ("order_submitted", "label_created", "picked_up"):
        current_ts = _advance_timestamp(current_ts, event_type, rng)
        _append_event(events, parcel, pickup, event_type, current_ts)

    if hubs:
        current_ts = _advance_timestamp(current_ts, "arrived_origin_hub", rng)
        _append_event(events, parcel, hubs[0], "arrived_origin_hub", current_ts)

        if len(hubs) > 1:
            current_ts = _advance_timestamp(current_ts, "departed_origin_hub", rng)
            _append_event(events, parcel, hubs[0], "departed_origin_hub", current_ts)

            for hop_index, hub in enumerate(hubs[1:-1], start=1):
                current_ts = _advance_timestamp(current_ts, "in_transit", rng, span_multiplier=hop_index + 1)
                _append_event(events, parcel, hub, "in_transit", current_ts)

            current_ts = _advance_timestamp(current_ts, "arrived_destination_hub", rng, span_multiplier=max(1, len(hubs) - 1))
            _append_event(events, parcel, hubs[-1], "arrived_destination_hub", current_ts)
        elif not is_local_delivery:
            current_ts = _advance_timestamp(current_ts, "arrived_destination_hub", rng)
            _append_event(events, parcel, hubs[0], "arrived_destination_hub", current_ts)

    if rng.random() < 0.12:
        delay_anchor = hubs[-1] if hubs else pickup
        current_ts = _advance_timestamp(current_ts, "delay", rng)
        _append_event(events, parcel, delay_anchor, "delay", current_ts)

    current_ts = _advance_timestamp(current_ts, "arrived_delivery_station", rng)
    _append_event(events, parcel, station, "arrived_delivery_station", current_ts)

    current_ts = _advance_timestamp(current_ts, "out_for_delivery", rng)
    _append_event(events, parcel, station, "out_for_delivery", current_ts)

    if rng.random() < 0.08:
        current_ts = _advance_timestamp(current_ts, "exception", rng)
        _append_event(events, parcel, station, "exception", current_ts)

        current_ts = _advance_timestamp(current_ts, "failed_delivery", rng)
        _append_event(events, parcel, station, "failed_delivery", current_ts)

        if rng.random() < 0.35:
            current_ts = _advance_timestamp(current_ts, "rts", rng)
            _append_event(events, parcel, station, "rts", current_ts)
            return events

        current_ts = _advance_timestamp(current_ts, "out_for_delivery", rng)
        _append_event(events, parcel, station, "out_for_delivery", current_ts)

    current_ts = _advance_timestamp(current_ts, "delivered", rng)
    _append_event(events, parcel, station, "delivered", current_ts)
    return events


def build_timeline(parcel: dict, max_events_per_parcel: int | None = None):
    rng = deterministic_rng(parcel["tracking_id"])
    lane, facilities = plan_route(parcel, rng)
    events = _build_base_timeline(parcel, facilities, rng)
    if max_events_per_parcel is not None:
        return lane, events[:max_events_per_parcel]
    return lane, events


def validate_route_contiguity(facility_ids: list[str]) -> bool:
    for current_id, next_id in zip(facility_ids, facility_ids[1:]):
        current = FACILITIES[current_id]
        if next_id not in current["allowed_next_hops"]:
            return False
    return True


def interleave_parcel_events(parcel_events: dict[str, list[dict]], seed_key: str = "interleave"):
    active = {tracking_id: list(events) for tracking_id, events in parcel_events.items() if events}
    rng = deterministic_rng(seed_key)
    ordered_events = []

    while active:
        tracking_id = rng.choice(sorted(active.keys()))
        ordered_events.append(active[tracking_id].pop(0))
        if not active[tracking_id]:
            del active[tracking_id]

    return ordered_events

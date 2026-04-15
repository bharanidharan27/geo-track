from __future__ import annotations

from itertools import product


CITY_CORRIDORS = {
    "IN": ["Delhi", "Mumbai", "Bengaluru"],
    "SG": ["Singapore"],
    "US": ["New York", "Columbus", "Chicago", "Dallas", "Denver", "Seattle"],
}

CITY_REGION_MAP = {
    "IN": {
        "Delhi": "aws-ap-south-1",
        "Mumbai": "aws-ap-south-1",
        "Bengaluru": "aws-ap-south-1",
    },
    "SG": {
        "Singapore": "aws-ap-southeast-1",
    },
    "US": {
        "New York": "aws-us-east-1",
        "Columbus": "aws-us-east-2",
        "Chicago": "aws-us-east-2",
        "Dallas": "aws-us-west-2",
        "Denver": "aws-us-west-2",
        "Seattle": "aws-us-west-2",
    },
}

FACILITY_TYPE_ALIASES = {
    "pickup_partner": "Pickup Partner",
    "origin_hub": "Origin Hub",
    "transit_hub": "Transit Hub",
    "destination_hub": "Destination Hub",
    "delivery_station": "Delivery Station",
}

EVENT_DISPLAY_NAMES = {
    "order_submitted": "Order Submitted",
    "label_created": "Label Created",
    "picked_up": "Picked Up",
    "arrived_origin_hub": "Arrived at Origin Hub",
    "departed_origin_hub": "Departed Origin Hub",
    "in_transit": "In Transit",
    "arrived_destination_hub": "Arrived at Destination Hub",
    "arrived_delivery_station": "Arrived at Delivery Station",
    "out_for_delivery": "Out for Delivery",
    "delivered": "Delivered",
    "delay": "Delayed",
    "exception": "Exception",
    "failed_delivery": "Delivery Attempt Failed",
    "rts": "Return to Sender",
    "handoff": "Handed Off",
    "arrival": "Arrival Scan",
    "departure": "Departure Scan",
}

EVENT_MESSAGE_TEMPLATES = {
    "order_submitted": "Customer order has been submitted.",
    "label_created": "Shipping label has been created and the shipment is queued for pickup.",
    "picked_up": "Package has been picked up from the shipper.",
    "arrived_origin_hub": "Package arrived at the origin processing hub.",
    "departed_origin_hub": "Package departed the origin hub for linehaul transport.",
    "in_transit": "Package is moving between logistics facilities.",
    "arrived_destination_hub": "Package arrived at the destination regional hub.",
    "arrived_delivery_station": "Package reached the local delivery station.",
    "out_for_delivery": "Courier is carrying the package for final delivery.",
    "delivered": "Package has been delivered successfully.",
    "delay": "Shipment is delayed due to an operational hold.",
    "exception": "Delivery exception recorded for this shipment.",
    "failed_delivery": "A delivery attempt was made but did not complete.",
    "rts": "Shipment is being returned to the sender.",
}

TIMING_RULES = {
    "order_submitted": (5, 45),
    "label_created": (15, 120),
    "picked_up": (60, 12 * 60),
    "arrived_origin_hub": (90, 10 * 60),
    "departed_origin_hub": (45, 6 * 60),
    "in_transit": (6 * 60, 36 * 60),
    "arrived_destination_hub": (2 * 60, 12 * 60),
    "arrived_delivery_station": (60, 8 * 60),
    "out_for_delivery": (4 * 60, 16 * 60),
    "delivered": (60, 10 * 60),
    "delay": (4 * 60, 24 * 60),
    "exception": (20, 3 * 60),
    "failed_delivery": (30, 4 * 60),
    "rts": (6 * 60, 36 * 60),
}

STATUS_BY_EVENT_TYPE = {
    "order_submitted": "created",
    "label_created": "created",
    "picked_up": "in_transit",
    "arrived_origin_hub": "in_transit",
    "departed_origin_hub": "in_transit",
    "in_transit": "in_transit",
    "arrived_destination_hub": "in_transit",
    "arrived_delivery_station": "in_transit",
    "out_for_delivery": "out_for_delivery",
    "delivered": "delivered",
    "delay": "exception",
    "exception": "exception",
    "failed_delivery": "failed_delivery",
    "rts": "rts",
    "handoff": "in_transit",
    "arrival": "in_transit",
    "departure": "in_transit",
}

SUPPORTED_EVENT_TYPES = tuple(EVENT_DISPLAY_NAMES.keys())
TRACKABLE_STATUSES = tuple(sorted(set(STATUS_BY_EVENT_TYPE.values())))


def _facility_id(country: str, city: str, suffix: str) -> str:
    normalized = city.lower().replace(" ", "-")
    return f"{country.lower()}-{normalized}-{suffix}"


def _location(city: str, country: str) -> str:
    return f"{city}, {country}"


def build_facilities():
    facilities = {}

    for country, cities in CITY_CORRIDORS.items():
        for index, city in enumerate(cities):
            region = CITY_REGION_MAP[country][city]
            pickup_id = _facility_id(country, city, "pickup")
            hub_id = _facility_id(country, city, "hub")
            station_id = _facility_id(country, city, "station")

            if index == 0:
                hub_type = "origin_hub"
            elif index == len(cities) - 1:
                hub_type = "destination_hub"
            else:
                hub_type = "transit_hub"

            facilities[pickup_id] = {
                "facility_id": pickup_id,
                "facility_type": "pickup_partner",
                "city": city,
                "country": country,
                "region": region,
                "location": _location(city, country),
                "allowed_next_hops": [hub_id],
            }
            facilities[hub_id] = {
                "facility_id": hub_id,
                "facility_type": hub_type,
                "city": city,
                "country": country,
                "region": region,
                "location": _location(city, country),
                "allowed_next_hops": [],
            }
            facilities[station_id] = {
                "facility_id": station_id,
                "facility_type": "delivery_station",
                "city": city,
                "country": country,
                "region": region,
                "location": _location(city, country),
                "allowed_next_hops": [],
            }

        for index, city in enumerate(cities):
            hub_id = _facility_id(country, city, "hub")
            station_id = _facility_id(country, city, "station")
            next_hops = [station_id]

            if index > 0:
                prev_city = cities[index - 1]
                next_hops.append(_facility_id(country, prev_city, "hub"))
            if index < len(cities) - 1:
                next_city = cities[index + 1]
                next_hops.append(_facility_id(country, next_city, "hub"))

            facilities[hub_id]["allowed_next_hops"] = next_hops

    return facilities


FACILITIES = build_facilities()


def build_lane_catalog():
    lanes = {}

    for country, cities in CITY_CORRIDORS.items():
        for origin_city, destination_city in product(cities, cities):
            start_idx = cities.index(origin_city)
            end_idx = cities.index(destination_city)
            step = 1 if end_idx >= start_idx else -1
            hub_cities = cities[start_idx:end_idx + step:step]

            pickup_id = _facility_id(country, origin_city, "pickup")
            station_id = _facility_id(country, destination_city, "station")
            hub_ids = [_facility_id(country, city, "hub") for city in hub_cities]

            lane_id = f"{country}:{origin_city}:{destination_city}"
            lanes[lane_id] = {
                "lane_id": lane_id,
                "country": country,
                "origin_city": origin_city,
                "destination_city": destination_city,
                "origin_region": CITY_REGION_MAP[country][origin_city],
                "destination_region": CITY_REGION_MAP[country][destination_city],
                "path": [pickup_id, *hub_ids, station_id],
                "hub_path": hub_ids,
                "service_level": "standard",
                "origin_location": _location(origin_city, country),
                "destination_location": _location(destination_city, country),
            }

    return lanes


LANE_CATALOG = build_lane_catalog()


def get_supported_regions():
    return sorted({facility["region"] for facility in FACILITIES.values()})


def get_facility(facility_id: str):
    return FACILITIES[facility_id]


def get_lane(country: str, origin_city: str, destination_city: str):
    return LANE_CATALOG[f"{country}:{origin_city}:{destination_city}"]


def get_lane_for_locations(origin_location: str, destination_location: str):
    origin_city, country = [part.strip() for part in origin_location.split(",")]
    destination_city = destination_location.split(",")[0].strip()
    return get_lane(country, origin_city, destination_city)


def list_lane_catalog():
    return list(LANE_CATALOG.values())

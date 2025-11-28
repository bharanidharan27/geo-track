# generator/utils/geo_config.py

import random
from typing import List, Dict

# Map your regions (as in list_supported_regions) to countries
REGION_TO_COUNTRY: Dict[str, str] = {
    "aws-us-west-2": "US",      # Oregon
    "aws-us-east-2": "US",      # Ohio
    "aws-us-east-1": "US",      # N. Virginia
    "aws-ap-south-1": "IN",     # Mumbai
    "aws-ap-southeast-1": "SG", # Singapore
}

# Ordered city corridors per country
CITY_ROUTE_ORDER: Dict[str, List[str]] = {
    # India: north → west → south
    "IN": ["Delhi", "Mumbai", "Bengaluru"],
    # Singapore is a city-state
    "SG": ["Singapore"],
    # US example: east → midwest → south → mountain/west
    "US": ["New York", "Columbus", "Chicago", "Dallas", "Denver", "Seattle"],
}

# Regions available per country
REGIONS_BY_COUNTRY: Dict[str, List[str]] = {}
for region, country in REGION_TO_COUNTRY.items():
    REGIONS_BY_COUNTRY.setdefault(country, []).append(region)


def random_city_for_country(country: str) -> str:
    """Pick a random city for a given country code."""
    return random.choice(CITY_ROUTE_ORDER[country])


def random_region_for_country(country: str) -> str:
    """Pick a random region belonging to a given country."""
    return random.choice(REGIONS_BY_COUNTRY[country])


def build_city_route(country: str,
                     origin_city: str,
                     dest_city: str,
                     max_stops: int | None = None) -> List[str]:
    """
    Build an ordered list of cities for this parcel journey inside one country.

    - Uses CITY_ROUTE_ORDER[country]
    - Route is a contiguous slice from origin_city to dest_city, either
      forward or backward (no direction changes).
    """
    cities = CITY_ROUTE_ORDER[country]

    if origin_city not in cities or dest_city not in cities:
        # Fallback: just start and end
        return [origin_city, dest_city] if origin_city != dest_city else [origin_city]

    origin_idx = cities.index(origin_city)
    dest_idx = cities.index(dest_city)

    if origin_idx == dest_idx:
        return [origin_city]

    step = 1 if dest_idx > origin_idx else -1

    if max_stops is not None:
        max_span = max_stops - 1
        if abs(dest_idx - origin_idx) > max_span:
            dest_idx = origin_idx + step * max_span

    route = cities[origin_idx:dest_idx + step:step]
    return route

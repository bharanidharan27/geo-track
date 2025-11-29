import json

def validate_scan_event(raw_json):
    """
    Basic validation so the consumer doesn't crash.
    Leave strict validation to the database.
    """
    try:
        data = json.loads(raw_json)
    except Exception:
        raise ValueError("Message is not valid JSON")

    required = [
        "account_id",
        "carrier_id",
        "tracking_id",
        "event_ts",
        "facility_region",
        "event_type"
    ]

    for key in required:
        if key not in data:
            raise ValueError(f"Missing field: {key}")

    return data

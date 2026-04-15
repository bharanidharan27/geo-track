import json


def validate_scan_event(raw_json):
    """
    Basic validation so the consumer does not crash.
    Leave strict validation to the database.
    """
    if isinstance(raw_json, dict):
        data = raw_json
    else:
        try:
            data = json.loads(raw_json)
        except Exception as exc:
            raise ValueError("Message is not valid JSON") from exc

    required = [
        "account_id",
        "carrier_id",
        "tracking_id",
        "event_ts",
        "facility_region",
        "event_type",
    ]

    for key in required:
        if key not in data:
            raise ValueError(f"Missing field: {key}")

    sequence_no = data.get("sequence_no")
    if sequence_no is not None and int(sequence_no) < 1:
        raise ValueError("sequence_no must be positive")

    return data

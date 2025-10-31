def get_topic_for_region(region: str) -> str:
    """Return Kafka topic name based on facility_region."""
    return f"scans.{region}"

def list_supported_regions():
    """List all available regions for event generation."""
    return ["us-west", "us-east", "us-central", "us-south"]

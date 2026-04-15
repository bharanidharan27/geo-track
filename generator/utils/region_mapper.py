def get_topic_for_region(region: str) -> str:
    """Return Kafka topic name based on facility_region."""
    return f"scans.{region}"


def list_supported_regions():
    """List all available regions for event generation."""
    try:
        from utils.logistics_config import get_supported_regions
    except ImportError:
        from generator.utils.logistics_config import get_supported_regions

    return get_supported_regions()

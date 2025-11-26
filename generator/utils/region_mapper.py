def get_topic_for_region(region: str) -> str:
    """Return Kafka topic name based on facility_region."""
    return f"scans.{region}"

def list_supported_regions():
    """List all available regions for event generation."""
    return ["aws-us-west-2", "aws-us-east-1", "aws-us-east-2", "aws-ap-south-1", "aws-ap-southeast-1"]

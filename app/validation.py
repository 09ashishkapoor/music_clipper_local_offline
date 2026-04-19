import re

def validate_timestamp(ts_str):
    """Validate if timestamp is in MM:SS or HH:MM:SS format."""
    if not ts_str:
        return False
    # Regex for MM:SS or HH:MM:SS
    pattern = r'^(\d{1,2}:)?([0-5]?\d):([0-5]\d)$'
    return bool(re.match(pattern, ts_str))

def validate_range(start_secs, end_secs, total_duration):
    """Validate that the range is logical and within bounds."""
    if start_secs is None or end_secs is None:
        return False, "Invalid timestamp format."
    if start_secs < 0:
        return False, "Start time cannot be negative."
    if start_secs >= end_secs:
        return False, "Start time must be before end time."
    if total_duration and end_secs > total_duration:
        return False, f"End time exceeds file duration ({total_duration:.2f}s)."
    return True, ""


def parse_positive_int(value_str, min_value=1):
    """Parse a positive integer from a string. Returns int or None."""
    try:
        value = int(str(value_str).strip())
    except Exception:
        return None

    if value < min_value:
        return None

    return value

from datetime import datetime
from typing import Union, Optional
import re


def convert_to_epoch(time_input: Union[datetime, int, str]) -> int:
    if isinstance(time_input, datetime):
        return int(time_input.timestamp())
    elif isinstance(time_input, int):
        return time_input
    elif isinstance(time_input, str):
        dt = datetime.fromisoformat(time_input)
        return int(dt.timestamp())
    else:
        raise ValueError("Invalid time input type. Must be datetime, int, or str.")


def extract_timestamp(trading_date_str, ns):
    trading_date_str = str(trading_date_str)
    # Regular expression to match and extract the timestamp
    match = re.search(r'(\d+)', trading_date_str)
    if match:
        timestamp = int(match.group(1)) / ns  # Convert milliseconds to seconds
        return timestamp
    return None


def to_time_s(d, ns=1000) -> Optional[str]:
    try:
        return datetime.fromtimestamp(extract_timestamp(d, ns)).__str__()
    except (ValueError, TypeError):
        return None


def flatten_nested_dict(nested_dict):
    result = []

    def flatten(element):
        if isinstance(element, list):
            for item in element:
                flatten(item)
        elif isinstance(element, dict):
            for key in element:
                flatten(element[key])
        else:
            result.append(element)

    flatten(nested_dict)
    return result

import json
from datetime import datetime
from functools import lru_cache
from typing import Union
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


def to_time_s(d, ns=1000) -> str:
    try:
        return datetime.fromtimestamp(extract_timestamp(d, ns)).__str__()
    except ValueError:
        return None


@lru_cache(maxsize=1)
def get_cookies():
    # read cookies.json
    cookies = json.loads(open('cookies.json').read())
    return {cookie['name']: cookie['value'] for cookie in cookies}


if __name__ == "__main__":
    print(get_cookies())

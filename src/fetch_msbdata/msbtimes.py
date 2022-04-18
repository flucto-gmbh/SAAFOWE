from datetime import datetime, timezone
import time
import sys

def parse_fmt_timestamp_string(timestamp_string : str, fmt : str = "%Y-%m-%dT%H-%M-%S") -> datetime:
    try:
        timestamp = datetime(*time.strptime(timestamp_string, fmt)[:6])
    except Exception as e:
        print(f'failed to parse time stamp: {timestamp_string}: {e}')
        sys.exit()
    timestamp = timestamp.replace(tzinfo=timezone.utc)
    return timestamp

def parse_generic_timestamp_string(timestamp_string : str) -> datetime:
    try:
        timestamp = datetime.fromisoformat(timestamp_string)
    except Exception as e:
        print(f'failed to parse time stamp: {timestamp_string}: {e}')
        sys.exit()
    timestamp = timestamp.replace(tzinfo=timezone.utc)
    return timestamp

def parse_begin_end(config : dict) -> tuple:
    if config['begin']:
        begin = parse_generic_timestamp_string(config['begin'])
    else:
        begin = datetime.fromtimestamp(time.time(), timezone.utc)
    if config['end']:
        end = parse_generic_timestamp_string(config['end'])
    else:
        end = datetime.fromtimestamp(0, timezone.utc)
    return (begin, end)



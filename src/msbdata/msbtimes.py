from datetime import datetime, timezone, timedelta
import time
import sys

AGGREGATION_INTERVALS = ["hourly", "daily", "weekly", "monthly", "all"]

def parse_fmt_timestamp_string(timestamp_string : str, fmt : str = "%Y-%m-%dT%H-%M-%S", verbose=False) -> datetime:
    try:
        timestamp = datetime(*time.strptime(timestamp_string, fmt)[:6])
    except Exception as e:
        if verbose:
            print(f'failed to parse time stamp: {timestamp_string}: {e}.. skipping')
        return None
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
        begin = datetime.fromtimestamp(0, timezone.utc)
    if config['end']:
        end = parse_generic_timestamp_string(config['end'])
    else:
        end = datetime.fromtimestamp(time.time(), timezone.utc)
    return (begin, end)

def are_in_equivalent_datetime_interval(
    timestamp: datetime, interval_boundary: datetime, interval: str
) -> bool:
    """
    receives two tuples objects x and y and checks if they are datetime
    in their first field are equivalent
    """
    assert interval in AGGREGATION_INTERVALS
    if interval == "all":
        return True
    elif interval == "hourly":
        return (
            # timestamp.year == interval_boundary.year and
            # timestamp.month == interval_boundary.month and
            # timestamp.day == interval_boundary.day and
            timestamp
            <= (
                datetime(
                    year=interval_boundary.year,
                    month=interval_boundary.month,
                    day=interval_boundary.day,
                    hour=interval_boundary.hour,
                    tzinfo=timezone.utc,
                )
                + timedelta(hours=1)
            )
        )
    elif interval == "daily":
        return (
            timestamp.year == interval_boundary.year
            and timestamp.month == interval_boundary.month
            and timestamp.day == interval_boundary.day
        )
    elif interval == "weekly":
        dx = date(timestamp.year, timestamp.month, timestamp.day)
        dy = date(
            interval_boundary.year, interval_boundary.month, interval_boundary.day
        )
        return (
            timestamp.year == interval_boundary.year
            and timestamp.month == interval_boundary.month
            and dx.isocalendar().week == dy.isocalendar().week
        )
    elif interval == "monthly":
        return (
            timestamp.year == interval_boundary.year
            and timestamp.month == interval_boundary.month
        )



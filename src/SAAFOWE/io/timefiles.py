from datetime import (datetime, timezone, timedelta)
from glob import glob
from os import path
import sys
import time

from anyio import current_time

def find_time_files(
    file_dir: str,
    file_pattern: str = "*.csv",
    begin: datetime = datetime.fromisoformat("1970-01-01T00:00:00+00:00"),
    end: datetime = datetime.fromtimestamp(time.time(), timezone.utc),
    verbose=False,
) -> list:

    files = list()

    for file in sorted(glob(path.join(file_dir, file_pattern))):
        timestamp = datetime.fromisoformat(file.split("_")[-1].split(".")[0])
        if verbose:
            print(f"timestamp: {timestamp}")
        if begin <= timestamp <= end:
            if verbose:
                print(f"matching file: {file}")
            files.append(file)
            continue
        if verbose:
            print(f"skipping: {file}")

    return files

def calc_time_intervals(begin : datetime, end : datetime, interval : str = 'hour', ) -> list:

    timestamps = list()
    timestamps.append(begin)
    counter = 1
    interval_start = None
    current_timestamp = begin
    

    if interval == 'hour':
        td = timedelta(hours=1)
        interval_start = datetime(year=begin.year, month=begin.month, day=begin.day, hour=begin.hour, tzinfo=begin.tzinfo)
    elif interval == 'day':
        td = timedelta(hours=24)
        interval_start = datetime(year=begin.year, month=begin.month, day=begin.day, tzinfo=begin.tzinfo)
    #elif interval == 'week':
    #    td = timedelta(weeks=1)
    elif interval == 'month':
        td = timedelta(weeks=4)
        interval_start = datetime(year=begin.year, month=begin.month, tzinfo=begin.tzinfo)
    else:
        print(f'unknown interval {interval}')
        sys.exit()
    
    while current_timestamp < end:
        current_timestamp = interval_start + (td * counter)
        timestamps.append(current_timestamp) 
        counter += 1

    # the last interval is either exactly the end time stamp or overshoots
    # thus replace it with the end time stamp
    timestamps[-1] = end

    return timestamps
    


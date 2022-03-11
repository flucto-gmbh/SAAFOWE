from datetime import (datetime, timezone, timedelta)
from glob import glob
from os import path
import sys
import time

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

def calc_time_intervals(begin : datetime, end : datetime, interval : str = 'hourly', ) -> list:

    timestamps = list()
    timestamps.append(begin)
    counter = 1
    interval_start = None
    current_timestamp = begin

    if interval == 'hourly':
        td = timedelta(hours=1)
        interval_start = datetime(year=begin.year, month=begin.month, day=begin.day, hour=begin.hour, tzinfo=begin.tzinfo)
    elif interval == 'daily':
        td = timedelta(hours=24)
        interval_start = datetime(year=begin.year, month=begin.month, day=begin.day, tzinfo=begin.tzinfo)
    #elif interval == 'week':
    #    td = timedelta(weeks=1)
    elif interval == 'monthly':
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
    
def get_filename_prefix(filepath : str, prefix : str, filename_sep : str = '_') -> str:
    filename_without_timestamp = '_'.join(filepath.split(path.sep)[-1].split(filename_sep)[:-1])
    return f'{prefix}_{filename_without_timestamp}'


def get_filename_ending(filepath : str) -> str:
    return filepath.split('.')[-1]


def get_output_filepath(output_dir : str, filename_prefix : str, timestamp : datetime, filename_ending : str, filename_sep = "_", timestamp_fmt = '%Y-%m-%dT%H:%M:%S%z'):
    assert path.isdir(output_dir), f'not a directory {output_dir}'
    filename = filename_sep.join([filename_prefix, datetime.strftime(timestamp, timestamp_fmt)])
    filename = f'{filename}.{filename_ending}'
    return path.join(output_dir, filename)
    

def concat_files(output_filepath : str, files : list):
    with open(output_filepath, 'a') as output_filehandle:
        header_written = False
        for file in files:
            with open(file, 'r') as input_filehandle:
                header = input_filehandle.readline()
                if not header_written:
                    output_filehandle.write(header)
                    header_written = True
                for line in input_filehandle:
                    output_filehandle.write(line)


def extract_timestamp(filename : str, filename_sep : str = '_', timestamp_pos : int = -1, timestamp_fmt : str = '%Y-%m-%dT%H:%M:%S%z') -> datetime:

    """
    extract_timestamp(filename : str, filename_sep = '_', timestamp_pos : int = -1 timestamp_fmt : str = '%Y-%m-%dT%T%z'):

    filename      path to a file containing a valid timestamp in the file name
    filename_sep  separator to separate metainformation in the filename. 
                  Example: msb-0008-a_imu_2022-01-01T12:12:12+00:00.log 
                  Here, the filename_sep is '_'
    timestamp_pos absolute position of the timestamp in the file name. Defaults to -1, 
                  referring to the last element in the file name
    timestamp_fmt Format of the time stamp in the file name

    
    If the timestamp is extracted successfully, returns a tz-aware datetime object
    If the timestamp cannot be extracted, return None

    """
    # timetamp_str = separate '/' & separate file ending & split by filename_sep and keep the timestamp_pos'th field
    timestamp_str = filename.split(path.sep)[-1]
    timestamp_str = timestamp_str.split('.')[0]
    timestamp_str = timestamp_str.split(filename_sep)[timestamp_pos]
    try:
        timestamp = datetime.strptime(timestamp_str, timestamp_fmt)
    except Exception as e:
        print(f'failed to convert to timestamp: {timestamp_str} -> {e}')
        return None
    return timestamp


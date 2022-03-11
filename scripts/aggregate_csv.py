import argparse
from collections import defaultdict
from datetime import (datetime, timezone)
from os import path
import sys

sys.path.insert(0, path.abspath(path.join(path.dirname(__file__), '../src')))

from SAAFOWE.io.timefiles import find_time_files, calc_time_intervals


def parse_cmdline() -> dict:
    cmd_parser = argparse.ArgumentParser()
    cmd_parser.add_argument('--verbose', action="store_true")
    cmd_parser.add_argument('-t', '--interval', type=str, default='hourly', help='aggregation interval. Valid descriptors are: hourly, daily or monthly') 
    cmd_parser.add_argument('input', nargs='+', default=(None if sys.stdin.isatty() else sys.stdin))

    return cmd_parser.parse_args().__dict__

def get_output_filename():
    pass

def concat_files():
    pass

def extract_timestamp(filename : str, filename_sep = '_', timestamp_pos : int = -1, timestamp_fmt : str = '%Y-%m-%dT%H:%M:%S%z') -> datetime:

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

def main():
    # parse command line arguments
    args = parse_cmdline()
    input_files = dict()
    aggregated_files = defaultdict(list)
    
    if args['verbose']:
        print(f'config: {args}')
        print(f'sys.path: {sys.path}')

    if type(args['input']) == type(list()):
        if args['verbose']: print("using input files provided via command line")
        for f in args['input']:
            if not path.isfile(f):
                if args['verbose']: print(f'not a regular file: {f} skipping')
                continue
            ts = extract_timestamp(f)
            if ts:
                if args['verbose']: print(f'found valid input file: {f}')
                input_files[ts] = f
    elif type(args['input']) == type(sys.stdin):
        if args['verbose']: print("using input files provided via stdin")
        for line in args['input']:
            if path.isfile(f := line.rstrip()):
                ts = extract_timestamp(f)
                if ts:
                    if args['verbose']: print(f'found valid input file: {f}')
                    input_files[ts] = f

    begin = sorted(input_files.keys())[0]
    end = sorted(input_files.keys())[-1]
    intervals = calc_time_intervals(begin=begin, end=end, interval=args['interval'])

    for lower, upper in zip(intervals[:-1], intervals[1:]):
        if args['verbose']: print(f'processing {lower} -> {upper}')
        for timestamp, f in input_files.items():
            if lower < timestamp <= upper:
                aggregated_files[upper].append(f)

    if args['verbose']:
        for interval, files in aggregated_files.items():
            print(f'{interval}')
            for f in files:
                print(f'    {f}')

    # 6. iterate over the intervals, read in files, sanitize files and write them out

if __name__ == "__main__":
    main()



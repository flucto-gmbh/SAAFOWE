import argparse
from collections import defaultdict
from datetime import (datetime, timezone)
from os import path
import sys

sys.path.insert(0, path.abspath(path.join(path.dirname(__file__), '../src')))

from SAAFOWE.io.timefiles import find_time_files, calc_time_intervals

AGGREGATE_INTERVALS = ["hourly", "daily", "monthly"]

def parse_cmdline() -> dict:
    cmd_parser = argparse.ArgumentParser()
    cmd_parser.add_argument('--verbose', action="store_true")
    cmd_parser.add_argument('-t', '--interval', type=str, default='hourly', help='aggregation interval. Valid descriptors are: hourly, daily or monthly') 
    cmd_parser.add_argument('input', nargs='+', default=(None if sys.stdin.isatty() else sys.stdin))
    cmd_parser.add_argument('-o', '--output', default=path.curdir, type=str, help='output directory')
    cmd_parser.add_argument('-p', '--output-prefix', default='aggregated', type=str, help='prefix to be prepended to the output file')

    return cmd_parser.parse_args().__dict__

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
    

def concat_files():
    pass

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

def main():
    # parse command line arguments
    input_files = dict()
    aggregated_files = defaultdict(list)
    args = parse_cmdline()
    assert args['interval'] in AGGREGATE_INTERVALS, f'not a valid interval: {args["interval"]}'

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

    for interval, files in aggregated_files.items():
        filename_prefix = get_filename_prefix(files[0], args['output_prefix'])
        filename_ending = get_filename_ending(files[0])
        output_filepath = get_output_filepath(output_dir = args['output'], filename_prefix = filename_prefix, timestamp = interval, filename_ending = filename_ending)
        if args['verbose']: print(f'setting output file to {output_filepath}')
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

if __name__ == "__main__":
    main()



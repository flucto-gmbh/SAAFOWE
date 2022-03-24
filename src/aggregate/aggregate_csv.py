#!/bin/env python3

import argparse
from collections import defaultdict
from datetime import (datetime, timezone)
from os import path
import sys

sys.path.insert(0, path.abspath(path.join(path.dirname(__file__), '../src')))

from SAAFOWE.io.timefiles import * 

AGGREGATE_INTERVALS = ["hourly", "daily", "weekly", "monthly", "all"]

def parse_cmdline() -> dict:
    cmd_parser = argparse.ArgumentParser()
    cmd_parser.add_argument('input', nargs='+', default=(None if sys.stdin.isatty() else sys.stdin))
    cmd_parser.add_argument('-o', '--output', default=path.curdir, type=str, help='output directory')
    cmd_parser.add_argument('-p', '--output-prefix', default='aggregated', type=str, help='prefix to be prepended to the output file')
    cmd_parser.add_argument('-t', '--interval', type=str, default='hourly', help='aggregation interval. Valid descriptors are: hourly, daily or monthly') 
    cmd_parser.add_argument('--verbose', action="store_true")

    return cmd_parser.parse_args().__dict__

def main():
    # parse command line arguments
    input_files = dict()
    aggregated_files = defaultdict(list)
    args = parse_cmdline()
    assert args['interval'] in AGGREGATE_INTERVALS, f'not a valid interval: {args["interval"]}'

    if args['verbose']:
        print(f'config: {args}')
        print(f'sys.path: {sys.path}')

    # there are two different ways of how the user can supply input files to the script:
    # - via stdin (e.g. if piping from another program)
    # - via command line parameters
    # all non-specific command line parameters are captured by argparse in the 'input' field
    # hence, checking the type of the input field will reveal where the input files are coming from
    # 
    # if the input field is of type list(), iterate over the list, check if the elements are 
    # valid files, and if so: extract the time stamp from the file name, and store the file
    # path in a dictionary, where the timestamp is the key to the filepath.
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
    # if the input field is of type sys.stdin (_io.TextIOWrapper), 
    # threat the input field like a file and iterate over each line
    elif type(args['input']) == type(sys.stdin):
        if args['verbose']: print("using input files provided via stdin")
        for line in args['input']:
            if path.isfile(f := line.rstrip()):
                ts = extract_timestamp(f)
                if ts:
                    if args['verbose']: print(f'found valid input file: {f}')
                    input_files[ts] = f

    # now, get the first and the last time stamp which is needed to calculate the range
    # of the time interval over which the data in the files is to be aggregated.
    begin = sorted(input_files.keys())[0]
    end = sorted(input_files.keys())[-1]
    # calculate intervals the actual intervals
    intervals = calc_time_intervals(begin=begin, end=end, interval=args['interval'])

    # iterate over time intervals and files and sort the files into the corresonding intervals
    for lower, upper in zip(intervals[:-1], intervals[1:]):
        if args['verbose']: print(f'processing {lower} -> {upper}')
        for timestamp, f in input_files.items():
            if lower <= timestamp <= upper:
                aggregated_files[upper].append(f)
            else:
                if args['verbose']: print(f'skipping timestamp {timestamp} from file {f}')

    if args['verbose']:
        for interval, files in aggregated_files.items():
            print(f'{interval}')
            for f in files:
                print(f'    {f}')

    for interval, files in aggregated_files.items():
        # use the first file in the file list to extract file prefix (everything except the timestamp)
        # and the file ending. 
        filename_prefix = get_filename_prefix(files[0], args['output_prefix'])
        filename_ending = get_filename_ending(files[0])
        # build the output file name and path
        output_filepath = get_output_filepath(output_dir = args['output'], filename_prefix = filename_prefix, timestamp = interval, filename_ending = filename_ending)
        if args['verbose']: print(f'setting output file to {output_filepath}')
        # concatenate all files from one interval into a single file
        concat_files(output_filepath = output_filepath, files = files)

if __name__ == "__main__":
    main()



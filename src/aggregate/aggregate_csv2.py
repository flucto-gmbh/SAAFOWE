#!/bin/env python3

import argparse
from datetime import (date, datetime, timezone)
import os
import sys

from csv_io import gen_input_files

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
    args = parse_cmdline()
    assert args['interval'] in AGGREGATE_INTERVALS, f'not a valid interval: {args["interval"]}'
    if args['verbose']:
        print(f'config: {args}')
        print(f'sys.path: {sys.path}')


    # comparison 




if __name__ == "__main__":
    main()



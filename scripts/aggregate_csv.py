import argparse
from code import interact
from datetime import (datetime, timezone)
from os import path
import sys
import time
from pexpect import ExceptionPexpect

sys.path.insert(0, path.abspath(path.join(path.dirname(__file__), '../src')))

from SAAFOWE.io.timefiles import find_time_files, calc_time_intervals


def parse_cmdline() -> dict:
    cmd_parser = argparse.ArgumentParser()
    cmd_parser.add_argument('--verbose', action="store_true")
    # parser.add_argument('-i', '--input-file', type=argparse.FileType('r'), default=(None if sys.stdin.isatty() else sys.stdin))
    # add interval
    # add stdin 

    return cmd_parser.parse_args().__dict__


def main():
    config = parse_cmdline()
    
    if config['verbose']:
        print(f'config: {config}')
        print(f'sys.path: {sys.path}')

    # 1. get files either from user or from stdin
    # 2. create dict with files, where the key is the timestamp
    # 3. get beginning and end from timestamps
    # 4. calculate the intervals
    # 5. iterate over files and sort them into a new defaultdict corresponding to each interval
    # 6. iterate over the intervals, read in files, sanitize files and write them out

if __name__ == "__main__":
    main()



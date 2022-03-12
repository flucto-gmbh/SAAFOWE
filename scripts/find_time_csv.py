import argparse
from datetime import (datetime, timezone)
from os import path
import sys
import time

sys.path.insert(0, path.abspath(path.join(path.dirname(__file__), '../src')))

from SAAFOWE.io.timefiles import find_time_files


def parse_cmdline() -> dict:
    cmd_parser = argparse.ArgumentParser()
    cmd_parser.add_argument('--begin', type=str)
    cmd_parser.add_argument('--end', type=str)
    cmd_parser.add_argument('--dir', default='.', type=str)
    cmd_parser.add_argument('--file-pattern', default='*.csv', type=str)
    cmd_parser.add_argument('--verbose', action="store_true")
    cmd_parser.add_argument('--print0', action='store_true')
    cmd_parser.add_argument('--print', action='store_true')

    return cmd_parser.parse_args().__dict__


def main():
    config = parse_cmdline()
    
    if config['verbose']:
        print(f'config: {config}')
        print(f'sys.path: {sys.path}')
    try:
        # first generate a naive time object
        begin = datetime.fromisoformat(config['begin'])
        # and now add the timezone
        begin = begin.replace(tzinfo=timezone.utc)
    except Exception as e:
        print(f'failed to parse begin time stamp: {config["begin"]}: {e}')
        sys.exit()
    if not config['end']:
        if config['verbose']: print(f'setting end to NOW')
        end = datetime.fromtimestamp(time.time(), timezone.utc)
    else:
        try:
            end = datetime.fromisoformat(config['end'])
            end = end.replace(tzinfo=timezone.utc)
        except Exception as e:
            print(f'failed to parse end time stamp: {config["end"]}: {e}')
            sys.exit()
    data_dir = path.abspath(config['dir'])
    if config['verbose']:
        print(f'looking for files in {data_dir} from {begin} to {end}')

    data_files = find_time_files(file_dir=data_dir, file_pattern=config['file_pattern'], begin=begin, end=end)

    # print(data_files)
    if config['print0']: 
        print(' '.join(data_files))
    elif config['print']:
        for d_file in data_files:
            print(d_file)

if __name__ == "__main__":
    main()



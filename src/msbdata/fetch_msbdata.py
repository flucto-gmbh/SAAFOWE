#!/usr/bin/env python3

import argparse
from config import REMOTE_SERVER, MSB_LIST, MSB_LOCAL_DATA_DIR
from datetime import datetime, timezone
# import fabric
import os
import sys
import time

from msbdata import fetch_remote_datafile_paths, extract_timestamp_fpath
from msbhosts import assemble_hosts
from msbtimes import parse_begin_end
from scp import copy_remote_datafile

# TODO
# - add --ip option to retrieve directly via a user provided ip address


def parse_validate_cmdline() -> dict:
    cmd_parser = argparse.ArgumentParser()
    cmd_parser.add_argument(
        "--msb",
        nargs="+",
        default=None,
        help="motion sensor box serial numbers from which data is to be fetched",
    )
    cmd_parser.add_argument(
        "-o", "--output-dir", required=True, type=str, help="output directory"
    )
    cmd_parser.add_argument("--verbose", action="store_true")
    cmd_parser.add_argument(
        "-r",
        "--remote",
        help="fetch data via reverse ssh tunnels on a remote server",
        action="store_true",
        default=False,
    )
    cmd_parser.add_argument(
        "--datetime-format",
        type=str,
        default="%Y-%m-%dT%H-%M-%S",
        help="date time format of timestamps in data files"
    )
    cmd_parser.add_argument(
        "--list-available-data",
        action="store_true",
        default=False,
        help="if set, the list of available data per motion sensor box is printed",
    )
    cmd_parser.add_argument(
        "--begin",
        default=None,
        type=str,
        help='use to select files based on a time stamp. Default is 1970-01-01T00:00:00',
    )
    cmd_parser.add_argument(
        "--end",
        default=None,
        type=str,
        help='use to select files based on a time stamp',
    )
    args = cmd_parser.parse_args().__dict__
    assert os.path.isdir(args["output_dir"]), f'not a directory: {args["output"]}'
    assert args["msb"], print(
        "please provide at least one motion sensor box serial number via\
the --msb command line parameter"
        )
    return args

def fetch_msbdata(config : dict):
    if config["verbose"]:
        print(config)

    (begin, end) = parse_begin_end(config)
    if config['verbose']:
        print(f"begin: {begin} -> end: {end}")

    for serialnumber, ssh_access_string in assemble_hosts(
        config["msb"], remote=config["remote"], verbose=config["verbose"]
    ):
        print(serialnumber, ssh_access_string)
        for remote_datafile_path in fetch_remote_datafile_paths(
            serialnumber, ssh_access_string, verbose=config["verbose"]
        ):
            if remote_datafile_ts := extract_datetime_fpath(remote_datafile_path, datetime_fmt=config['datetime_format']):
                if config['verbose']:
                    print(f'extracted timestamp: {remote_datafile_ts}')
                if begin <= remote_datafile_ts <= end:
                    if config['list_available_data']:
                        print(remote_datafile_path)
                    copy_remote_datafile(remote_datafile_path, serialnumber, config, verbose=True)

if __name__ == "__main__":
    config = parse_validate_cmdline()
    fetch_msbdata(config)

#!/usr/bin/env python3

import argparse
import json
import os
import sys

from config import MSB_LIST
from msbhosts import assemble_hosts

def parse_validate_cmdline() -> dict:
    cmd_parser = argparse.ArgumentParser()
    cmd_parser.add_argument("--verbose", action="store_true")
    cmd_parser.add_argument(
        "-r",
        "--remote",
        help="fetch data via reverse ssh tunnels on a remote server",
        action="store_true",
        default=False,
    )
    args = cmd_parser.parse_args().__dict__
    return args

def find_msb(config : dict):
    if config['verbose']:
        print(json.dumps(config))
    config['msb'] = MSB_LIST
    for host, access in assemble_hosts(config['msb'], remote=config['remote'], verbose=config['verbose']):
        print(host, access)

if __name__ == "__main__":
    config = parse_validate_cmdline()
    find_msb(config)

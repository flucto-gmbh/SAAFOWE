#!/usr/bin/env python3

# TODO
# - implement --ip flag to print local ip
# - implement --network-ssid to print local network ssid
# - implement --msb to find a specific motion sensor box
# - implement --location to get gps location

import argparse
import json
import os
import sys

from config import MSB_LIST, CMD_GPSD_LAT_LON
from msbhosts import assemble_hosts
from ssh import ssh_exec

def parse_validate_cmdline() -> dict:
    cmd_parser = argparse.ArgumentParser()
    cmd_parser.add_argument("--verbose", action="store_true")
    cmd_parser.add_argument(
        "--ip",
        action="store_true",
        help="print local ip address of remote motion sensor box",
        default=False,
    )
    cmd_parser.add_argument(
        "--network-ssid",
        action="store_true",
        help="print network ssid the motion sensor box is connected to",
        default=False,
    )
    cmd_parser.add_argument(
        "--gps",
        action="store_true",
        help="print gps coordinates of motion sensor box",
        default=False,
    )
    cmd_parser.add_argument(
        "--maps",
        action="store_true",
        help="print google maps link to display current location of motion sensor box",
        default=False,
    )
    cmd_parser.add_argument(
        "-r",
        "--remote",
        help="fetch data via reverse ssh tunnels on a remote server",
        action="store_true",
        default=False,
    )
    args = cmd_parser.parse_args().__dict__
    return args


def find_msb(config: dict):
    if config["verbose"]:
        print(json.dumps(config))
    config["msb"] = MSB_LIST
    for host, access in assemble_hosts(
        config["msb"], remote=config["remote"], verbose=config["verbose"]
    ):
        print(host, access, end="")
        if config['gps']:
            if ssh_response := ssh_exec(access, cmd=CMD_GPSD_LAT_LON):
                lat, lon = ssh_response.replace('\n', '').split(',')
                if config['maps']:
                    print(f" https://www.google.com/maps/search/?api=1&query={lat},{lon}", end="")
                else:
                    print(f" latitude: {lat} longitude: {lon}", end="")
            else:
                print("print failed to retrieve gps latitude and longitude")
        print("")

if __name__ == "__main__":
    config = parse_validate_cmdline()
    find_msb(config)

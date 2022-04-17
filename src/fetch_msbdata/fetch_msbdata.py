import argparse
from config import REMOTE_SERVER, MSB_LIST
import fabric
import os
import sys

from msbhostnames import assemble_hosts_ip, assemble_hosts_msb, assemble_hosts_remote


def parse_validate_cmdline() -> dict:
    cmd_parser = argparse.ArgumentParser()
    cmd_parser.add_argument(
        "--ip",
        nargs="+",
        default=None,
        help="ip addresses of motion sensor boxes to fetch data from",
    )
    cmd_parser.add_argument(
        "--msb",
        nargs="+",
        default=None,
        help="motion sensor box serial numbers from which data is to be fetched",
    )
    cmd_parser.add_argument(
        "-o", "--output-dir", required=True, type=str, help="output directory"
    )
    cmd_parser.add_argument(
        "-p",
        "--output-prefix",
        default="aggregated",
        type=str,
        help="prefix to be prepended to the output file",
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
        "--list-available-msb",
        action="store_true",
        default=False,
        help="if set, the list of available motion sensor boxes is printed",
    )
    cmd_parser.add_argument(
        "--list-available-data",
        action="store_true",
        default=False,
        help="if set, the list of available data per motion sensor box is printed",
    )
    args = cmd_parser.parse_args().__dict__
    assert os.path.isdir(args["output_dir"]), f'not a directory: {args["output"]}'
    if not args["ip"] and not args["msb"]:
        print(
            "please provide either a set of motion sensor box serial numbers\
via the --msb command line paramter or a range of ip\
addresses via the --ip command line parameter"
        )
        sys.exit()
    if args["remote"] and not args["msb"]:
        print(
            "please provide at least on motion sensor box serial number via\
the --msb command line paramter when using the --remote option"
        )
    return args


def fetch_msbdata():
    config = parse_validate_cmdline()
    hosts = list()
    if config["remote"]:
        hosts = assemble_hosts_remote(config["msb"])
    else:
        if config["msb"]:
            hosts = assemble_hosts_msb(config["msb"])
        if config["ip"]:
            hosts = assemble_hosts_ip(config["ip"])

    for host in hosts:
        pass


if __name__ == "__main__":
    fetch_msbdata()

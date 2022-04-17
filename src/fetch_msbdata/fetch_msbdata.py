import argparse
from config import REMOTE_SERVER, MSB_LIST
import fabric
import os
import sys

from msbdata import fetch_datafile_paths
from msbhosts import assemble_hosts


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
        "--list-available-data",
        action="store_true",
        default=False,
        help="if set, the list of available data per motion sensor box is printed",
    )
    cmd_parser.add_argument(
        "--begin",
        default=
        type=str,
        help='use to select files based on a time stamp',
    )
    cmd_parser.add_argument(
        "--end",
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


def fetch_msbdata():
    config = parse_validate_cmdline()
    if config["verbose"]:
        print(config)

    for serialnumber, ssh_access_string in assemble_hosts(
        config["msb"], remote=config["remote"], verbose=config["verbose"]
    ):
        for i, data_fpath in enumerate(fetch_datafile_paths(
            serialnumber, ssh_access_string, verbose=config["verbose"]
        )):
            if config['list_available_data']:
                print(i, data_fpath)


if __name__ == "__main__":
    fetch_msbdata()

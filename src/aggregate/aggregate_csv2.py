#!/bin/env python3
import argparse
from datetime import date, datetime, timezone, timedelta
import os
import sys

from csv_io import gen_input_files, extract_timestamps_fnames, validate_fpaths, concat_files
from partition_timestamps import are_in_equivalent_interval, AGGREGATION_INTERVALS


def parse_cmdline() -> dict:
    cmd_parser = argparse.ArgumentParser()
    cmd_parser.add_argument(
        "input", nargs="+", default=(None if sys.stdin.isatty() else sys.stdin)
    )
    cmd_parser.add_argument(
        "-o", "--output", default=None, type=str, help="output directory"
    )
    cmd_parser.add_argument(
        "-p",
        "--output-prefix",
        default="aggregated",
        type=str,
        help="prefix to be prepended to the output file",
    )
    cmd_parser.add_argument(
        "-t",
        "--interval",
        type=str,
        default="hourly",
        help="aggregation interval. Valid descriptors are: hourly, daily or monthly",
    )
    cmd_parser.add_argument("--verbose", action="store_true")

    return cmd_parser.parse_args().__dict__


def partition_files(timestamp_filepath_iterator: iter, args: dict):
    intervals = list()
    for timestamp, fpath in timestamp_filepath_iterator:
        if args["verbose"]:
            print(f"{timestamp} : {fpath}")
        current_interval = [(timestamp, fpath)]
        while True:
            try:
                timestamp, fpath = next(timestamp_filepath_iterator)
            except:
                intervals.append(current_interval)
                break
            if args["verbose"]:
                print(f"{timestamp} : {fpath}")
            if are_in_equivalent_interval(
                timestamp=timestamp,
                interval_boundary=current_interval[0][0],
                interval=args["interval"],
            ):
                current_interval.append((timestamp, fpath))
            else:
                intervals.append(current_interval)
                break
    return intervals


def make_output_path(
    output_dir,
    output_fname_preprefix,
    input_path_example,
    timestamp,
    filename_sep="_",
    timestamp_fmt="%Y-%m-%dT%H:%M:%S%z",
):
    """
    I have no idea if this implementation is correct. But at least it is
    compact and more or less readable. The original implementation was spread
    over multiple functions, with different names for similar things, and
    identical names for different things, and just plain wrong names, and lines
    with a million characters, and ... The Horror.
    """
    input_fname_without_timestamp = "_".join(
        input_path_example.split(os.path.sep)[-1].split(filename_sep)[:-1]
    )
    output_fname_prefix = f"{output_fname_preprefix}_{input_fname_without_timestamp}"
    output_fname_without_extension = filename_sep.join(
        [output_fname_prefix, datetime.strftime(timestamp, timestamp_fmt)]
    )
    extension = input_path_example.split(".")[-1]
    output_path = os.path.join(
        output_dir, f"{output_fname_without_extension}.{extension}"
    )
    return output_path


def main():
    args = parse_cmdline()
    assert (
        args["interval"] in AGGREGATION_INTERVALS
    ), f'not a valid interval: {args["interval"]}'
    if args["verbose"]:
        print(f"config: {args}")
        print(f"sys.path: {sys.path}")

    intervals = partition_files(
        extract_timestamps_fnames(validate_fpaths(gen_input_files(args))), args=args
    )

    for interval in intervals:
        if args["verbose"]:
            print(f"start: {interval[0][0]} -> end: {interval[-1][0]}")
        for _, fpath in interval:
            if args["verbose"]:
                print(f"    filepath: {fpath}")
        output_path = make_output_path(
            output_dir=args["output"],
            output_fname_preprefix="aggregated",
            input_path_example=interval[0][1],
            timestamp=interval[-1][0],
        )
        if args["verbose"]:
            print(f"ouput: {output_path}")

        concat_files(output_path, interval)


if __name__ == "__main__":
    main()

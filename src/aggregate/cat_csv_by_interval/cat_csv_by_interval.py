#!/usr/bin/env python3

import argparse
from datetime import date, datetime
from functools import partial
from itertools import chain
import os
import sys

from partition import partition

INTERVALS = ["hourly", "daily", "weekly", "monthly"]


def get_args() -> dict:
    cmd_parser = argparse.ArgumentParser()
    cmd_parser.add_argument(
        "input", nargs="+", default=(None if sys.stdin.isatty() else sys.stdin)
    )
    cmd_parser.add_argument(
        "-o", "--output", default=os.path.curdir, type=str, help="Output directory"
    )
    cmd_parser.add_argument(
        "-p",
        "--output-prefix",
        default="aggregated",
        type=str,
        help="Prefix to be prepended to the output filename",
    )
    cmd_parser.add_argument(
        "-t",
        "--interval",
        type=str,
        default="hourly",
        help=f'Aggregation interval. Valid are: {", ".join(INTERVALS)}',
    )
    cmd_parser.add_argument("--verbose", action="store_true")
    args = cmd_parser.parse_args().__dict__
    assert args["interval"] in INTERVALS, f'Not a valid interval: {args["interval"]}'
    assert type(args["input"]) in [
        type(list()),
        type(sys.stdin),
    ], f'Not a valid input type: {type(args["input"])}'
    assert os.path.isdir(args["output"]), f'Not a directory: {args["output"]}'
    return args


def gen_input_items(args):
    """
    Generate items from command line arguments args. Items are either given
    as a list of command line parameters, or as lines from stdin. This function
    provides a unified interface to both variants.

    NOTE: In the list case, the list is sorted here, as a convenience for
    consumers downstream. In the stdin case, sorting is not possible here in
    general, because the item stream might be infinite. Therefore, the stream
    coming from stdin must already be sorted.
    """
    assert "input" in args
    if type(args["input"]) == type(list()):
        items = sorted(args["input"])
        if args["verbose"]:
            print("Using input files provided via command line")
    elif type(args["input"]) == type(sys.stdin):
        items = (line.rstrip() for line in args["input"])
        if args["verbose"]:
            print("Using input files provided via stdin")
    else:
        raise ValueError(f'Not a valid input type: {type(args["input"])}')
    for item in items:
        yield item


def extract_timestamp(
    path: str,
    path_sep: str = "_",
    timestamp_pos: int = -1,
    timestamp_fmt: str = "%Y-%m-%dT%H:%M:%S%z",
) -> datetime:
    """
    Return a tz-aware datetime object extracted from the path.

    path            file path containing a valid timestamp in the file name
    path_sep        separator to separate metainformation in the path
                    Example: msb-0008-a_imu_2022-01-01T12:12:12+00:00.log
                    Here, path_sep is '_'
    timestamp_pos   absolute position of the timestamp in the file name after
                    some split. Default: -1, i.e. the last element.
    timestamp_fmt   Format of the timestamp in the file name
    """
    timestamp_str = path.split(path.sep)[-1]
    timestamp_str = timestamp_str.split(".")[0]
    timestamp_str = timestamp_str.split(path_sep)[timestamp_pos]
    try:
        timestamp = datetime.strptime(timestamp_str, timestamp_fmt)
    except Exception as e:
        print(f"Failed to convert to timestamp: {timestamp_str} -> {e}")
        raise
    else:
        return timestamp


def filter_filepaths(items, verbose=True):
    for item in items:
        if os.path.isfile(item):
            yield item
        else:
            if verbose:
                print(f"Not a filepath: {item}. Skipping.")


def gen_filepaths_with_timestamps(paths, verbose=True):
    for path in paths:
        try:
            timestamp = extract_timestamp(path)
        except:
            continue
        else:
            if verbose:
                print(f"Found valid input file: {path}")
            yield (timestamp, path)


def are_equivalent_filepaths_with_timestamps(x: tuple, y: tuple, interval: str) -> bool:
    """
    receives two tuples objects x and y and checks if they are datetime
    in their first field are equivalent
    """
    assert interval in INTERVALS
    tx, _ = x
    ty, _ = y
    if interval == "hourly":
        return (
            tx.year == ty.year
            and tx.month == ty.month
            and tx.day == ty.day
            and tx.hour == ty.hour
        )
    elif interval == "daily":
        return tx.year == ty.year and tx.month == ty.month and tx.day == ty.day
    elif interval == "weekly":
        dx = date(tx.year, tx.month, tx.day)
        dy = date(ty.year, ty.month, ty.day)
        return (
            tx.year == ty.year
            and tx.month == ty.month
            and dx.isocalendar().week == dy.isocalendar().week
        )
    elif interval == "monthly":
        return tx.year == ty.year and tx.month == ty.month


def partition_filepaths_with_timestamps(paths_with_ts: iter, interval: str):
    assert interval in INTERVALS
    # creates a new object eq that behaves like the functions
    # are_equivalent_filepaths_with_timestamps with the interval as given
    eq = partial(are_equivalent_filepaths_with_timestamps, interval=interval)
    for gen in partition(paths_with_ts, eq):
        paths = (path for _, path in gen)
        yield paths


def concat_csvs(paths):
    """
    Generate the lines of the CSV files referenced by paths. It is assumed that
    all CSV files have the same header line. The function asserts that this is
    true. The header is yielded once at the beginning of the output stream.
    """
    try:
        path = next(paths)
    except StopIteration:
        raise
    with open(path) as f:
        try:
            header = next(f)
        except StopIteration:
            raise TypeError(f"CSV file is empty, but we need a header: {path}")
        else:
            yield header
            for line in f:
                yield line
    for path in paths:
        with open(path) as f:
            try:
                other_header = next(f)
            except StopIteration:
                continue
            else:
                assert (
                    other_header == header
                ), f"CSV headers don't match: {header} != {other_header}"
                for line in f:
                    yield line

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
    args = get_args()
    input_path_partitions = partition_filepaths_with_timestamps(
        gen_filepaths_with_timestamps(filter_filepaths(gen_input_items(args))),
        args["interval"],
    )
    for input_paths in input_path_partitions:
        input_path_example = next(input_paths)
        output_path = make_output_path(
            args["output"],
            args["output_prefix"],
            input_path_example,
            extract_timestamp(input_path_example),
        )
        assert not os.path.exists(output_path), f"Exists already: {output_path}"
        if args["verbose"]:
            print(f"setting output file to {output_path}")
        input_lines = concat_csv(chain(iter([input_path_example]), input_paths))
        with open(output_path, "w") as f:
            for line in input_lines:
                f.write(line)

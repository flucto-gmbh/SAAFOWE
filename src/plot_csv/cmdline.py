import argparse
import sys
import os

from plot_config import AVAILABLE_PLOT_CONFIGURATIONS


def define_cmdline_args() -> argparse.ArgumentParser:
    """
    define_cmdline_args -> argparse.ArgumentParser object

    Instantiates an ArgumentParser object and adds valid command line arguments to it.

        Returns:
            argparse.ArgumentParser object
    """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="keeps matplotlib figures open for interactive use",
    )
    arg_parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        default=None,
        help="If provided, figure will be saved to this directory. Default is None",
    )
    arg_parser.add_argument(
        "input", nargs="+", default=(None if sys.stdin.isatty() else sys.stdin)
    )

    arg_parser.add_argument("--verbose", action="store_true", help="debug flag")

    return arg_parser


def parse_cmdline_args(arg_parser: argparse.ArgumentParser) -> dict:
    """
    parse_cmdline_args(arg_parser  : argparse.ArgumentParser) -> dict:

    Parses command line arguments provided by the user using the given argparse.ArgumentParser object

        Parameters:
            arg_parser : argparse.ArgumentParser object

        Returns:
            dictionary containing all valid command line arguments
    """
    try:
        args = arg_parser.parse_args().__dict__
    except Exception as e:
        print(f"failed to parse command line arguments: {e}")
        sys.exit()

    assert type(args["input"]) in [
        type(list()),
        type(sys.stdin),
    ], f'Not a valid input type: {type(args["input"])}'
    if args['output_dir']:
        assert os.path.isdir(args["output_dir"]), f'Not a directory: {args["output_dir"]}'

    return args

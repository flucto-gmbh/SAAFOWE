#!/bin/env python
import argparse
import matplotlib.pyplot as plt
import os
import sys
import tilemapbase

# insert current directory into PYTHONPATH to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from csv_io import gen_input_files, read_csv_files
from plot_config import FIGURE_CONFIGURATION, gps_position, gps_altitude
from plot import plot_timeseries, plot_gps_track, plot_gps_track_empty, plot_gps_track_tilemapbase

# TODO
# - implement different map backends:
#   - ipyleaflet: https://ipyleaflet.readthedocs.io/en/latest/api_reference/map.html -> export to html and open browser
#   - folium: http://python-visualization.github.io/folium/quickstart.html -> export to html and open in browser

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
    if args["output_dir"]:
        assert os.path.isdir(
            args["output_dir"]
        ), f'Not a directory: {args["output_dir"]}'

    return args


if __name__ == "__main__":
    tilemapbase.start_logging()

    args = parse_cmdline_args(define_cmdline_args())
    if args["verbose"]:
        print(f"command line parameters: {args}")
    data = read_csv_files(gen_input_files(args), verbose=args["verbose"])
    data = data[data.lat != 0]
    data = data[data.lon != 0]
    data = data.drop_duplicates(subset=['lat', 'lon'], keep = 'last')
    if args["verbose"]:
        print(f"{data.info()}")
    figures = dict()

    if data.empty:
        figures['gps_tracks'] = plot_gps_track_empty(figure_configuration = FIGURE_CONFIGURATION)
    else:
        # figures['gps_tracks'] = plot_gps_track(data, plot_metadata = gps_position)
        figures['gps_tracks'] = plot_gps_track_tilemapbase(data, plot_metadata = gps_position)

    if not data.empty:
        figures['altitude'] = plot_timeseries(data, plot_metadata = gps_altitude)

    if args["interactive"]:
        plt.show()
    if args["output_dir"]:
        for name, fig in figures.items():
            if args["verbose"]:
                print(f"saving figure {name}")
            fig.savefig(
                os.path.join(args["output_dir"], f"{name}.png"),
                dpi=FIGURE_CONFIGURATION["dpi"],
            )

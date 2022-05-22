#!/bin/env python

import argparse
import matplotlib.pyplot as plt
import os
import sys

# insert current directory into PYTHONPATH to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from csv_io import gen_input_files, read_csv_files_imu
from plot_config import FIGURE_CONFIGURATION, IMU_SENSORS
from plot import plot_timeseries, plot_psd_imu, plot_spectrum_imu


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
    arg_parser.add_argument(
        "--psd",
        action="store_true",
        help="calculate and plot power spectral density for the given data",
        default=False,
    )
    arg_parser.add_argument(
        "--spectrum",
        action="store_true",
        help="calculate and plot the magnitude spectrum for the given data",
        default=False,
    )
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
    args = parse_cmdline_args(define_cmdline_args())
    if args["verbose"]:
        print(f"command line parameters: {args}")
    data = read_csv_files_imu(gen_input_files(args), verbose=args["verbose"])
    if args["verbose"]:
        print(f"{data.info()}")
    figures = dict()
    for sensor_name, sensor_plot_metadata in IMU_SENSORS.items():
        if args["verbose"]:
            print(f"processing {sensor_name}")
        figures[sensor_name] = plot_timeseries(
            data,
            plot_metadata=sensor_plot_metadata,
            figure_configuration=FIGURE_CONFIGURATION,
        )
        if args["psd"]:
            figures[f"{sensor_name}_psd"] = plot_psd_imu(
                data,
                plot_metadata=sensor_plot_metadata,
                figure_configuration=FIGURE_CONFIGURATION,
            )
        if args['spectrum']:
            figures[f'{sensor_name}_spectrum'] = plot_spectrum_imu(
                data,
                plot_metadata=sensor_plot_metadata,
                figure_configuration=FIGURE_CONFIGURATION,
            )
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

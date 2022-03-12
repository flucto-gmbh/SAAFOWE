import argparse
from curses import meta
import matplotlib.pyplot as plt
from os import path
import pandas as pd
import sys

sys.path.insert(0, path.abspath(path.join(path.dirname(__file__), '../src')))

from SAAFOWE.io.args import parse_input
from SAAFOWE.io.csv import read_csv_files
from SAAFOWE.plots.timeseries import plot_timeseries
from SAAFOWE.config import IMU_SENSORS, PLOT_PARAMETERS


def parse_args() -> dict:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-i', '--interactive', action='store_true', help="Keeps matplotlib plot figures open for interactive use")
    arg_parser.add_argument('-o', '--output-dir', type=str, default=None, help='Output directory for plots. Default is the current directory')
    arg_parser.add_argument('input', nargs='+', default=(None if sys.stdin.isatty() else sys.stdin))
    arg_parser.add_argument('--verbose', action='store_true', help='debug flag')
    return arg_parser.parse_args().__dict__
   
    
def main():

    args = parse_args()
    input_files = parse_input(args)
    data = read_csv_files(input_files=input_files)

    acceleration_figure = plot_timeseries(data, metadata=IMU_SENSORS['acceleration'], plot_config=PLOT_PARAMETERS)
    rotation_figure = plot_timeseries(data, metadata=IMU_SENSORS['rotation'], plot_config=PLOT_PARAMETERS)
    magfield_figure = plot_timeseries(data, metadata=IMU_SENSORS['magfield'], plot_config=PLOT_PARAMETERS)
    
    if args['output_dir']:
        acceleration_figure.savefig(path.join(args['output_dir'], IMU_SENSORS['acceleration']['figure_filename']), dpi=PLOT_PARAMETERS['dpi'])
        rotation_figure.savefig(path.join(args['output_dir'], IMU_SENSORS['rotation']['figure_filename']), dpi=PLOT_PARAMETERS['dpi'])
        magfield_figure.savefig(path.join(args['output_dir'], IMU_SENSORS['magfield']['figure_filename']), dpi=PLOT_PARAMETERS['dpi'])

    if args['interactive']:
        plt.show()

if __name__ == "__main__":
    main()
    
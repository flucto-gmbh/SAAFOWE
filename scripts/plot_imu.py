import argparse
from curses import meta
import matplotlib.pyplot as plt
from os import path
import pandas as pd
import sys

sys.path.insert(0, path.abspath(path.join(path.dirname(__file__), '../src')))

from SAAFOWE.io.args import parse_input
from SAAFOWE.io.csv import read_csv_files
from SAAFOWE.config import IMU_PARAMETERS, PLOT_PARAMETERS


def parse_args() -> dict:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-i', '--interactive', action='store_true', help="Keeps matplotlib plot figures open for interactive use")
    arg_parser.add_argument('-o', '--output-dir', type=str, default=None, help='Output directory for plots. Default is the current directory')
    arg_parser.add_argument('input', nargs='+', default=(None if sys.stdin.isatty() else sys.stdin))
    arg_parser.add_argument('--verbose', action='store_true', help='debug flag')
    return arg_parser.parse_args().__dict__

def plot_data(data : pd.DataFrame, metadata : dict, plot_config : dict):
    fig = plt.figure(figsize=plot_config['figsize'])
    for k, l in zip(metadata['column_names'], metadata['labels']):
        plt.plot(data[k], label=l)
    if 'ylabel' in metadata:
        plt.ylabel(metadata['ylabel'])
    plt.xlabel('date / time')
    if 'ylim' in metadata:
        plt.ylim(metadata['ylim'])
    if 'title' in metadata:
        plt.title(metadata['title'])
    return fig
    
    
def main():

    args = parse_args()
    input_files = parse_input(args)
    data = read_csv_files(input_files=input_files)

    acceleration_figure = plot_data(data, metadata=IMU_PARAMETERS['acceleration'], plot_config=PLOT_PARAMETERS)
    rotation_figure = plot_data(data, metadata=IMU_PARAMETERS['rotation'], plot_config=PLOT_PARAMETERS)
    magfield_figure = plot_data(data, metadata=IMU_PARAMETERS['magfield'], plot_config=PLOT_PARAMETERS)
    
    if args['output_dir']:
        acceleration_figure.savefig(path.join(args['output_dir'], IMU_PARAMETERS['acceleration']['fig_name']), dpi=PLOT_PARAMETERS['dpi'])
        rotation_figure.savefig(path.join(args['output_dir'], IMU_PARAMETERS['rotation']['fig_name']), dpi=PLOT_PARAMETERS['dpi'])
        magfield_figure.savefig(path.join(args['output_dir'], IMU_PARAMETERS['magfield']['fig_name']), dpi=PLOT_PARAMETERS['dpi'])

    if args['interactive']:
        plt.show()
    # save figs here

if __name__ == "__main__":
    main()
    
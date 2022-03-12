import argparse
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

def plot_imu_component(data : pd.DataFrame, component_parameters : dict, plot_config : dict):
    plt.figure(figsize=plot_config['figsize'])
    for k, l in zip(component_parameters['column_names'], component_parameters['labels']):
        plt.plot(data[k], label=l)
    plt.ylabel(component_parameters['ylabel'])
    plt.xlabel('date / time')
    
def main():

    args = parse_args()
    input_files = parse_input(args)
    data = read_csv_files(input_files=input_files)

    plot_imu_component(data, component_parameters=IMU_PARAMETERS['acceleration'], plot_config=PLOT_PARAMETERS)
    plot_imu_component(data, component_parameters=IMU_PARAMETERS['rotation'], plot_config=PLOT_PARAMETERS)
    plot_imu_component(data, component_parameters=IMU_PARAMETERS['magfield'], plot_config=PLOT_PARAMETERS)
    
    if args['output_dir']:
        for p in IMU_PARAMETERS.keys():
            plt.savefig(path.join(args['output_dir'], IMU_PARAMETERS[p]['fig_name']), dpi=PLOT_PARAMETERS['dpi'])

    if args['interactive']:
        plt.show()
    # save figs here

if __name__ == "__main__":
    main()
    
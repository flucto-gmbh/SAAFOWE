#!/bin/env python

import argparse
import matplotlib.pyplot as plt
import os
import sys

# insert current directory into PYTHONPATH to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from cmdline import define_cmdline_args, parse_cmdline_args
from csv_io import gen_input_files, read_csv_files
from plot_config import FIGURE_CONFIGURATION
from plot import plot_timeseries

if __name__ == "__main__":
    args = parse_cmdline_args(define_cmdline_args())
    if args["verbose"]:
        print(f"command line parameters: {args}")
    data = read_csv_files(gen_input_files(args), verbose=args["verbose"])
    if args['verbose']:
        print(f'{data.info()}')
    figures = dict()
    for column in data.columns:
        if args['verbose']:
            print(f'processing {column}')
        if data[column].dtype == 'object':
            print(f'skipping column {column}: type object')
            continue
        figures[column] = plt.figure(figsize=FIGURE_CONFIGURATION['figsize'])
        plt.plot(data[column], label=column)
        plt.xlabel('date time')
        plt.legend()
    if args['interactive']:
        plt.show()
    if args['output_dir']:
        for name, fig in figures.items():
            if args['verbose']: 
                print(f'saving figure {name}')
            fig.savefig(os.path.join(args['output_dir'], f'{name}.png'), dpi=FIGURE_CONFIGURATION['dpi']) 


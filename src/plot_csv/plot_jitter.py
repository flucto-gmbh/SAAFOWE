#!/bin/env python

import argparse
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np
import os
import sys

# insert current directory into PYTHONPATH to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from cmdline import define_cmdline_args, parse_cmdline_args
from csv_io import gen_input_files, read_csv_files
from plot_config import FIGURE_CONFIGURATION

if __name__ == "__main__":
    args = parse_cmdline_args(define_cmdline_args())
    if args["verbose"]:
        print(f"command line parameters: {args}")
    data = read_csv_files(gen_input_files(args), verbose=args["verbose"])
    if args['verbose']:
        print(f'{data.info()}')
    t = data.index.to_series()
    dt = t.diff().iloc[1:].apply(lambda t: t.total_seconds())
    dt_mean = dt.mean()
    jitter = dt - dt_mean

    figures = dict()
    figures['jitter'] = plt.figure(figsize=FIGURE_CONFIGURATION['figsize'])
    plt.plot(jitter, label='jitter')
    plt.ylabel('seconds')
    plt.title('jitter')
    plt.tight_layout()

    figures['jitter_spectrum'] = plt.figure(figsize=FIGURE_CONFIGURATION['figsize'])
    plt.magnitude_spectrum(jitter, Fs = 1 / dt_mean)
    plt.title('jitter spectrum')
    plt.tight_layout()

    figures['jitter_psd'] = plt.figure(figsize=FIGURE_CONFIGURATION['figsize'])
    plt.psd(jitter, Fs = 1 / dt_mean)
    plt.title('jitter power spectral density')
    plt.tight_layout()

    figures['jitter_dist'] = plt.figure(figsize=FIGURE_CONFIGURATION['figsize'])
    bins = np.arange(-0.2, 0.2, 0.001)
    N, bins, patches = plt.hist(jitter, bins=bins, density=True)
    plt.gca().yaxis.set_major_formatter(PercentFormatter(xmax=N.max()))
    plt.title('jitter distribution')
    plt.tight_layout()

    if args['interactive']:
        plt.show()
    if args['output_dir']:
        for name, fig in figures.items():
            if args['verbose']: 
                print(f'saving figure {name}')
            fig.savefig(os.path.join(args['output_dir'], f'{name}.png'), dpi=FIGURE_CONFIGURATION['dpi']) 


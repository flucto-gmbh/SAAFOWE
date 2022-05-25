import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

from cmdline import parse_cmdline
from bfilter import butter_lowpass_sosfiltfilt
from plot import plot_signal
from rdm import rdm
from testdata import damped_harmonic_signal

# TODO
# - implement low pass filtering

def gen_input_files(args: dict) -> iter:
    """
    gen_input_files(args : dict) -> iter:

    generates a sorted list of input files from either stdin or the command line

        Parameters:
            args: dict containing the command line parameters

        Return:
            iterator over available input files
    """
    assert "input" in args, "no input files"
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


def estimate_damping(args: dict):
    if args['verbose']:
        print('configuration:')
        print(json.dumps(args, indent=4))
    for filepath in gen_input_files(args):
        if args["verbose"]:
            print(f"processing {filepath}")
        data = pd.read_csv(filepath)
        data.epoch = pd.to_datetime(data.epoch, utc=True, unit="s")
        data.set_index("epoch", inplace=True)
        for component in ["x", "y", "z"]:
            component_key = f"{args['acceleration_prefix']}{component}"
            fs = 1/(data.index[1] - data.index[0]).total_seconds()
            if args['verbose']:
                print(f"data has frequency of {fs}")
            timeseries = butter_lowpass_sosfiltfilt(data[component_key].to_numpy(), cutoff = args["filter_cutoff"], fs=fs)
            args['threshold'] = np.std(timeseries) * args['threshold_factor']
            log_dec, zeta, peaks, decay = rdm(
                timeseries=timeseries,
                config=args,
            )
            print(log_dec, zeta)
        if args['absolute_acceleration']:
            acc_abs = np.sqrt(
                np.power(data[f"{args['acceleration_prefix']}x"], 2) 
                + np.power(data[f"{args['acceleration_prefix']}y"], 2)
                + np.power(data[f"{args['acceleration_prefix']}z"], 2)
            )
            args['threshold'] = np.std(acc_abs)
            log_dec, zet, _ = rdm(acc_abs, args)
            print(log_dec, zeta)

if __name__ == "__main__":
    estimate_damping(parse_cmdline())
    plt.show()

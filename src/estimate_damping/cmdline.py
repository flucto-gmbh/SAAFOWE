import argparse
import sys


def parse_cmdline() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input", nargs="*", default=(None if sys.stdin.isatty() else sys.stdin)
    )
    parser.add_argument("--threshold-factor", type=float, default=1.0, help='scaling factor applied to the standard deviation of the signal to determine the threshold used to extract the decay curves.')
    parser.add_argument("--num-samples", type=int, default=1000, help="number of samples used per signal section to calculate the decay curve")
    parser.add_argument("--peak-distance", type=int, default=None, help="minimum number of sample between two consecutive peaks")
    parser.add_argument("--peak-prominence", type=float, default=None, help="minimum peak prominence in the decay curve")
    parser.add_argument("--filter-cutoff", type=float, default=1.0, help="cut off frequency of the low pass filter applied to the data")
    parser.add_argument("--acceleration-prefix", type=str, default='acc_')
    parser.add_argument("--absolute-acceleration", action="store_true")
    parser.add_argument("--plot-decay-curve", action="store_true")
    parser.add_argument("--plot-crossings", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args().__dict__

'''
        config : dict
            dictionary containing all relevant parameters needed to perform the rdm

            threshold : float
                crossing threshold in the signal. Typically, the standard deviation
                or multiples / fraction thereof are used.
            num_samples : int
                number of samples used to calculate the decay curve
            peak_distance: int
                number of elements between peaks in the decay curve
            peak_prominence : float
                the min. prominence of the peaks in the decay curve
'''



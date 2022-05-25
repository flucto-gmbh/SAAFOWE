import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks

from testdata import damped_harmonic_signal
from plot import plot_signal, plot_decay_curve, plot_crossings

def find_crossing(timeseries: np.array, threshold: float):
    for i in range(1, len(timeseries) - 1):
        # if timeseries[i] > threshold and timeseries[i-1] < threshold:
        if timeseries[i] > threshold:
            # upcrossing
            if timeseries[i - 1] <= threshold:
                yield i
                continue
            if timeseries[i + 1] <= threshold:
                yield i
                continue

def calc_decay_curve(
    timeseries: np.array,
    threshold: float,
    n_samples: float,
    min_num_crossings: int = 3,
):
    damping_curve = np.zeros(n_samples)
    len_timeseries = len(timeseries)
    num_crossings = 0
    crossing_indices = list()
    for crossing in find_crossing(timeseries=timeseries, threshold=threshold):
        if crossing + n_samples < len_timeseries:
            crossing_indices.append(crossing)
            damping_curve += timeseries[crossing : crossing + n_samples]
            num_crossings += 1
    if not num_crossings >= min_num_crossings:
        print(f"did not find any values above threshold {threshold}")
        sys.exit
    return ((damping_curve / num_crossings), np.array(crossing_indices))

def find_peaks_decay_curve(
    decay_curve: np.array, peak_distance: int = 150, peak_prominence: float = 0.5
):
    if peak_distance:
        peaks, _ = find_peaks(decay_curve, distance=peak_distance)
    elif peak_prominence:
        peaks, _ = find_peaks(decay_curve, prominence=peak_prominence)
    elif peak_distance and peak_prominence:
        peaks, _ = find_peaks(decay_curve, distance=peak_distance, prominence=peak_prominence)
    else:
        peaks, _ = find_peaks(decay_curve)
    return peaks


def calc_log_dec(decay_curve: np.array, peaks: np.array):
    log_dec_mean = 0
    for i in range(len(peaks)-1):
        log_dec_mean += np.log(decay_curve[peaks[i]] / decay_curve[peaks[i+1]]) 
    log_dec_mean /= len(peaks - 1)
    return log_dec_mean
    # return np.log(decay_curve[peaks[2]] / decay_curve[peaks[3]])


def calc_zeta(log_dec: float) -> float:
    return 1 / np.sqrt(1 + np.power(((2 * np.pi) / log_dec), 2))


def rdm(timeseries: np.array, config: dict):
    """
    rdm(timesries, config)

    Input
        timeseries : np.array
            time series containing the acceleration data. Must be one-dimensional
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

    Output
        zeta : float
            damping ratio
        log_dec : float
            logarithmic decrement
        peaks : np.array
            identified peaks in the decay curve used to calculate log_dec and zeta
        decay_curve : np.array
            the decay curve as calculated from the input time series
    """
    if config['verbose']:
        print(f"time series has {len(timeseries)} elements")
    decay_curve, crossings = calc_decay_curve(
        timeseries=timeseries,
        threshold=config["threshold"],
        n_samples=config["num_samples"],
    )
    if config['plot_crossings']:
        plot_crossings(timeseries, crossings, config['threshold'])
    decay_peaks = find_peaks_decay_curve(
        decay_curve=decay_curve,
        peak_distance=config["peak_distance"],
        peak_prominence=config["peak_prominence"],
    )
    if config['plot_decay_curve']:
        plot_decay_curve(decay_curve, decay_peaks)
    log_dec = calc_log_dec(decay_curve=decay_curve, peaks=decay_peaks)
    zeta = calc_zeta(log_dec=log_dec)
    return (zeta, log_dec, decay_peaks, decay_curve)


if __name__ == "__main__":
    t, y = damped_harmonic_signal()
    c = [c for c in find_crossing(y, threshold=0.66)]
    plot_signal(t, y)
    plt.scatter(
        t[c],
        y[c],
        marker="x",
        color="tab:orange",
    )

    decay_curve = calc_decay_curve(timeseries=y, threshold=0.66, n_samples=3000)
    peaks = find_decay_curve_peaks(decay_curve)
    log_dec = calc_log_dec(decay_curve, peaks)
    zeta = calc_zeta(log_dec)
    print(f"logarithimic decrement: {log_dec}")
    print(f"damping ratio: {zeta}")

    plt.figure()
    plt.plot(t[:3000], decay_curve, label=f"decay curve")
    plt.scatter(t[peaks], decay_curve[peaks], marker="x", color="tab:orange")
    plt.legend()
    plt.tight_layout()
    plt.show()

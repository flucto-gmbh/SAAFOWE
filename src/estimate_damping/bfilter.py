import numpy as np
from scipy.signal import butter, sosfiltfilt

def butter_lowpass_sosfiltfilt(data : np.array, cutoff : float, fs : float, pad='even', padlen=5000, order=3):
    """
    applies a symmetric filter (no phase offset)
    """

    if pad not in ('even', 'odd', 'constant', None):
        raise Exception('please provide a valid padding')

    # check if len(data > padlen)
    if len(data) < padlen:
        print(
            f'padlen exceeds the number of available data points. Setting padlen to {len(data)}')
        padlen = len(data) - 1

    nyq = fs*0.5
    cut = cutoff/nyq

    sos = butter(order, cut, btype='lowpass', output='sos')
    y = sosfiltfilt(sos, data, padtype=pad, padlen=padlen)

    return y



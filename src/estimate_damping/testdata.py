import numpy as np
import pandas as pd

from plot import plot_signal

def decay_curve(t : np.array, y_hat : float = 1.0, zeta : float = 0.025, omega : float = 1.0):
    y = y_hat * np.power(np.e, -zeta*t) * np.sin(omega * t)
    return y

def damped_harmonic_signal(init_length : float = 50.0, repetitions : int = 10, delta_t : float = 0.01):
    final_length = repetitions * init_length
    t = np.arange(0, final_length + delta_t, delta_t)
    y = decay_curve(np.arange(0, init_length + delta_t, delta_t))
    y = np.array([y]*10).flatten()[:1-repetitions]
    return (t, y)

if __name__ == "__main__":
    t, y = damped_harmonic_signal()
    plot_signal(t, y)

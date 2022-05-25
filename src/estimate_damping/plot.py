import matplotlib.pyplot as plt

def plot_signal(t, y, xlabel="time (s)", ylabel="amplitude (m)", figsize=(16,9), new_fig : bool = False, show_plot=True, plot_blocking=False):
    plt.figure(figsize=figsize)
    plt.plot(t, y)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    if show_plot:
        plt.show(block=plot_blocking)

def plot_crossings(timeseries, crossings, threshold, figsize=(16,9), show_plot=True, plot_blocking=False):
    plt.figure(figsize=figsize)
    plt.title("up- and downcrossings")
    plt.plot(timeseries)
    plt.scatter(crossings, timeseries[crossings], marker='x', color='tab:orange')
    plt.axhline(y=threshold, color='tab:red')
    plt.tight_layout()
    if show_plot:
        plt.show(block=plot_blocking)

def plot_decay_curve(decay_curve, peaks, figsize=(16,9), show_plot=True, plot_blocking=False):
    plt.figure(figsize=figsize)
    plt.title("decay curve")
    plt.plot(decay_curve)
    plt.scatter(peaks, decay_curve[peaks], marker='x', color='tab:orange')
    plt.tight_layout()
    if show_plot:
        plt.show(block=plot_blocking)
    

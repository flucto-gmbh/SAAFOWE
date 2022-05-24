import matplotlib.pyplot as plt

def plot_signal(t, y, xlabel="time (s)", ylabel="amplitude (m)", figsize=(16,9), new_fig : bool = False):
    plt.figure(figsize=figsize)
    plt.plot(t, y)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()
    plt.tight_layout()
    

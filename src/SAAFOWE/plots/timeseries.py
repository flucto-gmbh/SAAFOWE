import matplotlib.pyplot as plt
import pandas as pd

def plot_timeseries(data : pd.DataFrame, metadata : dict, plot_config : dict):
    fig = plt.figure(figsize=plot_config['figsize'])
    for k, l in zip(metadata['column_names'], metadata['labels']):
        plt.plot(data[k], label=l)
    if 'ylabel' in metadata:
        plt.ylabel(metadata['ylabel'])
    if 'xlabel' in metadata:
        plt.xlabel(metadata['xlabel'])
    if 'ylim' in metadata:
        plt.ylim(metadata['ylim'])
    if 'title' in metadata:
        plt.title(metadata['title'])
    return fig
 
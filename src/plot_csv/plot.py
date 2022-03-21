import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
import pandas as pd
import tilemapbase


from plot_config import FIGURE_CONFIGURATION, imu_accelerations, imu_rotations, imu_magfield, gps_position, gps_altitude


def plot_timeseries(data: pd.DataFrame, plot_metadata: dict, figure_configuration: dict = FIGURE_CONFIGURATION):
    fig = plt.figure(figsize=figure_configuration["figsize"])
    for k, l in zip(plot_metadata["column_names"], plot_metadata["labels"]):
        plt.plot(data[k], label=l)
    if "ylabel" in plot_metadata:
        plt.ylabel(plot_metadata["ylabel"])
    if "xlabel" in plot_metadata:
        plt.xlabel(plot_metadata["xlabel"])
    if "ylim" in plot_metadata:
        plt.ylim(plot_metadata["ylim"])
    if "title" in plot_metadata:
        plt.title(plot_metadata["title"])
    
    plt.tight_layout()
    return fig

def plot_psd_imu(
    data : pd.DataFrame,
    plot_metadata : dict,
    figure_configuration : dict = FIGURE_CONFIGURATION,
):
    dt = (data.index[1] - data.index[0]).total_seconds()
    fig = plt.figure(figsize=figure_configuration['figsize'])
 
    for k, l in zip(plot_metadata["column_names"], plot_metadata["labels"]):
        plt.psd(
            data[k],
            Fs = 1/dt,
            detrend = 'linear',
            label=l,
        )
    plt.legend()
    plt.tight_layout()
    return fig

def plot_spectrum_imu(
    data : pd.DataFrame,
    plot_metadata : dict,
    figure_configuration : dict = FIGURE_CONFIGURATION,
):
    dt = (data.index[1] - data.index[0]).total_seconds()
    fig = plt.figure(figsize=figure_configuration['figsize'])
 
    for k, l in zip(plot_metadata["column_names"], plot_metadata["labels"]):
        plt.magnitude_spectrum(
            data[k] - data[k].mean(),
            Fs = 1/dt,
            label=l,
        )
    plt.legend()
    plt.tight_layout()
    return fig

def plot_gps_track_empty(figure_configuration : dict = FIGURE_CONFIGURATION):
    fig = plt.figure(figsize=figure_configuration['figsize'])
    plt.text(
        x = 0.5,
        y = 0.5,
        s = "No GPS Track available",
        fontsize=36,
        horizontalalignment='center',
    )
    fig.tight_layout()
    return fig



def plot_gps_track(
    track: pd.DataFrame,
    plot_metadata : dict,
    figure_configuration : dict = FIGURE_CONFIGURATION,
    verbose=False,
):
    # create new figure, axes instances.
    fig = plt.figure(figsize=figure_configuration['figsize'])

    if figure_configuration['transparent']:
        fig.patch.set_alpha(0)

    min_lat = track.lat.min() - plot_metadata['margin']
    max_lat = track.lat.max() + plot_metadata['margin']
    min_lon = track.lon.min() - plot_metadata['margin']
    max_lon = track.lon.max() + plot_metadata['margin']
    if verbose:
        print(
            f"min_lat: {min_lat} min_lon: {min_lon} max_lat: {max_lat} max_lon: {max_lon}"
        )

    m = Basemap(
        llcrnrlon=min_lon,
        llcrnrlat=min_lat,
        urcrnrlon=max_lon,
        urcrnrlat=max_lat,
        resolution="h",
        projection="merc",
        lat_0=(max_lat - min_lat) / 2,
        lon_0=(max_lon - min_lon) / 2,
    )

    m.drawcoastlines()
    m.fillcontinents()
    m.drawcountries()
    m.drawstates()
    m.etopo()
    m.drawmapboundary(fill_color="#46bcec")
    m.fillcontinents(color="white", lake_color="#46bcec")
    # draw parallels
    m.drawparallels(np.arange(-90, 90, 2), labels=[1, 1, 1, 1])
    # draw meridians
    m.drawmeridians(np.arange(-180, 180, 2), labels=[1, 1, 1, 1])

    lons, lats = m(track.lon, track.lat)
    m.scatter(lons, lats, marker="o", color="tab:red", zorder=5, s=5)

    fig.tight_layout()

    return fig

def plot_gps_track_tilemapbase(
    track: pd.DataFrame,
    plot_metadata : dict,
    figure_configuration : dict = FIGURE_CONFIGURATION,
    verbose=False,
):
    # create new figure, axes instances.
    fig, ax = plt.subplots(figsize=figure_configuration['figsize'])

    if figure_configuration['transparent']:
        fig.patch.set_alpha(0)

    min_lat = track.lat.min() - plot_metadata['margin']
    max_lat = track.lat.max() + plot_metadata['margin']
    min_lon = track.lon.min() - plot_metadata['margin']
    max_lon = track.lon.max() + plot_metadata['margin']

    if verbose:
        print(
            f"min_lat: {min_lat} min_lon: {min_lon} max_lat: {max_lat} max_lon: {max_lon}"
        )

    tilemapbase.init(create=True)
    t = tilemapbase.tiles.build_OSM()
    extent = tilemapbase.Extent.from_lonlat(min_lon, max_lon, min_lat, max_lat)
    extent = extent.to_aspect(1.0)

    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    plotter = tilemapbase.Plotter(extent, t, width=600)
    plotter.plot(ax, t)
   
    x = list()
    y = list()
    for i, row in track.iterrows():
        _x, _y = tilemapbase.project(row.lon, row.lat)
        x.append(_x)
        y.append(_y)

    ax.scatter(x,y, marker=".", color="black", linewidth=20)



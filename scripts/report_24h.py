import argparse
from datetime import datetime, timezone, timedelta
from glob import glob
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
from os import environ, path
import os
import pandas as pd
import time

from soupsieve import match


def parse_arguments() -> dict:
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument(
        "--verbose", action="store_true", help="for debugging purposes"
    )

    arg_parser.add_argument(
        "--base-data-dir",
        help="directory to consistently store recorded data. Defaults to $HOME/msb_data",
        default=path.join(os.environ["HOME"], "msb_processed"),
        type=str,
    )

    arg_parser.add_argument(
        "--report-time-window",
        help="duration of report in hours",
        default=24,
        type=int,
    )

    return arg_parser.parse_args().__dict__


def match_time_files(
    data_dir: str,
    data_type: str = "imu",
    begin: datetime = datetime.fromisoformat("1970-01-01T00:00:00+00:00"),
    end: datetime = datetime.fromtimestamp(time.time(), timezone.utc),
    msb_pattern: str = "MSB-????-A",
    file_pattern: str = "*.csv",
    verbose: bool = True,
) -> dict:

    msb_files = dict()

    if verbose:
        print(f"processing all file in available between {begin} - {end}")

    for msb_available in glob(path.join(data_dir, msb_pattern)):

        if verbose:
            print(f"processing {msb_available}")
        msb_name = path.basename(msb_available)
        msb_files[msb_name] = list()

        for msb_file in glob(
            path.join(path.join(msb_available, data_type), file_pattern)
        ):
            timestamp = datetime.fromisoformat(msb_file.split("_")[-1].split(".")[0])

            if verbose:
                print(f"timestamp: {timestamp}")

            if begin <= timestamp <= end:
                if verbose:
                    print(f"matching file: {msb_file}")
                msb_files[msb_name].append(msb_file)
                continue
            if verbose:
                print(f"skipping: {msb_file}")

    return msb_files

def sanitize_data(data : pd.DataFrame):
    data.epoch = pd.to_datetime(data.epoch, unit='s', utc=True)
    data.set_index('epoch', inplace=True)

def read_data(msb_files : dict) -> dict :

    data = dict()

    for msb, files in msb_files.items():
        print(f"processing: {msb}")
        if not files:
            continue
        data[msb] = list()

        for data_file in files:

            print(f"processing: {data_file}")
            data[msb].append(pd.read_csv(data_file))
        
        data[msb] = pd.concat(data[msb]
        )
    
    return data

def set_index(msb_data : dict, verbose=False) -> dict:
    for _, data in msb_data.items():
        data.epoch = pd.to_datetime(data.epoch, unit='s', utc=True)
        data.set_index('epoch', inplace=True)
        if verbose: print(f'{data.info()}')
 
def plot_track(
    track : pd.DataFrame, 
    margin = 2, 
    figsize=(9,9), 
    save_fig = None, 
    verbose = False, 
    transparent = True
):
    # create new figure, axes instances.
    fig = plt.figure(figsize=figsize)

    if transparent:
        fig.patch.set_alpha(0)

    min_lat = track.lat.min() - margin
    max_lat = track.lat.max() + margin
    min_lon = track.lon.min() - margin
    max_lon = track.lon.max() + margin
    if verbose:
        print(f'min_lat: {min_lat} min_lon: {min_lon} max_lat: {max_lat} max_lon: {max_lon}')

    m = Basemap(llcrnrlon=min_lon,
                llcrnrlat=min_lat,
                urcrnrlon=max_lon,
                urcrnrlat=max_lat,
                resolution='h',
                projection='merc',
                lat_0=(max_lat - min_lat)/2,
                lon_0=(max_lon - min_lon)/2,
               )

    m.drawcoastlines()
    m.fillcontinents()
    m.drawcountries()
    m.drawstates()
    m.etopo()
    m.drawmapboundary(fill_color='#46bcec')
    m.fillcontinents(color = 'white',lake_color='#46bcec')
    # draw parallels
    m.drawparallels(np.arange(-90,90,2),labels=[1,1,1,1])
    # draw meridians
    m.drawmeridians(np.arange(-180,180,2),labels=[1,1,1,1])

    lons, lats = m(track.lon, track.lat)
    m.scatter(lons, lats, marker = 'o', color='tab:red', zorder=5, s=5)

    fig.tight_layout()

    if save_fig:
        plt.savefig(save_fig, dpi=300)

    if not save_fig:
        plt.show()

def main():

    config = parse_arguments()

    now = datetime.fromtimestamp(time.time(), timezone.utc)
    begin = now - timedelta(hours=config["report_time_window"])

    msb_imu_files = match_time_files(
        data_dir=config['base_data_dir'], begin=begin, end=now, verbose=True
    )

    msb_gps_files = match_time_files(
        config['base_data_dir'], data_type="gps", begin=begin, end=now, verbose=True,
    )

    msb_imu_data = read_data(msb_imu_files)
    imu_gps_data = read_data(msb_gps_files)

    set_index(msb_imu_data)
    set_index(imu_gps_data)

    # build block maxima
    for msb, data in msb_imu_data.items():

        max_acc_abs = list()
        max_acc_abs_i = list()
       
        data.insert(loc=3, column='acc_abs', value=(
            np.sqrt(
                np.power(data.acc_x, 2) +
                np.power(data.acc_y, 2) +
                np.power(data.acc_z, 2) 
            )
        ))

        for t, d in data.acc_abs.resample("10min"):
            if d.empty:
                continue
            max_acc_abs.append(d.max())
            max_acc_abs_i.append(d.idxmax())

        plt.figure()
        data.acc_abs.plot(label="acc_abs")
        # block_max_acc_abs.scatter(label='10 min maxima')
        plt.scatter(max_acc_abs_i, max_acc_abs, marker="x", color="tab:orange")
        plt.savefig(f"/tmp/{msb}_blockmaxima.png", dpi=150)

    # build gps maps
    for msb, data in imu_gps_data.items():
        plot_track(track=data, save_fig=f'/tmp/{msb}_gps.png') 


if __name__ == "__main__":
    main()

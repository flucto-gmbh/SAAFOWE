import argparse
from datetime import datetime, timezone, timedelta
from glob import glob
from click import DateTime
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
from os import environ, path
import os
import pandas as pd
import time

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

def find_time_files(
    file_dir : str,
    file_pattern : str = "*.csv",
    begin: datetime = datetime.fromisoformat("1970-01-01T00:00:00+00:00"),
    end: datetime = datetime.fromtimestamp(time.time(), timezone.utc),
    verbose=False
) -> list :

    files = list()

    for file in glob(path.join(file_dir, file_pattern)):
        timestamp = datetime.fromisoformat(file.split("_")[-1].split(".")[0])
        if verbose:
            print(f"timestamp: {timestamp}")
        if begin <= timestamp <= end:
            if verbose:
                print(f"matching file: {file}")
            files.append(file)
            continue
        if verbose:
            print(f"skipping: {file}")
    
    return files
    

def sanitize_data(data : pd.DataFrame):
    pass


def read_data(files : list) -> pd.DataFrame:
    data = list()
    for file in files:
        data.append(pd.read_csv(file))
    
    return pd.concat(data)

def set_index(data : pd.DataFrame, verbose : bool = False) -> pd.DataFrame:
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

def get_msb_dataset(
    data_dir : str,
    begin : datetime,
    end : DateTime,
    data_type : str = 'imu',
) -> pd.DataFrame:

    files = find_time_files(
        file_dir=path.join(data_dir, data_type),
        begin=begin,
        end=end,
    )

    if not files:
        return pd.DataFrame()

    data = read_data(files)

    set_index(data)

    sanitize_data(data)

    return data

def calc_abs_acc(data : pd.DataFrame):
    data.insert(loc=3, column='acc_abs', value=(
       np.sqrt(
           np.power(data.acc_x, 2) +
           np.power(data.acc_y, 2) +
           np.power(data.acc_z, 2) 
       )
    ))

def calc_block_maxima(data : pd.DataFrame, resample_interval : str = '10min') -> pd.DataFrame:

    t_i = list() 
    max_acc_abs = list()
    max_acc_abs_i = list()

    for t, d in data.acc_abs.resample(resample_interval):
        if d.empty:
            continue
        max_acc_abs.append(d.max())
        max_acc_abs_i.append(d.idxmax())
        t_i.append(t)

    return pd.DataFrame(
        {
            'max_acc_block_i' : max_acc_abs_i,
            'max_acc_block' : max_acc_abs,
        },
        index = t_i
    )

def plot_block_maxima(data : pd.DataFrame, acc_max_block : pd.DataFrame, save_fig = None, transparent = False):
    plt.figure()
    data.acc_abs.plot(label="acc_abs")
    # block_max_acc_abs.scatter(label='10 min maxima')
    plt.scatter(acc_max_block.max_acc_block_i, acc_max_block.max_acc_block, marker="x", color="tab:orange")
    if save_fig:
        plt.savefig(save_fig, dpi=150)

def main():

    config = parse_arguments()

    now = datetime.fromtimestamp(time.time(), timezone.utc)
    begin = now - timedelta(hours=config["report_time_window"])

    # iterate over available data directories
    for msb in glob(path.join(config['base_data_dir'], 'MSB-????-A')):
    # for msb in glob(path.join('/tmp/test/', 'MSB-????-A')):

        msb_name = path.basename(msb)

        print(f'processing imu {msb}')

        imu_data = get_msb_dataset(data_dir=msb, begin=begin, end=now, data_type="imu")
        if imu_data.empty:
            continue
        calc_abs_acc(imu_data)
        block_maxima_acc = calc_block_maxima(imu_data)
        plot_block_maxima(imu_data, block_maxima_acc, save_fig=f'/tmp/{msb_name}_acc_max_block.png')

    for msb in glob(path.join(config['base_data_dir'], 'MSB-????-A')):
    # for msb in glob(path.join('/tmp/test/', 'MSB-????-A')):

        msb_name = path.basename(msb)

        print(f'processing gps {msb}')

        gps_data = get_msb_dataset(data_dir=msb, begin=begin, end=now, data_type='gps')

        if gps_data.empty:
            continue
              
        # build gps maps
        plot_track(track=gps_data, save_fig=f'/tmp/{msb_name}_gps.png') 


if __name__ == "__main__":
    main()

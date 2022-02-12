import argparse
from datetime import datetime, timezone, timedelta
from glob import glob
from tabnanny import verbose
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
from os import environ, path, makedirs
import sys
import pandas as pd
import time


def parse_arguments() -> dict:
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument(
        "--verbose", action="store_true", help="for debugging purposes"
    )

    arg_parser.add_argument(
        "--data-dir",
        help="directory to consistently store recorded data. Defaults to $HOME/msb_data",
        default=path.join(environ["HOME"], "msb_processed"),
        type=str,
    )

    arg_parser.add_argument(
        "--results-dir",
        help="directory to consistently store recorded data. Defaults to $HOME/msb_data",
        default=path.join(environ["HOME"], path.join("msb_results", "24h-report")),
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
    file_dir: str,
    file_pattern: str = "*.csv",
    begin: datetime = datetime.fromisoformat("1970-01-01T00:00:00+00:00"),
    end: datetime = datetime.fromtimestamp(time.time(), timezone.utc),
    verbose=False,
) -> list:

    files = list()

    for file in sorted(glob(path.join(file_dir, file_pattern))):
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


def sanitize_data(data: pd.DataFrame, verbose: bool = False):

    if data.empty:
        print("empty dataframe, skipping!")
        return pd.DataFrame()

    if verbose:
        print("cleaning NaNs")
    data.fillna(method="ffill", inplace=True)

    if verbose:
        print("dropping duplicate indices")
    data = data.loc[~data.index.duplicated(keep="first")]


def read_data(files: list) -> pd.DataFrame:
    data = list()
    for file in files:

        tmp = pd.read_csv(file)

        try:
            set_index(tmp)
        except Exception as e:
            print(f"failed to set index: {e} skipping")
            continue

        try:
            sanitize_data(tmp)
        except Exception as e:
            print(f"failed to sanitize data: {e} skipping")
            continue

        data.append(tmp)

    return pd.concat(data)


def set_index(data: pd.DataFrame, verbose: bool = False):
    data.epoch = pd.to_datetime(data.epoch, unit="s", utc=True)
    data.set_index("epoch", inplace=True)
    if verbose:
        print(f"{data.info()}")

def plot_empty_track(figsize=(16,9), save_fig=None, verbose=False):
    fig = plt.figure(figsize=figsize)

    plt.text(
        x = 0.5,
        y = 0.5,
        s = "No GPS Track available",
        fontsize=36,
        horizontalalignment='center',
    )

    if save_fig:
        plt.savefig(save_fig, dpi=300)
    else:
        plt.show()



def plot_track(
    track: pd.DataFrame,
    margin=2,
    figsize=(16, 9),
    save_fig=None,
    verbose=False,
    transparent=True,
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

    if save_fig:
        plt.savefig(save_fig, dpi=300)
    else:
        plt.show()


def get_msb_dataset(
    data_dir: str,
    begin: datetime,
    end: datetime,
    data_type: str = "imu",
    verbose=False,
) -> pd.DataFrame:

    files = find_time_files(
        file_dir=path.join(data_dir, data_type),
        begin=begin,
        end=end,
        verbose=verbose,
    )

    if not files:
        if verbose: print('did not find any matching files!')
        return pd.DataFrame()

    if verbose: print(f'found {len(files)} data files')

    data = read_data(files)
    data.sort_index(inplace=True)

    return data


def calc_abs_acc(data: pd.DataFrame, verbose=False):
    if verbose: print('calculating absolute acceleration')

    data.insert(
        loc=3,
        column="acc_abs",
        value=(
            np.sqrt(
                np.power(data.acc_x, 2)
                + np.power(data.acc_y, 2)
                + np.power(data.acc_z, 2)
            )
        ),
    )


def calc_block_maxima(
    data: pd.DataFrame, 
    resample_interval: str = "10min",
    verbose=False,
) -> pd.DataFrame:

    t_i = list()
    max_acc_abs = list()
    max_acc_abs_i = list()
    std_acc_abs = list()

    for t, d in data.acc_abs.resample(resample_interval):
        if d.empty:
            continue
        max_acc_abs.append(d.max())
        max_acc_abs_i.append(d.idxmax())
        std_acc_abs = d.std()
        t_i.append(t)

    if verbose: print(f'calculated block maxima')

    return pd.DataFrame(
        {
            "max_acc_block_i": max_acc_abs_i,
            "max_acc_block": max_acc_abs,
            "std_acc_block": std_acc_abs,
        },
        index=t_i,
    )


def plot_block_maxima(
    data: pd.DataFrame,
    acc_max_block: pd.DataFrame,
    save_fig=None,
    transparent=False,
    figsize=(16, 9),
    verbose=False,
):
    plt.figure(figsize=figsize)
    data.acc_abs.plot(label="acc_abs")
    # block_max_acc_abs.scatter(label='10 min maxima')
    plt.scatter(
        acc_max_block.max_acc_block_i,
        acc_max_block.max_acc_block,
        marker="x",
        color="tab:orange",
    )
    if save_fig:
        plt.savefig(save_fig, dpi=150)


def main():

    config = parse_arguments()

    now = datetime.fromtimestamp(time.time(), timezone.utc)
    now_string = now.strftime('%Y%m%dT%H%M%S%z')
    # now_string = now.__str__().replace(':', '').replace('-','')
    begin = now - timedelta(hours=config["report_time_window"])

    if config["verbose"]:
        print(f"postprocess measurements in interval: {begin} -> {now}")

    if not path.isdir(config["data_dir"]):
        print(f'not a directory: {config["data_dir"]}')
        sys.exit(-1)

    if not path.isdir(config["results_dir"]):
        try:
            makedirs(config["results_dir"], exist_ok=True)
        except Exception as e:
            print(f"failed to create directory: {e}")
            sys.exit(-1)

    # iterate over available data directories
    for msb in glob(path.join(config["data_dir"], "MSB-????-A")):
        # for msb in glob(path.join('/tmp/test/', 'MSB-????-A')):

        msb_name = path.basename(msb)

        if config["verbose"]:
            print(f"processing imu {msb}")

        imu_data = get_msb_dataset(
            data_dir=msb,
            begin=begin,
            end=now,
            data_type="imu",
            verbose=config["verbose"],
        )

        if imu_data.empty:
            if config["verbose"]:
                print(f"did not find any measurements, skipping")
            continue

        if config["verbose"]:
            print(f"{imu_data.info()}")

        calc_abs_acc(imu_data, verbose=config["verbose"])
        block_maxima_acc = calc_block_maxima(imu_data, verbose=config["verbose"])
        plot_block_maxima(
            imu_data,
            block_maxima_acc,
            save_fig=path.join(
                config["results_dir"], f"{msb_name}_acc-max-block_{now_string}.png"
            ),
            verbose=config["verbose"],
        )

    for msb in glob(path.join(config["data_dir"], "MSB-????-A")):
        # for msb in glob(path.join('/tmp/test/', 'MSB-????-A')):

        msb_name = path.basename(msb)

        if config["verbose"]:
            print(f"processing gps {msb}")

        gps_data = get_msb_dataset(data_dir=msb, begin=begin, end=now, data_type="gps")

        # if there is no fix, then lat or lon are 0
        if config["verbose"]:
            print("dropping rows with no ")
        gps_data = gps_data[gps_data.lat != 0]

        if gps_data.empty:
            plot_empty_track(
                save_fig=path.join(config["results_dir"], f"{msb_name}_gps_{now_string}.png")
            )
            continue

        # build gps maps
        plot_track(
            track=gps_data,
            save_fig=path.join(config["results_dir"], f"{msb_name}_gps_{now_string}.png"),
        )


if __name__ == "__main__":
    main()

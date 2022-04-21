from datetime import datetime
import json
import os

from msbtimes import parse_fmt_timestamp_string
from config import MSB_REMOTE_DATA_DIR, MSB_LOCAL_DATA_DIR
from ssh import ssh_exec


def fetch_remote_datafile_paths(
    serialnumber: str, ssh_remote_host: str, verbose: bool = False
) -> list:
    for fpath in (
        ssh_exec(
            ssh_remote_host,
            f'find {MSB_REMOTE_DATA_DIR} -iname "*{serialnumber}*" -type f -print | sort',
            verbose=verbose,
        )
        .rstrip()
        .split("\n")
    ):
        yield fpath

def extract_timestamp_fpath(
    fpath: str,
    timestamp_field=-1,
    field_sep="_",
    timestamp_fmt: str = "%Y%m%dT%H%M%S%z",
) -> datetime:
    timestamp_string = fpath.split(".")[0]
    timestamp_string = timestamp_string.split(field_sep)[timestamp_field]
    if timestamp := parse_fmt_timestamp_string(timestamp_string, timestamp_fmt):
        return timestamp

def extract_timestamp_fpaths(
    fpaths: iter,
    timestamp_field: int = -1,
    field_sep: str = "_",
    timestamp_fmt: str = "%Y-%m-%dT%H:%M:%S%z",
) -> iter:
    """
    Return a tz-aware datetime object extracted from the path.

    fpath            file path containing a valid timestamp in the file name
    fpath_sep        separator to separate metainformation in the path
                    Example: msb-0008-a_imu_2022-01-01T12:12:12+00:00.log
                    Here, path_sep is '_'
    timestamp_field absolute position of the timestamp in the file name after
                    some split. Default: -1, i.e. the last element.
    timestamp_fmt   Format of the timestamp in the file name
    """

    for fpath in fpaths:
        print(fpath)
        yield (
            extract_timestamp_fpath(
                fpath=fpath,
                timestamp_field=timestamp_field,
                field_sep=field_sep,
                timestamp_fmt=timestamp_fmt,
            ),
            fpath,
        )

def read_parse_msblogfile(logfile: str, verbose: bool = False) -> iter:
    with open(logfile, "r") as logfile_fhandle:
        for line in logfile_fhandle:
            try:
                data = json.loads(line.rstrip())
            except Exception as e:
                if verbose:
                    print(f"failed to parse line: {line} {e} skipping")
                continue
            if verbose:
                print(f"{data}")
            yield data

def get_output_filepath(output_dir, logfile_name, output_filename_prefix):
    output_filename = f"{output_filename_prefix}_{logfile_name}.csv"
    output_fulldir = os.path.join(output_dir, output_filename_prefix)
    os.makedirs(output_fulldir, exist_ok=True)
    return os.path.join(output_fulldir, output_filename)

def decompose_logfile_stream(
    data_iter: iter, logfile_name: str, output_dir: str, verbose: bool = False
):
    global imu_filehandle
    imu_filehandle = None
    global gps_filehandle
    gps_filehandle = None
    global att_filehandle
    att_filehandle = None

    def create_append_imu_file(imu_data: list):
        global imu_filehandle
        if not imu_filehandle:
            imu_filehandle = open(
                get_output_filepath(output_dir, logfile_name, "imu"), "w"
            )
        imu_filehandle.writelines(",".join(map(str, imu_data)) + "\n")

    def create_append_att_file(att_data: list):
        global att_filehandle
        if not att_filehandle:
            att_filehandle = open(
                get_output_filepath(output_dir, logfile_name, "att"), "w"
            )
        att_filehandle.writelines(",".join(map(str, att_data)) + "\n")

    def create_append_gps_file(gps_data: list):
        global gps_filehandle
        if not gps_filehandle:
            gps_filehandle = open(
                get_output_filepath(output_dir, logfile_name, "gps"), "w"
            )
        epoch, uptime, data = gps_data
        for param in ["lat", "lon", "alt", "time"]:
            if not param in data:
                data[param] = 0
        gps_filehandle.writelines(
            ",".join(
                map(
                    str,
                    (
                        epoch,
                        uptime,
                        data["time"],
                        data["lat"],
                        data["lon"],
                        data["alt"],
                    ),
                )
            )
            + "\n"
        )

    for data in data_iter:
        if "imu" in data:
            if verbose:
                print(f'imu: {data["imu"]}')
            create_append_imu_file(data["imu"])
        elif "gps" in data:
            if verbose:
                print(f'gps: {data["gps"]}')
            create_append_gps_file(data["gps"])
        elif "att" in data:
            if verbose:
                print(f'att: {data["att"]}')
            create_append_att_file(data["att"])
        else:
            if verbose:
                print(f"unknown topic in data: {data}")

    for fhandle in [imu_filehandle, att_filehandle, gps_filehandle]:
        if fhandle:
            fhandle.close()

def gen_input_files(args : dict) -> iter:
    """
    gen_input_files(args : dict) -> iter:

    generates a sorted list of input files from either stdin or the command line

        Parameters:
            args: iterator over available input files

        Return:
            iterator over available input files
    """
    assert 'input' in args, 'no input files'
    if type(args['input']) == type(list()):
        items = sorted(args['input'])
        if args['verbose']:
            print("Using input files provided via command line")
    elif type(args['input']) == type(sys.stdin):
        items = (line.rstrip() for line in args['input'])
        if args['verbose']:
            print("Using input files provided via stdin")
    else:
        raise ValueError(f'Not a valid input type: {type(args["input"])}')
    for item in items:
        yield item

def validate_fpaths(fpaths : iter) -> iter:
    for fpath in fpaths:
        if os.path.isfile(fpath):
            yield fpath

def concat_files(output_filepath : str, files : list):
    with open(output_filepath, 'a') as output_filehandle:
        header_written = False
        for _, file in files:
            with open(file, 'r') as input_filehandle:
                header = input_filehandle.readline()
                if not header_written:
                    output_filehandle.write(header)
                    header_written = True
                for line in input_filehandle:
                    output_filehandle.write(line)



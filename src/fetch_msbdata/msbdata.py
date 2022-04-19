from datetime import datetime
import json
import os

from msbtimes import parse_fmt_timestamp_string
from config import MSB_REMOTE_DATA_DIR, MSB_LOCAL_DATA_DIR
from ssh import ssh_exec

def fetch_remote_datafile_paths(
    serialnumber: str, ssh_remote_host: str, verbose: bool = False
) -> list:
    for fpath in ssh_exec(
        ssh_remote_host,
        f'find {MSB_REMOTE_DATA_DIR} -iname "*{serialnumber}*" -type f -print | sort',
        verbose=verbose,
    ).rstrip().split("\n"):
        yield fpath

def extract_datetime_fpath(
    fpath : str, 
    datetime_field = 2,
    field_sep = "_", 
    datetime_fmt : str = '%Y-%m-%dT%H-%M-%S'
) -> datetime:
    datetime_string = fpath.split(".")[0].split(field_sep)[datetime_field]
    return parse_fmt_timestamp_string(datetime_string, datetime_fmt)

if __name__ == "__main__":
    timestamp_str = "2022-01-01T12-22-13"
    filename = f"imu_msb-0021-a_{timestamp_str}.csv" 
    print(extract_datetime_fpath(filename))

def read_parse_msbdatafile(logfile : str, verbose : bool = False) -> iter:
    with open(logfile, 'r') as logfile_fhandle:
        for line in logfile_fhandle:
            try:
                data = json.loads(line.rstrip())
            except Exception as e:
                if verbose:
                    print(f'failed to parse line: {line} {e} skipping')
                continue
            if verbose:
                print(f'{data}')
            yield data

def get_output_filepath(output_dir, logfile_name, output_filename_prefix):
    output_filename = f"{output_filename_prefix}_{logfile_name}.csv"
    output_fulldir = os.path.join(output_dir, output_filename_prefix)
    os.makedirs(output_fulldir, exist_ok=True)
    return os.path.join(output_fulldir, output_filename)
    
def decompose_logfile_stream(data_iter : iter, logfile_name : str, output_dir : str, verbose : bool = False):
    global imu_filehandle
    imu_filehandle = None
    global gps_filehandle
    gps_filehandle = None
    global att_filehandle
    att_filehandle = None

    def create_append_imu_file(imu_data : list):
        global imu_filehandle
        if not imu_filehandle:
            imu_filehandle = open(get_output_filepath(output_dir, logfile_name, 'imu'), 'w')
        imu_filehandle.writelines(",".join(map(str, imu_data)) + "\n")

    def create_append_att_file(att_data : list):
        global att_filehandle
        if not att_filehandle:
            att_filehandle = open(get_output_filepath(output_dir, logfile_name, 'att'), 'w')
        att_filehandle.writelines(",".join(map(str, att_data)) + "\n")

    def create_append_gps_file(gps_data : list):
        global gps_filehandle
        if not gps_filehandle:
            gps_filehandle = open(get_output_filepath(output_dir, logfile_name, 'gps'), 'w')
        epoch, uptime, data = gps_data
        for param in ['lat', 'lon', 'alt', 'time']:
            if not param in data:
                data[param] = 0
        gps_filehandle.writelines(",".join(map(str, (epoch, uptime, data['time'], data['lat'], data['lon'], data['alt']))) + "\n")

    for data in data_iter:
        if 'imu' in data:
            if verbose:
                print(f'imu: {data["imu"]}')
            create_append_imu_file(data['imu'])
        elif 'gps' in data:
            if verbose:
                print(f'gps: {data["gps"]}')
            create_append_gps_file(data['gps'])
        elif 'att' in data:
            if verbose:
                print(f'att: {data["att"]}')
            create_append_att_file(data['att'])
        else:
            if verbose:
                print(f'unknown topic in data: {data}')

    for fhandle in [imu_filehandle, att_filehandle, gps_filehandle]:
        if fhandle:
            fhandle.close()



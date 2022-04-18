from datetime import datetime
import os

from msbtimes import parse_fmt_timestamp_string
from config import MSB_REMOTE_DATA_DIR, MSB_LOCAL_DATA_DIR
from ssh import ssh_exec

def fetch_datafile_paths(
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


from datetime import datetime
import os

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

def extract_datetime_fpath(fpath : str) -> datetime.datetime:
    pass




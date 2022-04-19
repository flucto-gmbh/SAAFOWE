import os
import subprocess

from config import SSH_KEYFILE, SSH_USER, REMOTE_SERVER, MSB_LOCAL_DATA_DIR
from msbhosts import serial2port, serial2hostname

def assemble_scp_remote(serialnumber : str, remote_path : str, local_path : str, verbose : bool = False):
    remote_port = serial2port(serialnumber)
    scp_cmd = f'scp -o ConnectTimeout=10 -o BatchMode=yes -i {SSH_KEYFILE} -P {remote_port} {SSH_USER}@{REMOTE_SERVER}:{remote_path} {local_path}'
    if verbose:
        print(f'assembled scp command: {scp_cmd}')
    return scp_cmd

def assemble_scp_local(serialnumber : str, remote_path : str, local_path : str, verbose : bool = False):
    remote_host = serial2hostname(serialnumber)
    scp_cmd = f'scp -o ConnectTimeout=10 -o BatchMode=yes -i {SSH_KEYFILE} {SSH_USER}@{remote_host}:{remote_path} {local_path}'
    if verbose:
        print(f'assembled scp command: {scp_cmd}')
    return scp_cmd

def copy_remote_datafile(remote_datafile_path : str, serialnumber : str, config : dict, test : bool = False, verbose : bool = False):
    local_data_dir = os.path.join(MSB_LOCAL_DATA_DIR, serialnumber)
    if not os.path.isdir(local_data_dir):
        os.makedirs(local_data_dir, exist_ok=True)
    if config['remote']:
        scp_cmd = assemble_scp_remote(serialnumber, remote_datafile_path, local_data_dir)
    else:
        scp_cmd = assemble_scp_local(serialnumber, remote_datafile_path, local_data_dir)
    if verbose:
        print(f"executing {scp_cmd}")
    if test:
        return
    stdout, stderr = subprocess.Popen(
        scp_cmd,
        shell=True,
        #stdout=subprocess.STDOUT,
        #stderr=subprocess.DEVNULL
    ).communicate()

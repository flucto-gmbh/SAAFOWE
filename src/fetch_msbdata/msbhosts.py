from config import SSH_USER, SSH_KEYFILE, REMOTE_SERVER
from ssh import ssh_exec
import subprocess

def serial2hostname(serialnumber : str, tld : str = 'local') -> str:
    return f'{serialnumber}.{tld}'

def hostname2serial(hostname : str) -> str:
    return hostname.split('.')[0]

def serial2port(serialnumber : str, port_offset : int = 65000) -> int:
    return int(serialnumber.split('-')[1]) + port_offset

def get_hostname_getent(remote_host : str, verbose=False):
    output = subprocess.Popen(f'getent hosts {remote_host}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).communicate()[0]
    if output:
        if verbose:
            print(f'getent returned {output}')
        ip, hostname = " ".join(output.decode('utf-8').rstrip().split(' ')).split()
        return hostname.lower()
    else:
        print(f'failed to resolve {remote_host}')
        return None

def get_hostname_ssh(ssh_remote_host : str, verbose : bool = False) -> str:
    if hostname := ssh_exec(ssh_remote_host, cmd = 'hostname', verbose = verbose):
        if verbose:
            print(f'retrieved hostname {hostname.rstrip()}')
        return hostname.rstrip().lower()
    else:
        if verbose: 
            print('failed to get hostname')
        return None

def assemble_hosts_local(serialnumber : str, verbose=False) -> iter:
    remote_host = serial2hostname(serialnumber)
    if verbose:
        print(f'trying host: {remote_host}')
    hostname = get_hostname_getent(remote_host, verbose=verbose)
    if verbose:
        print(f'get_hostname_getent returned {hostname}')
    if hostname.split(".")[0] == serialnumber:
        if verbose:
            print(f'hostname and serialnumber match! {serialnumber} == {hostname}')
        return (serialnumber, f"{SSH_USER}@{remote_host} -i {SSH_KEYFILE}")
    else:
        return None

def assemble_hosts_remote(serialnumber : str, verbose : bool = False) -> iter:
    ssh_remote_host = f'{SSH_USER}@{REMOTE_SERVER} -p {serial2port(serialnumber)} -i {SSH_KEYFILE}'
    if verbose:
        print(f'assembled ssh remote host: {ssh_remote_host}')
    hostname = get_hostname_ssh(ssh_remote_host, verbose = verbose)
    if hostname == serialnumber:
        if verbose:
            print(f'hostname and serialnumber match! {serialnumber} == {hostname}')
        return (hostname, ssh_remote_host)
    else:
        return None

def assemble_hosts(serialnumbers : list, remote : bool = False, verbose : bool = False) -> iter:
    """
    assemble_hosts(serialnumbers : list, remote : bool = False, verbose : bool = False) -> iter

    Parameters:
        serialnumbers (list): A list containing serialnumbers of motion sensor
            from which data is to be retrieved

        remote (bool): flag to be used if data is to be retrieved via reverse
            ssh tunnels

        verbose (bool): flag to display debugging information

    Returns:
        Returns an iterator of tuples containing the serialnumber (str)
        and an ssh access string, that can be used to fetch data or execute
        remote bash commands

    """
    for serialnumber in serialnumbers:
        serialnumber = serialnumber.lower()
        if verbose:
            print(f'processing serialnumber: {serialnumber}')
        if remote:
            if host_access := assemble_hosts_remote(serialnumber, verbose=verbose):
                yield host_access
        else:
            if host_access := assemble_hosts_local(serialnumber, verbose=verbose):
                yield host_access


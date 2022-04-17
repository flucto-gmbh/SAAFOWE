from config import SSH_USER, SSH_KEYFILE, REMOTE_SERVER
from ssh import ssh_exec
import subprocess

def serial2hostname(serialnumber : str, tld : str = 'local') -> str:
    return f'{serialnumber}.{tld}'

def hostname2serial(hostname : str) -> str:
    return hostname.split('.')[0]

def serial2port(serialnumber : str, port_offset : int = 65000) -> int:
    return int(serialnumber.split('-')[1]) + port_offset

def get_hostname_getent(remote_host : str):
    output = subprocess.Popen(f'getent hosts {remote_host}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).communicate()[0]
    if output:
        ip, hostname = output.decode('utf-8').split(' ')
        return (hostname, ip)
    else:
        return None

def get_hostname_ssh(ssh_remote_host : str) -> str:
    if hostname := ssh_exec(ssh_remote_host, cmd = 'hostname'):
        return hostname.rstrip().lower()
    else:
        return None

def assemble_hosts_local(serialnumber : str, verbose=False) -> iter:
    remote_host = serial2hostname(serialnumber)
    if verbose:
        print(f'trying host: {remote_host}')
    hostname = get_hostname_getent(remote_host)
    if hostname == serialnumber:
        if verbose:
            print(f'hostname and serialnumber match! {serialnumber} == {hostname}')
        return (hostname, remote_host)
    else:
        return None

def assemble_hosts_remote(serialnumber : str, verbose=False) -> iter:
    ssh_remote_host = f'{SSH_USER}@{REMOTE_SERVER} -p {serial2port(serialnumber)} -i {SSH_KEYFILE}'
    if verbose:
        print(f'assembled ssh remote host: {ssh_remote_host}')
    hostname = get_hostname_ssh(ssh_remote_host)
    if hostname == serialnumber:
        if verbose:
            print(f'hostname and serialnumber match! {serialnumber} == {hostname}')
        return (hostname, ssh_remote_host)
    else:
        return None

def assemble_hosts_ip():
    pass

def assemble_hosts(config : dict) -> iter:
    for serialnumber in config['msb']:
        if config['verbose']:
            print(f'processing serialnumber: {serialnumber}')
        if config['remote']:
            if host_access := assemble_hosts_remote(serialnumber, verbose=config['verbose']):
                yield host_access
        else:
            if host_access := assemble_hosts_local(serialnumber, verbose=config['verbose']):
                yield host_access


import subprocess
from config import SSH_KEYFILE, SSH_USER


def ssh_exec(ssh_remote_host: str, cmd: str) -> str:
    # return subprocess.Popen(f'ssh {ssh_remote_host} {cmd}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    # stdout=subprocess.DEVNULL,
    # stderr=subprocess.STDOUT
    # this is way more difficult than anticipated: https://docs.python.org/3/library/subprocess.html
    # Popen().communicate() returns a tuple of (stdout, stderr), we only return stdout
    output = subprocess.Popen(
        f"ssh -o ConnectTimeout=5 -o BatchMode=yes {ssh_remote_host} {cmd}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    ).communicate()[0]
    if output:
        return output.decode("utf-8")
    else:
        return None

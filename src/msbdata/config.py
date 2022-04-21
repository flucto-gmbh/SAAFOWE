import os

REMOTE_SERVER = "flucto.tech"
MSB_LIST = [f"msb-{i:04d}-a" for i in range(1, 26)]
MSB_REMOTE_DATA_DIR = "/home/pi/msb_data"
SSH_KEYFILE = f'{os.environ["HOME"]}/.ssh/msb_key'
SSH_USER = 'pi'

if local_data_dir := os.environ['MSB_DATA']:
    MSB_LOCAL_DATA_DIR = local_data_dir
else:
    MSB_LOCAL_DATA_DIR = os.path.join(os.environ['HOME'], 'msb_data')
    if not os.path.isdir(MSB_LOCAL_DATA_DIR):
        os.makedirs(MSB_LOCAL_DATA_DIR, exist_ok=True)


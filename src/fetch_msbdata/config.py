import os

REMOTE_SERVER = "flucto.tech"
MSB_LIST = [f"msb-{i:04d}-a" for i in range(1, 26)]
MSB_REMOTE_DATA_DIR = "/home/pi/msb_data"
SSH_KEYFILE = f'{os.environ["HOME"]}/.ssh/msb_key'
SSH_USER = 'pi'


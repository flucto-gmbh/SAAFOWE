#!/bin/env python
import os
from commandline import parse_cmdline_args, define_cmdline_args

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



def main():
    config = parse_cmdline_args(define_cmdline_args())
    if config['verbose']:
        print(f'{config}')

    for infile_path in validate_fpaths(gen_input_files(config)):
        if config['verbose']:
            print(f'{infile_path}')
        with open(infile_path, 'r') as fhandle:
            next(fhandle)
            for line in fhandle:
                data = list(map(float, line.rstrip().split(',')))
                print(data)
                print(type(data))
                break
            



"""
            # calculate dt
            t_cur = time.time()
            dt = t_cur - t_old           

            data = pickle.loads(
                imu_buffer.pop()
            )

            imu_time = data[0]
            acc = data[2:5]
            gyr = data[5:8]
            mag = data[8:11]

            t_int_cur = imu_time
            dt_int = t_int_cur - t_int_old
            t_int_old = t_int_cur

            if config['print']:
                print(f'time : {imu_time} acc : {acc} gyr : {gyr} mag : {mag}')

            # remove constant offset from gyro data
            # low pass filter gyro data

            # temporally integrate rotation
            pitch += gyr[0]*dt_int
            roll += gyr[1]*dt_int

            # Only use accelerometer when it's steady (magnitude is near 1g)
            force_magnitude = math.sqrt(acc[0]**2 + acc[1]**2 + acc[2]**2)
            if force_magnitude > 0.95 and force_magnitude < 1.05:
                logging.debug(f'correcting angles: {force_magnitude}')
                
                pitch_corr = math.atan2(-1*acc[1], -1*acc[2])*(180/math.pi)
                logging.debug(f'pitch acc: {pitch_corr}')
                pitch = (pitch * 0.9) + (pitch_corr * 0.1)
                
                roll_corr = math.atan2(acc[0], -1*acc[2])*(180/math.pi)
                logging.debug(f'roll acc: {roll_corr}')
                roll = (roll * 0.9) + (roll_corr * 0.1)

            else:
                logging.debug(f'exceeding acceleration magnitude: {force_magnitude}')

            p = (pitch*180/math.pi)
            r = (roll*180/math.pi)
            if config['print']:
                print(f'pitch: {p} roll: {r}')

 
"""

if __name__ == "__main__":
    main()

from datetime import datetime
import os

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

def extract_timestamps_fnames(
    fpaths: iter,
    fpath_sep: str = "_",
    timestamp_pos: int = -1,
    timestamp_fmt: str = "%Y-%m-%dT%H:%M:%S%z",
) -> iter:
    """
    Return a tz-aware datetime object extracted from the path.

    fpath            file path containing a valid timestamp in the file name
    fpath_sep        separator to separate metainformation in the path
                    Example: msb-0008-a_imu_2022-01-01T12:12:12+00:00.log
                    Here, path_sep is '_'
    timestamp_pos   absolute position of the timestamp in the file name after
                    some split. Default: -1, i.e. the last element.
    timestamp_fmt   Format of the timestamp in the file name
    """

    for fpath in fpaths:
        timestamp_str = fpath.split(fpath_sep)[-1]
        timestamp_str = timestamp_str.split(".")[0]
        timestamp_str = timestamp_str.split(fpath_sep)[timestamp_pos]
        try:
            timestamp = datetime.strptime(timestamp_str, timestamp_fmt)
        except Exception as e:
            print(f"Failed to convert to timestamp: {timestamp_str} -> {e}")
            raise
        else:
            yield (timestamp, fpath)

def concat_files(output_filepath : str, files : list):
    with open(output_filepath, 'a') as output_filehandle:
        header_written = False
        for _, file in files:
            with open(file, 'r') as input_filehandle:
                header = input_filehandle.readline()
                if not header_written:
                    output_filehandle.write(header)
                    header_written = True
                for line in input_filehandle:
                    output_filehandle.write(line)



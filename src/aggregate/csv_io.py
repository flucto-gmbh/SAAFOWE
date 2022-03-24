
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

def extract_timestamp_fname(
    path: str,
    path_sep: str = "_",
    timestamp_pos: int = -1,
    timestamp_fmt: str = "%Y-%m-%dT%H:%M:%S%z",
) -> datetime:
    """
    Return a tz-aware datetime object extracted from the path.

    path            file path containing a valid timestamp in the file name
    path_sep        separator to separate metainformation in the path
                    Example: msb-0008-a_imu_2022-01-01T12:12:12+00:00.log
                    Here, path_sep is '_'
    timestamp_pos   absolute position of the timestamp in the file name after
                    some split. Default: -1, i.e. the last element.
    timestamp_fmt   Format of the timestamp in the file name
    """
    timestamp_str = path.split(path.sep)[-1]
    timestamp_str = timestamp_str.split(".")[0]
    timestamp_str = timestamp_str.split(path_sep)[timestamp_pos]
    try:
        timestamp = datetime.strptime(timestamp_str, timestamp_fmt)
    except Exception as e:
        print(f"Failed to convert to timestamp: {timestamp_str} -> {e}")
        raise
    else:
        return timestamp



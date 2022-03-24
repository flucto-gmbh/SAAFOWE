import pandas as pd
import numpy as np

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

def read_csv_files(input_files : iter, verbose : bool = False) -> pd.DataFrame:
    """
    read_csv_files(input_files : iter, verbose=False) -> pd.DataFrame:

        Parameters:
            input_files: iterature over available input files
            verbose: debugging flag, default: False

        Returns:
            Pandas DataFrame containing the sanitized data from the input files
    """

    tmp_dfs = list()
    for f in input_files:
        if verbose: print(f'parsing {f}')
        tmp_df = pd.read_csv(f)
        tmp_df['epoch'] = pd.to_datetime(tmp_df['epoch'], unit='s', utc=True)
        tmp_df.set_index('epoch', inplace=True)
        tmp_dfs.append(tmp_df)
    
    data = pd.concat(tmp_dfs)
    data.sort_index(inplace=True)
    data = data[~data.index.duplicated(keep='last')]

    # optional: check for NaNs
    return data


def read_csv_files_gps(file_paths : iter, verbose : bool = False) -> pd.DataFrame:
    raw_data = read_csv_files(file_paths, verbose=verbose)
    raw_data = raw_data.apply(lambda x: pd.to_numeric(x, errors='coerce'))
    raw_data = raw_data.drop(labels='time', axis=1)
    raw_data = raw_data[(raw_data.lat != 0) & (raw_data.lon != 0)]
    raw_data = raw_data.drop_duplicates(subset=['lat', 'lon'], keep = 'last')
    raw_data = raw_data[~raw_data.lat.isna()]
    raw_data = raw_data[~raw_data.lon.isna()]
    return raw_data

def read_csv_files_imu(file_paths : iter, verbose : bool = False) -> pd.DataFrame:
    raw_data = read_csv_files(file_paths, verbose=verbose)
    raw_data = raw_data.apply(lambda x: pd.to_numeric(x, errors='coerce')).dropna()
    return raw_data

    # gps data contains one column of strings (date time strings).
    # drop this column

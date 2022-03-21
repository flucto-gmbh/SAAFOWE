import pandas as pd

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

def read_csv_files(input_files : iter, verbose=False) -> pd.DataFrame:
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
        tmp_dfs.append(pd.read_csv(f))
        tmp_dfs[-1]['epoch'] = pd.to_datetime(tmp_dfs[-1]['epoch'], unit='s', utc=True)
        tmp_dfs[-1].set_index('epoch', inplace=True)
    
    data = pd.concat(tmp_dfs)
    data.sort_index(inplace=True)

    # optional: check for NaNs
    return data
 


import pandas as pd

def read_csv_files(input_files : dict) -> pd.DataFrame:

    tmp_dfs = list()
    for _, f  in input_files.items() :
        print(f)
        tmp_dfs.append(pd.read_csv(f))
        tmp_dfs[-1]['epoch'] = pd.to_datetime(tmp_dfs[-1]['epoch'], unit='s', utc=True)
        tmp_dfs[-1].set_index('epoch', inplace=True)
    
    data = pd.concat(tmp_dfs)
    data.sort_index(inplace=True)

    # optional: check for NaNs
    return data
    
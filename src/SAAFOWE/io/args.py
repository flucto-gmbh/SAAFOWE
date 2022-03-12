from .timefiles import extract_timestamp
from os import path

def parse_input(args : dict):
    input_files = dict()
    if type(args['input']) == type(list()):
        if args['verbose']: print("using input files provided via command line")
        for f in args['input']:
            if not path.isfile(f):
                if args['verbose']: print(f'not a regular file: {f} skipping')
                continue
            ts = extract_timestamp(f)
            if ts:
                if args['verbose']: print(f'found valid input file: {f}')
                input_files[ts] = f
    # if the input field is of type sys.stdin (_io.TextIOWrapper), 
    # threat the input field like a file and iterate over each line
    elif type(args['input']) == type(sys.stdin):
        if args['verbose']: print("using input files provided via stdin")
        for line in args['input']:
            if path.isfile(f := line.rstrip()):
                ts = extract_timestamp(f)
                if ts:
                    if args['verbose']: print(f'found valid input file: {f}')
                    input_files[ts] = f
    else:
        raise Exception(f'uknown input: {args["input"]}')

    return input_files

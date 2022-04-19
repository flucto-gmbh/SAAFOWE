import argparse
from glob import glob
import json
import os
import sys

from msbdata import read_parse_msblogfile, decompose_logfile_stream, validate_fpaths, gen_input_files

def parse_cmdline() -> dict:
    args = argparse.ArgumentParser()
    args.add_argument("input", nargs="+", default=(None if sys.stdin.isatty() else sys.stdin), help="input files to be processed. can either be stdin or a list of files")
    args.add_argument("--input-filepattern", default="*.log", type=str, help="input dir containing msb logfile")
    args.add_argument("--output-dir", "-o", default="", type=str, help="output file directory")
    args.add_argument("--verbose", "-v", default=False, action="store_true", help="debugging output")
    config = args.parse_args().__dict__
    assert os.path.isdir(config['output_dir']), f"please provide a valid output dir"
    return config


def extract_msbdata(config : dict):
    #for logfile in sorted(glob(os.path.join(config['input_dir'], config['input_filepattern']))):
    for logfile in validate_fpaths(gen_input_files(config)):
        logfile_name = os.path.basename(logfile).split('.')[0]
        if not os.path.isfile(logfile):
            if config['verbose']:
                print(f'not a valid file {logfile}, skipping')
            continue
        decompose_logfile_stream(read_parse_msblogfile(logfile, verbose=config['verbose']), logfile_name, output_dir=config['output_dir'])


if __name__ == "__main__":
    config = parse_cmdline()
    extract_msbdata(config)


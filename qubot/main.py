#!/usr/bin/env python3

import argparse
from sys import path
from os import getcwd
from os.path import join, dirname, abspath
path.append(abspath(join(dirname(__file__), '..')))

from qubot.config.qubot import Qubot
from qubot.utils.io import write_json


def main():
    parser = argparse.ArgumentParser(description='Run Qubot via command-line.',
                                     usage='qubot [-h] config_file [--output_file OUTPUT_FILE]')
    parser.add_argument('config_file', type=str, help='path to the Qubot configuration file')
    parser.add_argument('--output_file', '-o', type=str, dest='output_file', default="qu_stats.qu.json",
                        help='the destination file to output the run stats into', required=False)
    args = parser.parse_args()

    qb = Qubot.from_file(args.config_file)
    qb.run()
    write_json(join(getcwd(), args.output_file), qb.get_stats().to_dict())

if __name__ == "__main__":
    main()

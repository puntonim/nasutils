#! /usr/bin/python
"""
Deduplicate lines in a text file.

Lines' order is preserved. Unique lines are printed in stdout.
A possible use case: deduplicate ~/.bash_history if you do not use HISTCONTROL=erasedups

Usage:
    $ ./dedupe_lines.py myfile.txt
"""
from __future__ import print_function

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import utils


filein = None


def parse_args():
    global filein
    try:
        filein = os.path.abspath(os.path.expanduser(sys.argv[1]))
    except IndexError:
        utils.exit_with_error_msg('Please provide a file as argument')

    # Ensure the file is valid.
    if not os.path.isfile(filein):
        utils.exit_with_error_msg('Please provide a valid file')

    return filein


def dedupe_lines():
    unique_lines = set()
    for line in open(filein, 'r'):
        if line not in unique_lines:
            print(line, end='')
            unique_lines.add(line)


if __name__ == '__main__':
    parse_args()
    dedupe_lines()
    sys.exit(0)

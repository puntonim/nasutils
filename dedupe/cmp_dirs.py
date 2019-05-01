#! /usr/bin/python
"""
Compare 2 dirs that look similar. The comparison is recursive and based on file names and file size.
The comparison does not consider owner, group, permissions, times, checksum of the content.

The 2 dirs can contain many files and subdirs.
The diff files are printed in output.
It is a wrapper around the command:
$ find dir1 dir2 -printf "%P\t%s\n" | sort | uniq -u

Usage:
    $ cmp_dirs.py dir1 dir1
"""
import os
import subprocess
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import utils


FIND_CMD = utils.config.get('main', 'find-cmd')
WC_CMD = utils.config.get('main', 'wc-cmd')
SORT_CMD = utils.config.get('main', 'sort-cmd')
UNIQ_CMD = utils.config.get('main', 'uniq-cmd')


def parse_args():
    try:
        dir1 = os.path.abspath(sys.argv[1])
        dir2 = os.path.abspath(sys.argv[2])
    except IndexError:
        utils.exit_with_error_msg('Please provide two dirs as arguments')

    # Ensure the dirs are valid.
    if not os.path.isdir(dir1) or not os.path.isdir(dir2):
        utils.exit_with_error_msg('Please provide valid dirs')

    return dir1, dir2


def find_diff(dir1, dir2):
    # Eg.: $ gfind dir1 dir2 -printf "%P\t%s\n" | sort | uniq -u
    cmd = '{} "{}" "{}" -printf "%P\\t%s\\n" | {} | {} -u'.format(
        FIND_CMD, dir1, dir2, SORT_CMD, UNIQ_CMD)
    output = subprocess.check_output(cmd, shell=True).rstrip()
    if not output:
        utils.print_msg('No diff\n')
    for line in output.splitlines():
        if line:
            relative_path, size = line.split('\t')
            _print_diff(relative_path, size, dir1, dir2)


def _print_diff(relative_path, size, dir1, dir2):
    if relative_path == '':
        utils.print_msg('The 2 given dirs have diff size: {} bytes'.format(size))
        return

    # Find out if it is missing in dir1 or dir2.
    if os.path.isfile(os.path.join(dir1, relative_path)):
        which_dir = 'dir2'
    else:
        which_dir = 'dir1'
    utils.print_msg('> File: {}\nmissing in {}\n'.format(relative_path, which_dir))


if __name__ == '__main__':
    utils.print_msg('DEDUPE DIRS')
    utils.print_msg('===========')

    dir1, dir2 = parse_args()
    find_diff(dir1, dir2)

    utils.print_msg('No errors - DONE')
    sys.exit(0)

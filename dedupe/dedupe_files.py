#! /usr/bin/python
"""
Search for duplicate files in a root dir. The comparison is based on file name and size. If there is a match, a
checksum of the content is compared.

The root dir can contain many files and subdirs.
The duplicated files are printed in output.
It is a wrapper around the commands:
$ find root -type f ! -path "*@eaDir*" ! -name '.DS_Store' -printf "%f\t%s\n" | sort | uniq -d
$ md5 -q myfile.jpg

Usage:
    $ dedupe_files.py [--write-rm-script] root
Options:
    --write-rm-script   Write a Bash script for the actual deletion of duplicated files

Note: the format for the Bash script created with the option `--write-rm-script` is:
```
#! /bin/bash

# Keep: "/home/me/dupes/dir1/4.jpg"
rm "/home/me/dupes/dir2/4.jpg"
rm "/home/me/dupes/dir3/4.jpg"

# Keep: "/home/me/dupes/dir1/2.jpg"
rm "/home/me/dupes/dir2/2.jpg"
```
"""
import datetime
import os
import subprocess
import sys
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import utils


FIND_CMD = utils.config.get('main', 'find-cmd')
WC_CMD = utils.config.get('main', 'wc-cmd')
SORT_CMD = utils.config.get('main', 'sort-cmd')
UNIQ_CMD = utils.config.get('main', 'uniq-cmd')
CHECKSUM_CMD = utils.config.get('main', 'checksum-cmd')


do_write_rm_script = False


def parse_args():
    if '--write-rm-script' in sys.argv:
        sys.argv.remove('--write-rm-script')
        global do_write_rm_script
        do_write_rm_script = True

    try:
        root = os.path.abspath(sys.argv[1])
    except IndexError:
        utils.exit_with_error_msg('Please provide a dirs as argument')

    # Ensure the dir is valid.
    if not os.path.isdir(root):
        utils.exit_with_error_msg('Please provide a valid dir')

    return root


class Deduper(object):
    def __init__(self, root):
        self.root = root
        self.checksums_dupes_map = defaultdict(list)

    def find_dupes(self):
        # Eg.: $ find root -type f ! -path "*@eaDir*" ! -name ".DS_Store" -printf "%f\t%s\n" | sort | uniq -d
        cmd = '{} "{}" -type f ! -path "*@eaDir*" ! -name ".DS_Store" -printf "%f\\t%s\\n" | {} | {} -d'.format(
            FIND_CMD, self.root, SORT_CMD, UNIQ_CMD)
        output = subprocess.check_output(cmd, shell=True).rstrip()
        if not output:
            utils.print_msg('No dupes\n')
        utils.print_msg('> Found {} files with one ore more potential duplicate (files with the same name and size)'.format(
            output.count('\n')))
        utils.print_msg('\n> Comparing checksums...')
        for line in output.splitlines():
            if line:
                filename, size = line.split('\t')
                paths = self._find_all_duplicates_full_path(filename)
                dupes = self._compare_checksums(paths)
                self._print_dupes(dupes)
        if do_write_rm_script:
            self._write_rm_script()

    def _find_all_duplicates_full_path(self, filename):
        # Eg.: $ find root -type f ! -path "*@eaDir*" ! -name ".DS_Store" -name myfile.jpg
        cmd = '{} "{}" -type f ! -path "*@eaDir*" ! -name ".DS_Store" -name "{}"'.format(
            FIND_CMD, self.root, filename)
        output = subprocess.check_output(cmd, shell=True).rstrip()
        if not output:
            utils.exit_with_error_msg('Couldn\'t find the actual duplicates for: {}'.format(filename))
        paths = []
        for line in output.splitlines():
            paths.append(line.strip())
        return paths

    def _compare_checksums(self, paths):
        checksum_dupes_map = defaultdict(list)
        for path in paths:
            # Eg.: $ md5 -q myfile.jpg
            cmd = '{} "{}"'.format(CHECKSUM_CMD, path)
            output = subprocess.check_output(cmd, shell=True).rstrip()
            if not output:
                utils.exit_with_error_msg('Couldn\'t compute the checksum for: {}'.format(path))
            checksum_dupes_map[output.strip()].append(path)
        self.checksums_dupes_map.update(checksum_dupes_map)
        return checksum_dupes_map

    def _print_dupes(self, checksum_dupes_map):
        for check, paths in checksum_dupes_map.items():
            utils.print_msg('> Checksum {}:\n{}\n'.format(check, '\n'.join(paths)))

    def _write_rm_script(self):
        """
        Format:
        ```
        #! /bin/bash

        # Keep: "/home/me/dupes/dir1/4.jpg"
        rm "/home/me/dupes/dir2/4.jpg"
        rm "/home/me/dupes/dir3/4.jpg"

        # Keep: "/home/me/dupes/dir1/2.jpg"
        rm "/home/me/dupes/dir2/2.jpg"
        ```
        """
        if not self.checksums_dupes_map:
            return
        now = datetime.datetime.now()
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'rm_dupes_{}.sh'.format(now.strftime("%Y-%m-%d-%Hh%Mm")))
        utils.print_msg('> Writing rm script...')
        with open(path, 'w') as fout:
            fout.write('#! /bin/bash\n')
            for check, paths in self.checksums_dupes_map.items():
                to_keep = paths[0]
                del paths[0]
                fout.write('\n# Keep: "{}"\n'.format(to_keep))
                for to_remove in paths:
                    fout.write('rm "{}"\n'.format(to_remove))


if __name__ == '__main__':
    utils.print_msg('DEDUPE FILES')
    utils.print_msg('============')

    root = parse_args()
    deduper = Deduper(root)
    deduper.find_dupes()

    utils.print_msg('\nNo errors - DONE')
    sys.exit(0)

#! /usr/bin/python
"""
Search for duplicate files in a root dir. The comparison is based on file size. If there is a match, their checksum
is compared. With the option `--metadata-checksum-first` a checksum of the metadata is computed and compared first.
This is particularly useful with photos and video from cameras and smartphones.
If the reading of the metadata fails, then a checksum of the content is computed and compared.

The root dir can contain many files and subdirs.
The duplicated files are printed in output.

Usage:
    $ ./dedupe_files.py [--write-rm-script] [--exclude-pathname="*.iso"] [--metadata-checksum-first] root
Options:
    --write-rm-script           Write a Bash script for the actual deletion of duplicated files
    --metadata-checksum-first   Try to read the metadata and compute the checksum on metadata. Particularly efficient
                                with photos and videos from smartphones.
    --exclude-pathname          Exclude files with this name in their path.
                                Eg. to exclude a subdir: -exclude-pathname="*/my subdir/*"
                                Eg. to exclude all *.iso files: -exclude-pathname="*.iso"
                                This option can be used multiple times.
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
CHECKSUMFILE_CMD = utils.config.get('main', 'checksumfile-cmd')
CHECKSUMSTRING_CMD = utils.config.get('main', 'checksumstring-cmd')
TAIL_CMD = utils.config.get('main', 'tail-cmd')
SIPS_CMD = utils.config.get('main', 'sips-cmd')


root = None
extensions = set()
do_write_rm_script = False
exclude_pathnames = []
do_metadata_checksum_first = False


def parse_args():
    # Handle '--write-rm-script' option.
    if '--write-rm-script' in sys.argv:
        sys.argv.remove('--write-rm-script')
        global do_write_rm_script
        do_write_rm_script = True

    # Handle '--metadata-checksum-first' option.
    if '--metadata-checksum-first' in sys.argv:
        sys.argv.remove('--metadata-checksum-first')
        global do_metadata_checksum_first
        do_metadata_checksum_first = True

    # Handle '--exclude-pathname' option. It can be used multiple times.
    idx_to_delete = []
    for i, argv in enumerate(sys.argv):
        if argv.startswith('--exclude-pathname'):
            global exclude_pathnames
            exclude_pathnames.append(argv.split('=')[1])
            idx_to_delete.append(i)
    idx_to_delete.sort()
    idx_to_delete.reverse()
    for idx in idx_to_delete:
        del sys.argv[idx]

    global root
    try:
        root = os.path.abspath(sys.argv[1])
    except IndexError:
        utils.exit_with_error_msg('Please provide a dirs as argument')

    # Ensure the dir is valid.
    if not os.path.isdir(root):
        utils.exit_with_error_msg('Please provide a valid dir')

    return root


def find_dupes():
    sizes_and_paths = _list_all_sizes_and_paths()
    dupes_map = _create_groups_by_size(sizes_and_paths)
    _remove_non_dupes(dupes_map, '\n> Removing files with unique size...')
    _group_by_size_and_checksum(dupes_map)
    _remove_non_dupes(dupes_map, '\n> Removing files with the same size but different checksum...')
    _print_dupes(dupes_map)
    if do_write_rm_script:
        _write_rm_script(dupes_map)


def _list_all_sizes_and_paths():
    exclude_pathnames_option = ''
    for pathname in exclude_pathnames:
        exclude_pathnames_option += '! -path "{}" '.format(pathname)
    utils.print_msg('\n> Building size and path list...')
    # Eg.: $ gfind root -type f ! -path "*@eaDir*" ! -name ".DS_Store" ! -path excludepathname -printf "%s\t%P\n"
    cmd = '{} "{}" -type f ! -path "*@eaDir*" ! -name ".DS_Store" {} -printf "%s\\t%P\\n"'.format(
        FIND_CMD, root, exclude_pathnames_option)
    output = subprocess.check_output(cmd, shell=True).rstrip()
    output = output.decode('utf-8')
    if not output:
        utils.print_msg('No files in root')
    output = output.splitlines()
    utils.print_msg('> Found {} files'.format(len(output)))

    sizes_and_paths = []
    for line in output:
        if not line:
            continue
        size, path = line.split('\t')
        if sys.version_info[0] < 3:  # For Python 2.
            size = size.encode('utf-8')
            path = path.encode('utf-8')
        sizes_and_paths.append((size, path))

    return sizes_and_paths


def _create_groups_by_size(sizes_and_paths):
    utils.print_msg('\n> Grouping all found files by size...')
    dupes_map = defaultdict(list)
    for size, path in sizes_and_paths:
        dupes_map[size].append(path)
    return dupes_map


def _remove_non_dupes(data, msg=None):
    if msg:
        utils.print_msg(msg)
    keys_to_remove = [k for k, v in data.items() if len(v) < 2]
    for key in keys_to_remove:
        del data[key]


def _group_by_size_and_checksum(dupes_map):
    total_num = 0
    for dupes in dupes_map.values():
        total_num += len(dupes)
    i = 1
    for size, dupes in dupes_map.items():
        utils.print_msg('\n> [{}/{}] Comparing checksums for files with the same size:\n{}'.format(i, total_num,'\n'.join(dupes)))
        i += len(dupes)
        actual_dupes = _select_dupes_with_same_checksum(dupes, total_num)
        dupes_map[size] = actual_dupes


def _select_dupes_with_same_checksum(dupes, total_num):
    checksums_map = defaultdict(list)
    for dupe in dupes:
        full_path = os.path.join(root, dupe)
        try:
            hashval = _hash_metadata(full_path)
        except (MetadataReadingError, SkipMetadataReadingOption) as ex:
            if isinstance(ex, MetadataReadingError):
                utils.print_msg('> Metadata reading failed for: {}\nHashing its content instead...'.format(dupe))
            hashval = _hash_content(full_path)
        checksums_map[hashval].append(dupe)
    _remove_non_dupes(checksums_map)
    dupes = checksums_map.values()  # A list of lists.
    if not dupes:
        return []
    if len(dupes) > 1:
        utils.exit_with_error_msg('Found a group of files with the same size and subgroups of checksums, too weird!!')
    return dupes[0]


class MetadataReadingError(Exception):
    pass


class SkipMetadataReadingOption(Exception):
    pass


def _hash_metadata(path):
    if not do_metadata_checksum_first:
        raise SkipMetadataReadingOption
    utils.print_msg('> Reading and hashing metadata for: {}'.format(path))
    # Eg.: $ sips -g all file.jpg | tail -n +2
    cmd = '{} -g all "{}" | {} -n +2'.format(
        SIPS_CMD, path, TAIL_CMD)
    output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).rstrip()
    if 'error' in output.lower():
        raise MetadataReadingError
    # Eg.: $ md5 -q "string"
    cmd = '{} "{}"'.format(CHECKSUMSTRING_CMD, output)
    hashval = subprocess.check_output(cmd, shell=True).rstrip()
    return hashval


def _hash_content(path):
    utils.print_msg('> Hashing content for: {}'.format(path))
    # Eg.: $ md5 -q "file.mov"
    cmd = '{} "{}"'.format(CHECKSUMFILE_CMD, path)
    hashval = subprocess.check_output(cmd, shell=True).rstrip()
    return hashval


def _print_dupes(dupes_map):
    global extensions
    if not dupes_map:
        utils.print_msg('No dupes')
        return
    for size, paths in dupes_map.items():
        utils.print_msg('> Dupes found, size bytes {} and same metadata or content:\n{}\n'.format(size, '\n'.join(paths)))
        for path in paths:
            ext = path[path.rfind('.'):]
            extensions.add(ext)
    utils.print_msg('>>>>> Extensions found in dupes: {}'.format(' '.join(extensions)))


def _write_rm_script(dupes_map):
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
    utils.print_msg('\n> Writing rm script...')
    if not dupes_map:
        utils.print_msg('No dupes')
        return
    now = datetime.datetime.now()
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'rm_dupes_{}.sh'.format(now.strftime("%Y-%m-%d-%Hh%Mm")))
    with open(path, 'w') as fout:
        fout.write('#! /bin/bash\n')
        fout.write('# >>>>> Extensions found in dupes: {}\n'.format(' '.join(extensions)))
        for check, paths in dupes_map.items():
            to_keep = paths[0]
            del paths[0]
            fout.write('\n# Keep: "{}"\n'.format(os.path.join(root, to_keep)))
            for to_remove in paths:
                fout.write('rm "{}"\n'.format(os.path.join(root, to_remove)))


if __name__ == '__main__':
    utils.print_msg('DEDUPE FILES')
    utils.print_msg('============')

    parse_args()
    find_dupes()

    utils.print_msg('\nNo errors - DONE')
    sys.exit(0)

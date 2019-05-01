# Dedupe

Compare and deduplicate files and dirs.

## `cmp_dirs.py`
Compare 2 dirs that look similar. The comparison is recursive and based on file names and file size.
The comparison does not consider owner, group, permissions, times, checksum of the content.

The 2 dirs can contain many files and subdirs.
The diff files are printed in output.

Usage:
```bash
$ cmp_dirs.py dir1 dir1
DEDUPE DIRS
===========
The 2 given dirs have diff size: 2404 bytes
The 2 given dirs have diff size: 2438 bytes
> File: IMG_20140101_234554.jpg
missing in dir2

No errors - DONE
```
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
COMPARE DIRS
============
The 2 given dirs have diff size: 2404 bytes
The 2 given dirs have diff size: 2438 bytes
> File: IMG_20140101_234554.jpg
missing in dir2

No errors - DONE
```

## `dedupe_files.py`
Search for duplicate files in a root dir. The comparison is based on file name and size. If there is a match, a
checksum of the content is compared.

The root dir can contain many files and subdirs.
The duplicated files are printed in output.

Usage:
```bash
$ dedupe_files.py "my dir"
DEDUPE FILES
============
> Checksum f4f4aa1e5c25afe19f79c35cf74ee02e:
/home/my dir/2018.06.29 London/IMGP0010.JPG
/home/my dir/2018.06 Trip to London/IMGP0010.JPG

> Checksum 999a88f1ac7e59da0c0f63fa64bf0cce:
/home/my dir/2018.06.29 London/IMGP0033.JPG
/home/my dir/2018.06 Trip to London/IMGP0033.JPG

No errors - DONE
```
Options:
 - `--write-rm-script` to write a Bash script to perform the actual deletion of duplicated files.
 
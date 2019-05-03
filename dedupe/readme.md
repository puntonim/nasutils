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

## `dedupe_files_by_name.py`
Search for duplicate files in a root dir. The comparison is based on file name and size. If there is a match, a
checksum of the content is compared.

The root dir can contain many files and subdirs.
The duplicated files are printed in output.

Usage:
```bash
$ dedupe_files_by_name.py "my dir"
DEDUPE FILES BY NAME
====================
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
 - `--exclude-pathname` to exclude files with this name in their path.   
    Eg. to exclude a subdir: `-exclude-pathname="*/my subdir/*"`   
    Eg. to exclude all *.iso files: `-exclude-pathname="*.iso"`   
    This option can be used multiple times.


## `dedupe_files.py`
Search for duplicate files in a root dir. The comparison is based on file size. If there is a match, their checksum
is compared. With the option `--metadata-checksum-first` a checksum of the metadata is computed and compared first.
This is particularly useful with photos and video from cameras and smartphones.
If the reading of the metadata fails, then a checksum of the content is computed and compared.

The root dir can contain many files and subdirs.
The duplicated files are printed in output.

Performance are great. Run on a old macbook in a root dir with 25k file, it took:
- 8 mins in a run with ~270 actual dupes
- 1 min in a run with no dupes

Usage:
```bash
$ dedupe_files.py --metadata-checksum-first "my dir"
DEDUPE FILES
============

> Building size and path list...
> Found 24378 files

> Grouping all found files by size...

> Removing files with unique size...
...
> [153/154] Comparing checksums for files with the same size:
2006.11.17-20 London/travel/pag12.jpg
2008.12.31 Valmalenco/IMG_4799.JPG
> Reading and hashing metadata for: 2006.11.17-20 London/travel/pag12.jpg
> Metadata reading failed for: 2006.11.17-20 London/travel/pag12.jpg
Hashing its content instead...
> Hashing content for: 2006.11.17-20 London/travel/pag12.jpg
> Reading and hashing metadata for: 2008.12.31 Valmalenco/IMG_4799.JPG

> Removing files with the same size but different checksum...
No dupes

> Writing rm script...
No dupes

No errors - DONE
```
Options:
 - `--write-rm-script` to write a Bash script to perform the actual deletion of duplicated files.
 - `--metadata-checksum-first` to try to read the metadata and compute the checksum on metadata. Particularly efficient
    with photos and videos from smartphones. 
 - `--exclude-pathname` to exclude files with this name in their path.   
    Eg. to exclude a subdir: `-exclude-pathname="*/my subdir/*"`   
    Eg. to exclude all *.iso files: `-exclude-pathname="*.iso"`   
    This option can be used multiple times.
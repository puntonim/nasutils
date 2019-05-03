"""
rm script format:

```
#! /bin/bash
# >>>>> Extensions found in dupes: .jpg .JPG .mp4

# Keep: "/Volumes/1/IMG_20140819_192125.jpg"
rm "/Volumes/2/2014-08-19 19.21.25.jpg"

# Keep: "/Volumes/1/IMG_20150607_144835.jpg"
rm "/Volumes/2/2015-06-07 14.48.35.jpg"

# Keep: "/Volumes/1/IMG_20150402_092650.jpg"
rm "/Volumes/2/2015-04-02 09.26.50.jpg"

# Keep: "/Volumes/1/IMG_20150714_091512.jpg"
rm "/Volumes/2/2015-07-14 09.15.13.jpg"

# Keep: "/Volumes/1/IMG_20150307_161100.jpg"
rm "/Volumes/2/2015-03-07 16.11.01.jpg"
```
"""
import os
import subprocess
if hasattr(__builtins__, 'raw_input'):
    input = raw_input
import sys


def go():
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'rm_dupes_2019-05-03-14h38m.sh')
    with open(path, 'r') as fin:
        content = fin.read()

    lines = content.split('\n')
    failed = []
    i = 0
    while i < len(lines):

        if lines[i].startswith('# Keep: "/Volumes/'):
            path1 = lines[i][lines[i].find('"/Volumes/'):]
            path2 = lines[i+1][lines[i+1].find('"/Volumes/'):]
            filename1 = lines[i][lines[i].rfind('/'):].lstrip('/')
            filename2 = lines[i+1][lines[i+1].rfind('/'):].lstrip('/')

            try:
                year1, month1, day1, hour1, minute1, second1 = parse1(filename1)
                year2, month2, day2, hour2, minute2, second2 = parse2(filename2)
            except Exception:
                print('{} or {} not in the right format'.format(filename1, filename2))
                failed.append([path1, path2, 'wrong format'])
                i += 1
                continue

            if year1!=year2 or month1!=month2 or day1!=day2 or hour1!=hour2 or minute1!=minute2:
                print('{} != {}'.format(filename1, filename2))
                failed.append([path1, path2])
            else:
                if not abs(second1-second2) < 3:
                    print('{} sec != {} sec'.format(filename1, filename2))
                    failed.append([path1, path2, 'secs'])
                else:
                    print('{} == {}'.format(filename1, filename2))
        i += 1

    handle_failed(failed)


def parse1(name):
    """
    IMG_20150402_093057.jpg
    VID_20150513_181521.mp4
    """
    year = month = day = hour = minute = second = None
    name = name.lstrip('IMG_').lstrip('VID_')
    year = int(name[:4])
    month = int(name[4:6])
    day = int(name[6:8])
    hour = int(name[9:11])
    minute = int(name[11:13])
    second = int(name[13:15])
    return year, month, day, hour, minute, second


def parse2(name):
    """
    2015-04-02 09.30.58.jpg
    2015-05-13 16.06.06.mp4
    """
    year = month = day = hour = minute = second = None
    year = int(name[:4])
    month = int(name[5:7])
    day = int(name[8:10])
    hour = int(name[11:13])
    minute = int(name[14:16])
    second = int(name[17:19])
    return year, month, day, hour, minute, second


def handle_failed(failed):
    print('FAILED: #{}'.format(len(failed)))
    print('FAILED:\n{}'.format('\n'.join(str(x) for x in failed)))

    for failure in failed:
        subprocess.check_call('open {}'.format(failure[0]), shell=True)
        input('Press a key to see its dupe... ')
        subprocess.check_call('open {}'.format(failure[1]), shell=True)

        answer = input('Continue [y/n*]? ')
        if answer != 'y':
            sys.exit(1)


if __name__ == '__main__':
    go()

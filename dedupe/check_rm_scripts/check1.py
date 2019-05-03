"""
rm script format:

```
#! /bin/bash
# >>>>> Extensions found in dupes: .jpg .mp4

# Keep: "/Volumes/beforearuba/IMG_20161126_101632.jpg"
rm "/Volumes/maybedupes/IMG_20161126_101632.jpg"

# Keep: "/Volumes/beforearuba/IMG_20161126_155632.jpg"
rm "/Volumes/maybedupes/IMG_20161126_155632.jpg"

# Keep: "/Volumes/beforearuba/IMG_20161126_155349.jpg"
rm "/Volumes/maybedupes/IMG_20161126_155349.jpg"
```
"""
import os

def go():
    path = os.path.join(os.path.dirnameos.path.dirname((os.path.realpath(__file__))), 'rm_dupes_2019-05-03-13h48m.sh')
    with open(path, 'r') as fin:
        content = fin.read()

    lines = content.split('\n')
    failed = []
    i = 0
    while i < len(lines):

        if lines[i].startswith('# Keep: "/Volumes/'):
            filename1 = lines[i][lines[i].rfind('/'):]
            filename2 = lines[i+1][lines[i+1].rfind('/'):]
            if filename1 == filename2:
                print('{} == {}'.format(filename1, filename2))
            else:
                failed.append([filename1, filename2])
                print('{} != {}'.format(filename1, filename2))

        i += 1

    print('FAILED: #{}'.format(len(failed)))
    print('FAILED:\n{}'.format('\n'.join(str(x) for x in failed)))


if __name__ == '__main__':
    go()

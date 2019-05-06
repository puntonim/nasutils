# nasutils

Set of utils I use for some typical Network Attached Storage operations. Mostly in Python, Bash and Makefile.

## Setup
Create `config.ini` (see `config.ini.template`)


## Utils list
See `readme.md` in each dir.

### 1. [Nimlinks](https://github.com/puntonim/nimlinks)
Set of tools for macOS to create and handle special links to files.
Especially useful when used with file sync apps like Synology Drive or Owncloud/Nextcloud.

### 2. Dedupe files
Compare and deduplicate files and dirs. Particularly efficient with photos.

### 3. Dedupe lines
Deduplicate lines in a text file.

### 4. BakConfigs
Backup for any configuration item in the machine: `~/.ssh/config`, `/etc/hosts`, list of all `brew`-installed
formulae, list of `/Applications`, SublimeText config dir, etc. Highly customizable.

## Development
When writing Python code, especially if you aim at running the code on a NAS, try to:
 - write code compatible with Python 2 and 3
 - do not use any external library, so that no virtualenv is necessary.


## Copyright
Copyright 2019 puntonim (https://github.com/puntonim). No License.

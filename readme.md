# nasutils

Set of utils I use for some typical Network Attached Storage operations. Mostly in Python, Bash and Makefile.

## Setup
Create `config.ini` (see `config.ini.template`)


## Utils list
See `readme.md` in each dir.

### 1. [Nimlinks](https://github.com/puntonim/nimlinks)
Set of tools for macOS to create and handle special links to files.
Especially useful when used with file sync apps like Synology Drive or Owncloud/Nextcloud.
 
### 2. Dedupe
Compare and deduplicate files and dirs. Particularly efficient with photos.


## Development
When writing Python code, try to:
 - write code compatible with Python 2 and 3 so that it works in old and new macOS versions
 - do not use any external library, so that no virtualenv is necessary. This way scripts work in any vanilla macOS.


## Copyright
Copyright 2019 puntonim (https://github.com/puntonim). No License.

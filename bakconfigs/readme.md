# BakConfigs

Backup for any configuration item in the machine: `~/.ssh/config`, `/etc/hosts`, list of all `brew`-installed
formulae, list of `/Applications`, SublimeText config dir, etc. Highly customizable.

## Usage
First create a configuration file in ~/myconfigurations/bakconfigs.ini
```bash
$ ./bakconfigs.py ~/myconfigurations
```

## `bakconfigs.ini` FORMAT:
Each section is an item to be processed.   
Each section can have the following attributes:
- `bakdir`: required. Name of the subdir to be created in the given root and where to store the backup files/dirs.
- `action`: required. Valid values are:
    - `list`: run an `ls` and store the stdout in a text file.
    - `copy`: run a `rsync` (file or dir).
    - `zip`: run a `zip` on the given target (file or dir).
    - `custom command`: run a custom command and store the stdout in a text file.
- `target`: required unless the action is `custom command`. The actual configuration file or dir.
- `cmd`: required only if the action is `custom command`. The actual command to run. Its stdout is stored in a text file.

Example:

```ini
[Applications]
bakdir = Applications
action = list
target = /Applications

[Bash profile]
bakdir = Bash
action = copy
target = ~/.bash_profile

[Bash history]
bakdir = Bash
action = zip
# target can ba a file or dir.
target = ~/.bash_history

[PyCharm 2019-1]
bakdir = PyCharm 2019-1
action = zip
# target can ba a file or dir.
target = ~/Library/Preferences/PyCharm2019.1

[Brew]
bakdir = Brew
action = custom command
# Run the custom command and store the stdout in a text file.
cmd = brew list --full-name --versions
```
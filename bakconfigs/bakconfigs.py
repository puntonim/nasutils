#! /usr/bin/python
"""
Backup for any configuration item in the machine: `~/.ssh/config`, `/etc/hosts`, list of all `brew`-installed
formulae, list of `/Applications`, SublimeText config dir, etc. Highly customizable.

Usage:
    # First create a configuration file in ~/myconfigurations/bakconfigs.ini
    $ ./bakconfigs.py ~/myconfigurations

bakconfigs.ini FORMAT:
Each section is an item to be processed.
Each section can have the following attributes:
    - bakdir: required. Name of the subdir to be created in the given root and where to store the backup files/dirs.
    - action: required. Valid values are: list, copy, zip, custom command
        - list: run an `ls` and store the stdout in a text file.
        - copy: run a `rsync` (file or dir).
        - zip: run a `zip` on the given target (file or dir).
        - custom command: run a custom command and store the stdout in a text file.
    - target: required unless the action is `custom command`. The actual configuration file or dir.
    - cmd: required only if the action is `custom command`. The actual command to run. Its stdout is stored in a text file.
Example:
```
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
"""
import os
import subprocess
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import utils


LS_CMD = utils.config.get('main', 'ls-cmd')
ZIP_CMD = utils.config.get('main', 'zip-cmd')
RSYC_CMD = utils.config.get('main', 'rsync-cmd')


root = None
config = None


class CommandHandler(object):
    def __init__(self, action, bakdir, target=None, custom_cmd=None):
        self.action = action
        self.bakdir = bakdir
        self.target = os.path.expanduser(target.rstrip('/')) if target else None
        self.custom_cmd = custom_cmd
        # File name or dir name.
        self.target_name = self.target[self.target.rfind('/')+1:] if target else None

    def execute(self):
        if not os.path.isdir(self.bakdir):
            os.mkdir(self.bakdir)
        return getattr(self, '_' + self.action.replace(' ', '_'))()

    def _list(self):
        cmd = '{} -alhs "{}" > "{}.txt"'.format(LS_CMD, self.target, os.path.join(self.bakdir, self.target_name))
        subprocess.check_call(cmd, shell=True)

    def _zip(self):
        zip_path = os.path.join(self.bakdir, self.target_name.lstrip('.'))
        cmd = '{} -r "{}.zip" "{}"'.format(ZIP_CMD, zip_path, self.target_name)
        cwd = self.target[:-len(self.target_name)]
        subprocess.check_call(cmd, cwd=cwd, shell=True)

    def _copy(self):
        copy_path = os.path.join(self.bakdir, self.target_name.lstrip('.'))
        if os.path.isdir(self.target):
            self.target += '/'
        cmd = '{} -av --progress --delete "{}" "{}"'.format(RSYC_CMD, self.target, copy_path)
        subprocess.check_call(cmd, shell=True)

    def _custom_command(self):
        cmd = '{} > "{}.txt"'.format(self.custom_cmd, os.path.join(self.bakdir, self.custom_cmd.split(' ')[0]))
        subprocess.check_call(cmd, shell=True)


def parse_args():
    global root
    try:
        root = os.path.abspath(sys.argv[1])
    except IndexError:
        utils.exit_with_error_msg('Please provide a dirs as argument')

    # Ensure the dir is valid.
    if not os.path.isdir(root):
        utils.exit_with_error_msg('Please provide a valid dir')

    return root


def load_config():
    path = os.path.join(root, 'bakconfigs.ini')
    global config
    config = utils.ConfigParserLazy(path, defaults=dict(cmd=None, target=None))


def bak():
    for section in config.sections():
        bakdir = config.get(section, 'bakdir')
        bakdir_fullpath = os.path.join(root, bakdir)
        action = config.get(section, 'action')
        target = config.get(section, 'target')
        custom_cmd = config.get(section, 'cmd', None)
        utils.print_msg('> Excuting {}...'.format(section))
        cmd = CommandHandler(action, bakdir_fullpath, target, custom_cmd)
        cmd.execute()


if __name__ == '__main__':
    utils.print_msg('BAKCONFIGS')
    utils.print_msg('==========')

    parse_args()
    load_config()
    bak()

    utils.print_msg('\nNo errors - DONE')
    sys.exit(0)

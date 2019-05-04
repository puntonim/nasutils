#! /usr/bin/python
import os
import subprocess
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import utils


root = None
config = None


class CommandHandler(object):
    def __init__(self, action, bakdir, target):
        self.action = action
        self.bakdir = bakdir
        self.target = target.rstrip('/')
        # File name or dir name.
        self.target_name = self.target[self.target.rfind('/')+1:]

    def execute(self):
        if not os.path.isdir(self.bakdir):
            os.mkdir(self.bakdir)
        return getattr(self, '_' + self.action)()

    def _list(self):
        cmd = 'ls -alhs "{}" > "{}.txt"'.format(self.target, os.path.join(self.bakdir, self.target_name))
        subprocess.check_call(cmd, shell=True)

    def _zip(self):
        cmd = 'zip -r "{}.zip" "{}"'.format(os.path.join(self.bakdir, self.target_name), self.target_name)
        cwd = os.path.expanduser(self.target[:-len(self.target_name)])
        subprocess.check_call(cmd, cwd=cwd, shell=True)


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
    config = utils.ConfigParserLazy(path)


def bak():
    for section in config.sections():
        bakdir = config.get(section, 'bakdir')
        bakdir_fullpath = os.path.join(root, bakdir)
        action = config.get(section, 'action')
        target = config.get(section, 'target')
        utils.print_msg('> Excuting {}...'.format(section))
        cmd = CommandHandler(action, bakdir_fullpath, target)
        cmd.execute()


if __name__ == '__main__':
    utils.print_msg('BAKCONFIGS')
    utils.print_msg('==========')

    parse_args()
    load_config()
    bak()

    utils.print_msg('\nNo errors - DONE')
    sys.exit(0)

from __future__ import print_function

import sys


def exit_with_error_msg(msg):
    FAILCOL = '\033[91m'
    ENDCOL = '\033[0m'
    ERROR = FAILCOL + 'ERROR' + ENDCOL
    print(ERROR + ' ' + msg, file=sys.stderr)
    sys.exit(1)


def print_msg(msg):
    OKCOL = '\033[92m'
    ENDCOL = '\033[0m'
    OK = OKCOL + 'OK' + ENDCOL
    DONE = OKCOL + 'DONE' + ENDCOL
    print(msg.replace('OK', OK).replace('DONE', DONE))


def print_wrn(msg):
    WARNCOL = '\033[93m'
    ENDCOL = '\033[0m'
    print(WARNCOL + msg +ENDCOL)

#!/usr/bin/env python3

'''
$ rcfile.py
after=3 before=1 context=0 color=True
'''

import sys

from hashbang import command, Argument
from pathlib import Path

DIR = Path(__file__).parent


class RcFile:
    def __init__(self, filepath):
        self.filepath = filepath

    def apply_hashbang_extension(self, cmd):
        with self.filepath.open('r') as rcfile:
            rclines = list(rcfile.readlines())
            for line in rclines:
                key, value, *_ = line.rstrip('\n').split('=') + [None]
                cmd.default_values[key] = value


@command(RcFile(DIR/'rcfile'))
def grep(*, after=0, before=0, context=0, color=False):
    print('after={} before={} context={} color={}'.format(
        after, before, context, color))


if __name__ == '__main__':
    grep.execute()

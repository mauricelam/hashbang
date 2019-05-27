#!/usr/bin/env python3

'''
Add an example of how an extension can be created to read from a configuration
file where some arguments are preconfigured. This can work for positional
and optional arguments, but required positional arguments are still required,
so default value for those will never take effect

$ configfile.py
file='hashbang.py' after=3 before=1 context=0 color=True
'''

import sys

from hashbang import command, Argument
from pathlib import Path

DIR = Path(__file__).parent


class ConfigFile:
    def __init__(self, filepath):
        self.filepath = filepath

    def apply_hashbang_extension(self, cmd):
        with self.filepath.open('r') as configfile:
            lines = list(configfile.readlines())
            for line in lines:
                key, value, *_ = line.rstrip('\n').split('=', 1) + [None]
                cmd.default_values[key] = value


@command(
    ConfigFile(DIR/'configfile'),
    Argument('after', type=int),
    Argument('before', type=int),
    Argument('context', type=int))
def grep(file=None, *, after=0, before=0, context=0, color=False):
    print('file={} after={} before={} context={} color={}'.format(
        *[repr(i) for i in (file, after, before, context, color)]))


if __name__ == '__main__':
    grep.execute()

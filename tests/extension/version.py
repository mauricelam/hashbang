#!/usr/bin/env python3

'''
$ version.py --version
0.1.0
'''

import sys

from hashbang import command, Argument


class VersionArgument(Argument):
    def __init__(self, *args, version=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.version = version

    def add_argument(self, parser, argname, param, *, partial=False):
        parser.add_argument(
            '--version',
            action='version',
            version=self.version)


class Version:
    '''
    Demonstrates how an extension can be used to add an extra version argument.
    '''

    def __init__(self, version):
        super().__init__()
        self.versionarg = VersionArgument(version=version)

    def apply_hashbang_extension(self, cmd):
        cmd.arguments['version'] = (None, self.versionarg)


@command(Version('0.1.0'))
def main():
    print('Hello world')


if __name__ == '__main__':
    main.execute()

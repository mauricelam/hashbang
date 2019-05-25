#!/usr/bin/env python3

'''
$ version.py --version
0.1.0

$ version.py --help
> usage: version.py [--version] [-h]
>
> optional arguments:
>   --version   show program's version number and exit
>   -h, --help  show this help message and exit
'''

import sys

from hashbang import command, Argument


class Version(Argument):
    '''
    Demonstrates how an extension can be used to add an extra version argument.
    '''

    def __init__(self, version):
        super().__init__()
        self.version = version

    def apply_hashbang_extension(self, cmd):
        cmd.arguments['version'] = (None, self)

    def add_argument(self, parser, argname, param, *, partial=False):
        parser.add_argument(
            '--version',
            action='version',
            version=self.version)


@command(Version('0.1.0'))
def main():
    print('Hello world')


if __name__ == '__main__':
    main.execute()

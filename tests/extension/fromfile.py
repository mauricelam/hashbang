#!/usr/bin/env python3

'''
$ fromfile.py @fromfile.txt
arg1=None arg2=two arg3=three
'''

import sys

from hashbang import command, Argument


class FromFilePrefixChars:
    '''
    Demonstrates how an extension can be used to specify the
    fromfile_prefix_chars argument.
    '''

    def __init__(self, prefix):
        self.prefix = prefix

    def apply_hashbang_extension(self, cmd):
        cmd.argparse_kwargs['fromfile_prefix_chars'] = self.prefix


@command(FromFilePrefixChars('@'))
def main(*, arg1=None, arg2=None, arg3=None):
    print('arg1={} arg2={} arg3={}'.format(arg1, arg2, arg3))


if __name__ == '__main__':
    main.execute()

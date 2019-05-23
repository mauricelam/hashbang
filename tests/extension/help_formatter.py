#!/usr/bin/env python3

'''
$ help_formatter.py --help
> usage: help_formatter.py [-h]
>
> The description and the epilog is already formatted and should not be line
> wrapped.
>
> 1. One
> 2. Two
> 3. Three
>
> optional arguments:
>   -h, --help  show this help message and exit
'''

import argparse
import sys

from hashbang import command, Argument


@command(formatter_class=argparse.RawDescriptionHelpFormatter)
def help_formatter():
    '''
    The description and the epilog is already formatted and should not be line
    wrapped.

    1. One
    2. Two
    3. Three
    '''
    print('Hello world')


if __name__ == '__main__':
    help_formatter.execute()

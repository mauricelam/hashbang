#!/usr/bin/env python3

'''
$ subcommands_sorted.py  # returncode=2 stderr=True
usage: subcommands_sorted.py [-h] {one,two,three,four}
subcommands_sorted.py: error: the following arguments are required: subcommand

$ subcommands_sorted.py one 123 456 789
subcommand1 arg=123 remaining=('456', '789') flag1=False

$ subcommands_sorted.py two 345 678 9
subcommand2 arg=345 remaining=('678', '9') flag2=False
'''

from hashbang import command, subcommands
import sys


@command
def subcommand1(arg, *remaining, flag1=False):
    print(
            'subcommand1 arg={} remaining={} flag1={}'
            .format(arg, remaining, flag1))


@command
def subcommand2(arg, *remaining, flag2=False):
    print(
            'subcommand2 arg={} remaining={} flag2={}'
            .format(arg, remaining, flag2))


if __name__ == '__main__':
    if sys.version_info >= (3, 6):
        # kwargs maintains declaration order on versions >= 3.6
        subcommands(
            one=subcommand1,
            two=subcommand2,
            three=subcommand2,
            four=subcommand2)
    else:
        # arg tuple order will be retained
        subcommands(
            ('one', subcommand1),
            ('two', subcommand2),
            ('three', subcommand2),
            ('four', subcommand2))

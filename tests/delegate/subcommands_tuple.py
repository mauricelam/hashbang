#!/usr/bin/env python3

'''
$ subcommands_tuple.py  # returncode=2 stderr=True
usage: subcommands_tuple.py [-h] {one,two,three,four}
subcommands_tuple.py: error: the following arguments are required: subcommand

$ subcommands_tuple.py one 123 456 789
subcommand1 arg=123 remaining=('456', '789') flag1=False

$ subcommands_tuple.py two 345 678 9
subcommand2 arg=345 remaining=('678', '9') flag2=False
'''

from hashbang import command, subcommands


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
    # arg tuple order will be retained
    subcommands(
        ('one', subcommand1),
        ('two', subcommand2),
        ('three', subcommand2),
        ('four', subcommand2))

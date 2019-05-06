#!/usr/bin/env python3

'''
$ basic.py  # returncode=2 stderr=True
usage: basic.py [--verbose] [-h] {subcommand1,subcommand2}
basic.py: error: the following arguments are required: subcommand

$ basic.py subcommand1 123 456 789
subcommand1 arg=123 remaining=('456', '789') flag1=False

$ basic.py subcommand2 345 678 9
subcommand2 arg=345 remaining=('678', '9') flag2=False

$ basic.py subcommand2 345 678 9 --verbose
Executing subcommand2...
subcommand2 arg=345 remaining=('678', '9') flag2=False

$ basic.py nonexistent  # returncode=2 stderr=True
usage: basic.py [--verbose] [-h] {subcommand1,subcommand2}
basic.py: error: argument subcommand: invalid choice: 'nonexistent' (choose from 'subcommand1', 'subcommand2')

$ basic.py --help  # returncode=100
> usage: basic.py [--verbose] [{subcommand1,subcommand2}]
>
> positional arguments:
>   {subcommand1,subcommand2}
>
> optional arguments:
>   --verbose

$ basic.py subcommand1 --help  # returncode=100
> usage: basic.py subcommand1 [--flag1] [arg] [remaining [remaining ...]]
>
> positional arguments:
>   arg
>   remaining
>
> optional arguments:
>   --flag1
'''

from hashbang import command, Argument, NoMatchingDelegate


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


@command.delegator
def main(
        subcommand: Argument(choices=('subcommand1', 'subcommand2')),
        *__rest__,
        verbose=False):
    if verbose:
        print('Executing {}...'.format(subcommand))
    if subcommand == 'subcommand1':
        subcommand1.execute(__rest__)
    elif subcommand == 'subcommand2':
        subcommand2.execute(__rest__)
    else:
        raise NoMatchingDelegate()


if __name__ == '__main__':
    main.execute()

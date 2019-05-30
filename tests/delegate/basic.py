#!/usr/bin/env python3

'''
$ basic.py  # returncode=2 stderr=True
usage: basic.py [--verbose] [-h] subcommand
basic.py: error: the following arguments are required: subcommand

$ basic.py subcommand1 123 456 789
subcommand1 arg='123' remaining=('456', '789') flag1=False verbose=False

$ basic.py subcommand2 345 678 9
subcommand2 arg='345' remaining=('678', '9') flag2=False verbose=False

$ basic.py subcommand2 345 678 9 --verbose
Executing subcommand2...
subcommand2 arg='345' remaining=('678', '9') flag2=False verbose=False

$ basic.py nonexistent  # returncode=1 stderr=True
No matching delegate

$ basic.py subcommand2 -- 123 -- --abcd
subcommand2 arg='123' remaining=('--abcd',) flag2=False verbose=False

$ basic.py --verbose subcommand2 123
Executing subcommand2...
subcommand2 arg='123' remaining=() flag2=False verbose=False

$ basic.py subcommand2 -- --verbose 123
subcommand2 arg='123' remaining=() flag2=False verbose=True

$ basic.py subcommand2 -- -- --verbose 123
subcommand2 arg='--verbose' remaining=('123',) flag2=False verbose=False

$ basic.py subcommand2 -- -- -- --verbose 123
subcommand2 arg='--' remaining=('--verbose', '123') flag2=False verbose=False

$ basic.py --help
> usage: basic.py [--verbose] subcommand
>
> positional arguments:
>   subcommand
>
> optional arguments:
>   --verbose

$ basic.py subcommand1 --help
> usage: basic.py subcommand1 [--flag1] [--verbose]
>                             arg [remaining [remaining ...]]
>
> positional arguments:
>   arg
>   remaining
>
> optional arguments:
>   --flag1
>   --verbose
'''

from hashbang import command, Argument, NoMatchingDelegate


@command
def subcommand1(arg, *remaining, flag1=False, verbose=False):
    print(
            'subcommand1 arg={} remaining={} flag1={} verbose={}'
            .format(*map(repr, (arg, remaining, flag1, verbose))))


@command
def subcommand2(arg, *remaining, flag2=False, verbose=False):
    print(
            'subcommand2 arg={} remaining={} flag2={} verbose={}'
            .format(*map(repr, (arg, remaining, flag2, verbose))))


@command.delegator
def main(
        # Usually you would want to specify the choices for a subcommand arg
        # subcommand: Argument(choices=('subcommand1', 'subcommand2')),
        subcommand,
        *_REMAINDER_,
        verbose=False):
    if verbose:
        print('Executing {}...'.format(subcommand))
    if subcommand == 'subcommand1':
        subcommand1.execute(_REMAINDER_)
    elif subcommand == 'subcommand2':
        subcommand2.execute(_REMAINDER_)
    else:
        raise NoMatchingDelegate()


if __name__ == '__main__':
    main.execute()

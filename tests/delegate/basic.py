#!/usr/bin/env python3

'''
$ basic.py  # returncode=2 stderr=True
usage: basic.py [--verbose] [-h] subcommand
basic.py: error: the following arguments are required: subcommand

$ basic.py subcommand1 123 456 789
subcommand1 arg=123 remaining=('456', '789') flag1=False

$ basic.py subcommand2 345 678 9
subcommand2 arg=345 remaining=('678', '9') flag2=False

$ basic.py subcommand2 345 678 9 --verbose
Executing subcommand2...
subcommand2 arg=345 remaining=('678', '9') flag2=False

$ basic.py nonexistent  # returncode=1 stderr=True
No matching delegate

$ basic.py subcommand2 -- 123 -- --abcd
subcommand2 arg=123 remaining=('--abcd',) flag2=False

$ basic.py --help
> usage: basic.py [--verbose] subcommand
>
> positional arguments:
>   subcommand
>
> optional arguments:
>   --verbose

$ basic.py subcommand1 --help
> usage: basic.py subcommand1 [--flag1] arg [remaining [remaining ...]]
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

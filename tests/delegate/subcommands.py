#!/usr/bin/env python3

'''
$ subcommands.py  # returncode=2 stderr=True
usage: subcommands.py [-h] {pairs,kwargs,auto}
subcommands.py: error: the following arguments are required: subcommand

$ subcommands.py --help  # returncode=100
> usage: subcommands.py [{pairs,kwargs,auto}]
>
> positional arguments:
>   {pairs,kwargs,auto}

$ subcommands.py auto --help  # returncode=100
> usage: subcommands.py auto [{one,two,on1,tw2}]
>
> positional arguments:
>   {one,two,on1,tw2}

$ subcommands.py pairs --help  # returncode=100
> usage: subcommands.py pairs [{one,two,on1,tw2}]
>
> positional arguments:
>   {one,two,on1,tw2}

$ subcommands.py kwargs --help  # returncode=100 glob=True
> usage: subcommands.py kwargs [{*}]
>
> positional arguments:
>   {*}

$ subcommands.py auto one 123 456 789
subcommand1 arg=123 remaining=('456', '789') flag1=False

$ subcommands.py auto two 345 678 9
subcommand2 arg=345 remaining=('678', '9') flag2=False

$ subcommands.py <TAB>
pairs\x0bkwargs\x0bauto

$ subcommands.py au<TAB>
auto 

$ subcommands.py auto <TAB>
one\x0btwo\x0bon1\x0btw2

$ subcommands.py auto o<TAB>
one\x0bon1
'''

from hashbang import command, subcommands, Argument, NoMatchingDelegate
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


# Using pairs preserves the insertion order
pairs = subcommands(
        ('one', subcommand1),
        ('two', subcommand2),
        ('on1', subcommand1),
        ('tw2', subcommand2))

# Using keyword arguments preserve insertion order in python 3.6 or above,
# and sorts by key on lower versions
kwargs = subcommands(
        one=subcommand1,
        two=subcommand2,
        on1=subcommand1,
        tw2=subcommand2)


@command.delegator
def main(
        subcommand: Argument(choices=('pairs', 'kwargs', 'auto')),
        *_REMAINDER_):
    if subcommand == 'auto':
        if sys.version_info >= (3, 6):
            return kwargs.execute(_REMAINDER_)
        else:
            return pairs.execute(_REMAINDER_)
    elif subcommand == 'pairs':
        return pairs.execute(_REMAINDER_)
    elif subcommand == 'kwargs':
        return kwargs.execute(_REMAINDER_)
    else:
        raise NoMatchingDelegate()


if __name__ == '__main__':
    main.execute()

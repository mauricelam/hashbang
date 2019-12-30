#!/usr/bin/env python3

'''
$ context.py subcommand1 123 456
subcommand1 arg='123' remaining=('456',) flag1=False verbose=False \
context=[Context]

$ context.py subcommand1 123 456 --verbose
Executing subcommand1 with [Context]...
subcommand1 arg='123' remaining=('456',) flag1=False verbose=True \
context=[Context]

$ context.py subcommand1 --help
> usage: context.py subcommand1 [--flag1] [--verbose]
>                               arg [remaining [remaining ...]]
>
> positional arguments:
>   arg
>   remaining
>
> optional arguments:
>   --flag1
>   --verbose

$ context.py subcommand2 123 456 --verbose
Executing subcommand2 with [Context]...
subcommand2 arg='123' remaining=('456',) flag2=False verbose=True \
context=[Context]
'''

from hashbang import command, Argument, NoMatchingDelegate


@command(
    Argument('context_', py_only=True))
def subcommand1(arg, *remaining, flag1=False, verbose=False, context_=None):
    print(
            'subcommand1 arg={} remaining={} flag1={} verbose={} context={}'
            .format(*map(repr, (arg, remaining, flag1, verbose, context_))))


@command(
    Argument('context', py_only=True))
def subcommand2(arg, *remaining, flag2=False, verbose=False, context=None):
    print(
            'subcommand2 arg={} remaining={} flag2={} verbose={} context={}'
            .format(*map(repr, (arg, remaining, flag2, verbose, context))))


class Context:
    def __repr__(self):
        return '[Context]'


@command.delegator
def main(
        # Usually you would want to specify the choices for a subcommand arg
        # subcommand: Argument(choices=('subcommand1', 'subcommand2')),
        subcommand,
        *_REMAINDER_,
        verbose=False):
    context = Context()
    if verbose:
        print('Executing {} with {}...'.format(subcommand, context))
    if subcommand == 'subcommand1':
        subcommand1.execute(
            _REMAINDER_,
            verbose=verbose,
            context_=context)
    elif subcommand == 'subcommand2':
        subcommand2.execute(
            _REMAINDER_,
            verbose=verbose,
            context=context)
    else:
        raise NoMatchingDelegate()


if __name__ == '__main__':
    main.execute()

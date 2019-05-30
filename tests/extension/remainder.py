#!/usr/bin/env python3

'''
$ remainder.py my-script.sh
scriptfile='my-script.sh' interactive=False command=()

$ remainder.py my-script.sh -i
scriptfile='my-script.sh' interactive=True command=()

$ remainder.py my-script.sh -i -c ls /usr
scriptfile='my-script.sh' interactive=True command=['ls', '/usr']

$ remainder.py my-script.sh -c ls /usr -i
scriptfile='my-script.sh' interactive=False command=['ls', '/usr', '-i']

$ remainder.py --help
> usage: remainder.py [--interactive] [--command ...] [-h] [scriptfile]
>
> positional arguments:
>   scriptfile
>
> optional arguments:
>   --interactive, -i
>   --command ..., -c ...
>   -h, --help            show this help message and exit
'''

import argparse
import sys

from hashbang import command, Argument


class RemainderArgument(Argument):
    '''
    This example uses nargs=argparse.REMAINDER, to capture everything after an
    optional argument ('-c'). argparse.REMAINDER should typically used for
    optional arguments, whereas *_REMAINDER_ should be used for positional
    arguments (capturing without a '-c' flag).
    '''

    def add_argument(self, cmd, arg_container, param):
        argument = arg_container.add_argument(
            *self.get_flag_names(param.name.rstrip('_')),
            action='store',
            nargs=argparse.REMAINDER,
            # For append arguments, argparse calls append() directly
            # on the default, so make sure we don't reuse the default
            # value, and convert to list to allow tuples as defaults
            default=param.default,
            dest=param.name,
            choices=self.choices,
            help=self.help,
            type=self.type,
            required=self.required)


@command(
    Argument('interactive', aliases=('i',)),
    RemainderArgument('command', aliases=('c',)))
def bash(scriptfile=None, *, interactive=False, command=()):
    print('scriptfile={} interactive={} command={}'.format(
        *map(repr, (scriptfile, interactive, command))))


if __name__ == '__main__':
    bash.execute()

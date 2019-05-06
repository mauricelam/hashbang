#!/usr/bin/env python3

'''
$ help.py --help  # returncode=100
> usage: help.py [--arg ARG] [-h]
>
> optional arguments:
>   --arg ARG   The argument
>   -h, --help  show this help message and exit
'''

from hashbang import command, Argument


@command
def main(*, arg: Argument(help='The argument') = 'one'):
    print('arg={}'.format(arg))


if __name__ == '__main__':
    main.execute()

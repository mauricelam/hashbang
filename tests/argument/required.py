#!/usr/bin/env python3

'''
$ required.py --help
> usage: required.py --arg ARG --flag [-h]
>
> optional arguments:
>   --arg ARG
>   --flag
>   -h, --help  show this help message and exit

$ required.py  # returncode=2 stderr=True
usage: required.py --arg ARG --flag [-h]
required.py: error: the following arguments are required: --arg

$ required.py --arg chocolate  # returncode=2 stderr=True
usage: required.py --arg ARG --flag [-h]
required.py: error: one of the arguments --flag is required

$ required.py --arg chocolate --flag
arg='chocolate' flag=True

$ required.py --arg chocolate --noflag
arg='chocolate' flag=False
'''

from hashbang import command, Argument


@command(
    Argument('arg', required=True),
    Argument('flag', required=True))
def main(*, arg=None, flag=False):
    print('arg={} flag={}'.format(*map(repr, (arg, flag))))


if __name__ == '__main__':
    main.execute()

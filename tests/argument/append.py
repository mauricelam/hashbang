#!/usr/bin/env python3

'''
$ append.py --help
> usage: append.py [--arg ARG] [-h]
>
> optional arguments:
>   --arg ARG
>   -h, --help  show this help message and exit

$ append.py
arg=[]

$ append.py --arg chocolate
arg=['chocolate']

$ append.py --arg chocolate --arg hazelnut --arg nutella
arg=['chocolate', 'hazelnut', 'nutella']
'''

from hashbang import command, Argument


@command(Argument('arg', append=True))
def main(*, arg=()):
    print('arg={}'.format(*map(repr, (arg,))))


if __name__ == '__main__':
    main.execute()

#!/usr/bin/env python3

'''
$ choices.py --help  # returncode=100
> usage: choices.py [--arg {one,two,three}] [-h]
>
> optional arguments:
>   --arg {one,two,three}
>   -h, --help            show this help message and exit

$ choices.py --<TAB>
--arg 

$ choices.py --arg <TAB>
one\x0btwo\x0bthree
'''

from hashbang import command, Argument


@command
def main(*, arg: Argument(choices=('one', 'two', 'three')) = 'one'):
    print('arg={}'.format(arg))


if __name__ == '__main__':
    main.execute()

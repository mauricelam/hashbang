#!/usr/bin/env python3

'''
$ return_value_processor.py
a
b
c

$ return_value_processor.py --help
> usage: print_abc [-h]
>
> optional arguments:
>   -h, --help  show this help message and exit
'''

from hashbang import command


@command(
    prog='print_abc',
    return_value_processor=lambda v: print('\n'.join(v)))
def abc():
    return ['a', 'b', 'c']


if __name__ == '__main__':
    abc.execute()

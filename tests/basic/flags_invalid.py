#!/usr/bin/env python3

'''
$ flags_invalid.py  # returncode=1 stderr=True
Error: Choices cannot be specified for boolean flag "flag1"
'''

from hashbang import command, Argument


@command
def main(*, flag1: Argument(choices=('a', 'b')) = False):
    print('flag1={}'.format(flag1))


if __name__ == '__main__':
    main.execute()

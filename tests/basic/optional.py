#!/usr/bin/env python3

'''
$ optional.py 123
arg1='123' arg2='default'

$ optional.py 123 789
arg1='123' arg2='789'
'''

from hashbang import command


@command
def main(arg1, arg2='default'):
    print('arg1={} arg2={}'.format(*map(repr, (arg1, arg2))))


if __name__ == '__main__':
    main.execute()

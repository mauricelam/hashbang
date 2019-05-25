#!/usr/bin/env python3

'''
$ callable.py aloha --flag1
arg=aloha flag1=True
'''

import sys

from hashbang import command


class MyCallableClass:

    attribute1 = 'attr1'

    def __call__(self, arg, *, flag1=False):
        print('arg={} flag1={}'.format(arg, flag1))


original = MyCallableClass()
main = command(original)


if __name__ == '__main__':
    main.execute()

#!/usr/bin/env python3

'''
Note: Using hashbang.command on non-function callable classes is not
recommended. This test is here to make sure we don't unintentionally change
the behavior, but it may intentionally be changed in the future.

For a more proper usage, consider making a proxy function, like wrap_callable
in tests/experimental/class.py.

$ callable.py aloha --flag1
arg=aloha flag1=True
'''

import sys

from hashbang import command


class MyCallableClass:

    def __init__(self):
        self.attribute1 = 'attr1'

    def __call__(self, arg, *, flag1=False):
        print('arg={} flag1={}'.format(arg, flag1))


original = MyCallableClass()
main = command(original)


if __name__ == '__main__':
    main.execute()

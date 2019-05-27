#!/usr/bin/env python3

'''
$ append_invalid_default.py  # returncode=1 stderr=True
Error: When "append" is true, the default value of the argument must be empty \
to avoid the surprising behavior described in \
https://bugs.python.org/issue16399.
Instead, use `arg = arg or ("default value")` in your implementation.
'''

from hashbang import command, Argument


@command(Argument('arg', append=True))
def main(*, arg=('default value is not allowed')):
    print('arg={}'.format(*map(repr, (arg,))))


if __name__ == '__main__':
    main.execute()

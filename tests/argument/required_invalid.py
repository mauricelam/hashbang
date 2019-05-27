#!/usr/bin/env python3

'''
$ required_invalid.py  # returncode=1 stderr=True
Error: "required" does not apply to positional arguments. Specify a default \
value if you want optional positional args.
e.g. def func(foo=123)
'''

from hashbang import command, Argument


@command(Argument('arg', required=True))
def main(arg='one'):
    print('arg={}'.format(repr(arg)))


if __name__ == '__main__':
    main.execute()

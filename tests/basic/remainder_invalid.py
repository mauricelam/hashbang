#!/usr/bin/env python3

'''
$ remainder_invalid.py 123  # returncode=1 stderr=True
Error: Remainder arg "arg1" must be variadic (*arg)
'''

from hashbang import command, Argument


@command
def main(arg1: Argument(remainder=True), flag1=False):
    print('arg1={} _REMAINDER_={} flag1={}'.format(arg1, _REMAINDER_, flag1))


if __name__ == '__main__':
    main.execute()

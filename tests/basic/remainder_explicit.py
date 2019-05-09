#!/usr/bin/env python3

'''
$ remainder_explicit.py 123
arg1=123 rem=() flag1=False

$ remainder_explicit.py 123 456 789 --aloha
arg1=123 rem=('456', '789', '--aloha') flag1=False

$ remainder_explicit.py 123 456 789 --aloha --flag1
arg1=123 rem=('456', '789', '--aloha') flag1=True
'''

from hashbang import command, Argument


@command
def main(arg1, *rem: Argument(remainder=True), flag1=False):
    print('arg1={} rem={} flag1={}'.format(arg1, rem, flag1))


if __name__ == '__main__':
    main.execute()

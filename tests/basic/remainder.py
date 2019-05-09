#!/usr/bin/env python3

'''
$ remainder.py 123
arg1=123 _REMAINDER_=() flag1=False

$ remainder.py 123 456 789 --aloha
arg1=123 _REMAINDER_=('456', '789', '--aloha') flag1=False

$ remainder.py 123 456 789 --aloha --flag1
arg1=123 _REMAINDER_=('456', '789', '--aloha') flag1=True
'''

from hashbang import command


@command
def main(arg1, *_REMAINDER_, flag1=False):
    print('arg1={} _REMAINDER_={} flag1={}'.format(arg1, _REMAINDER_, flag1))


if __name__ == '__main__':
    main.execute()

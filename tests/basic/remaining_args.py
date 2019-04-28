#!/usr/bin/env python3

'''
$ remaining_args.py 123
arg1=123 __rest__=() flag1=False

$ remaining_args.py 123 456 789 --aloha
arg1=123 __rest__=('456', '789', '--aloha') flag1=False

$ remaining_args.py 123 456 789 --aloha --flag1
arg1=123 __rest__=('456', '789', '--aloha') flag1=True
'''

from hashbang import command, Argument


@command
def main(arg1, *__rest__, flag1=False):
    print('arg1={} __rest__={} flag1={}'.format(arg1, __rest__, flag1))


if __name__ == '__main__':
    main.execute()

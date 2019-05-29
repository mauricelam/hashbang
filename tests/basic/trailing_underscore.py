#!/usr/bin/env python3

'''
$ trailing_underscore.py abc def ghi --flag1 --flag2
arg='abc' args=('def', 'ghi') flag1=True flag2=True

$ trailing_underscore.py '' --noflag1 --noflag2
arg='' args=() flag1=False flag2=False

$ trailing_underscore.py aloha
arg='aloha' args=() flag1=False flag2=True
'''

from hashbang import command


@command
def main(arg_, *args_, flag1_=False, flag2_=True):
    '''
    Trailing underscores should be skipped in flag names
    '''
    print('arg={} args={} flag1={} flag2={}'.format(
        *map(repr, (arg_, args_, flag1_, flag2_))))


if __name__ == '__main__':
    main.execute()

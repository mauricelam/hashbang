#!/usr/bin/env python3

'''
$ flags_.py --flag1 --flag2
flag1=True flag2=True

$ flags_.py --noflag1 --noflag2
flag1=False flag2=False

$ flags_.py
flag1=False flag2=True
'''

from hashbang import command


@command
def main(*, flag1_=False, flag2_=True):
    '''
    Trailing underscores should be skipped in flag names
    '''
    print('flag1={} flag2={}'.format(flag1_, flag2_))


if __name__ == '__main__':
    main.execute()

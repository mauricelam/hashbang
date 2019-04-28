#!/usr/bin/env python3

'''
$ flags.py --flag1 --flag2
flag1=True flag2=True

$ flags.py --noflag1 --noflag2
flag1=False flag2=False

$ flags.py
flag1=False flag2=True
'''

from hashbang import command

@command
def main(*, flag1=False, flag2=True):
    print('flag1={} flag2={}'.format(flag1, flag2))

if __name__ == '__main__':
    main.execute()

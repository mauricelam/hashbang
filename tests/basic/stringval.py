#!/usr/bin/env python3

'''
$ stringval.py --flag1  # returncode=2 stderr=True
usage: stringval.py [--flag1 FLAG1] [-h]
stringval.py: error: argument --flag1: expected one argument

$ stringval.py --flag1 one
flag1=one

$ stringval.py --flag1=ONE
flag1=ONE
'''

from hashbang import command

@command
def main(*, flag1='hello'):
    print('flag1={}'.format(flag1))

if __name__ == '__main__':
    main.execute()

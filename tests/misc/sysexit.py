#!/usr/bin/env python3

'''
$ sysexit.py  # returncode=111
one one one
'''

import sys

from hashbang import command


@command
def main():
    print('one one one')
    sys.exit(111)


if __name__ == '__main__':
    main.execute()

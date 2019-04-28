#!/usr/bin/env python3

'''
$ positional_args.py 123 456
arg1=123 arg2=456

$ positional_args.py 123  # returncode=2 stderr=True
usage: positional_args.py [-h] arg1 arg2
positional_args.py: error: the following arguments are required: arg2
'''

from command import command

@command
def main(arg1, arg2):
    print('arg1={} arg2={}'.format(arg1, arg2))

if __name__ == '__main__':
    main.execute()

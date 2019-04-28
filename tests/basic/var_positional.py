#!/usr/bin/env python3

'''
$ var_positional.py  # returncode=2 stderr=True
usage: var_positional.py [-h] arg1 [arg2] [args [args ...]]
var_positional.py: error: the following arguments are required: arg1, args

$ var_positional.py 123
arg1=123 arg2=two args=()

$ var_positional.py 123 456
arg1=123 arg2=456 args=()

$ var_positional.py 123 456 789
arg1=123 arg2=456 args=('789',)

$ var_positional.py 123 456 789 000 111
arg1=123 arg2=456 args=('789', '000', '111')

$ var_positional.py 123 456 --abc  # returncode=2 stderr=True
usage: var_positional.py [-h] arg1 [arg2] [args [args ...]]
var_positional.py: error: unrecognized arguments: --abc

$ var_positional.py --help  # returncode=100
> usage: var_positional.py [-h] arg1 [arg2] [args [args ...]]
>
> positional arguments:
>   arg1
>   arg2
>   args
>
> optional arguments:
>   -h, --help  show this help message and exit
'''

from hashbang import command

@command
def main(arg1, arg2='two', *args):
    print('arg1={} arg2={} args={}'.format(arg1, arg2, args))

if __name__ == '__main__':
    main.execute()

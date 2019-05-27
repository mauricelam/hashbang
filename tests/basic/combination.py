#!/usr/bin/env python3

'''
$ combination.py 123
arg1='123' arg2='two' args=() flag1=False flag2=True opt='default'

$ combination.py 123 --flag1 --noflag2
arg1='123' arg2='two' args=() flag1=True flag2=False opt='default'

$ combination.py 123 456 789 --opt='halo'
arg1='123' arg2='456' args=('789',) flag1=False flag2=True opt='halo'
'''

from hashbang import command


@command
def main(
        arg1,
        arg2='two',
        *args,
        flag1=False,
        flag2=True,
        opt='default'):
    print('arg1={} arg2={} args={} flag1={} flag2={} opt={}'.format(
            *map(repr, (arg1, arg2, args, flag1, flag2, opt))))


if __name__ == '__main__':
    main.execute()

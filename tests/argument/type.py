#!/usr/bin/env python3

'''
$ type.py
args=() port=0
<class 'int'>

$ type.py 123 456 789 --port=123
args=(123, 456, 789) port=123
<class 'int'>
'''

from hashbang import command, Argument


@command
def main(*args: Argument(type=int),
         port: Argument(type=int) = 0):
    print('args={} port={}'.format(*map(repr, (args, port))))
    print('{}'.format(type(port)))


if __name__ == '__main__':
    main.execute()

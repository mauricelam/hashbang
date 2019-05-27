#!/usr/bin/env python3

'''
$ type_annotation.py
arg='one'

$ type_annotation.py --arg two
arg='two'
'''

from hashbang import command, Argument


@command
def main(*, arg: str = 'one'):
    '''
    Test to make sure that non-Argument annotations are ignored
    '''
    print('arg={}'.format(repr(arg)))


if __name__ == '__main__':
    main.execute()

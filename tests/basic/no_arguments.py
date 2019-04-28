#!/usr/bin/env python3

'''
$ no_arguments.py
Hello world
'''

from command import command

@command
def main():
    '''Function with no arguments'''
    print('Hello world')

if __name__ == '__main__':
    main.execute()

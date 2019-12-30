#!/usr/bin/env python3

'''
$ nonexistent.py  # returncode=1 stderr=True glob=True
> Traceback (most recent call last):
>   ...
> RuntimeError: Command property "nonexistent" cannot be set
'''

from hashbang import command


@command(nonexistent='foobar')
def main():
    print('Hello world')


if __name__ == '__main__':
    main.execute()

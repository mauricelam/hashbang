#!/usr/bin/env python3

'''
$ nonexistent.py  # returncode=1 stderr=True glob=True
> Traceback (most recent call last):
>   File "*nonexistent.py", line *, in <module>
>     @command(nonexistent='foobar')
>   ...
> RuntimeError: Command property "nonexistent" cannot be set
'''

from hashbang import command


@command(nonexistent='foobar')
def main():
    print('Hello world')


if __name__ == '__main__':
    main.execute()

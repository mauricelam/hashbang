#!/usr/bin/env python3

'''
$ kwarg_parser.py  # returncode=1 stderr=True glob=True
> Traceback (most recent call last):
>   File "*parser.py", line *, in <module>
>     @command(parser='foobar')
>   ...
> RuntimeError: Command property "parser" cannot be set
'''

from hashbang import command


@command(parser='foobar')
def main():
    print('Hello world')


if __name__ == '__main__':
    main.execute()

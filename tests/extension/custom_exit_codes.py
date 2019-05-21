#!/usr/bin/env python3

'''
$ custom_exit_codes.py  # returncode=1
CustomError

$ custom_exit_codes.py --exitcode=44  # returncode=44
CustomError
'''

import sys

from hashbang import command, Argument


def exception_handler(exception):
    try:
        raise exception
    except CustomError as e:
        print('CustomError')
        sys.exit(e.exitcode())


class CustomError(Exception):

    def __init__(self, code):
        super().__init__()
        self.code = code

    def exitcode(self):
        return self.code


@command(
    Argument('exitcode', type=int),
    exception_handler=exception_handler)
def main(*, exitcode=1):
    raise CustomError(exitcode)


if __name__ == '__main__':
    main.execute()

#!/usr/bin/env python3

'''
$ exception_handler.py  # returncode=1 stderr=True glob=True
> Traceback (most recent call last):
>   File "exception_handler.py", line *, in <module>
>     raiser.execute()
>   ...
>   File "exception_handler.py", line *, in raiser
>     raise Exception('Raiser: Exception')
> Exception: Raiser: Exception

$ exception_handler.py --error=runtime  # returncode=1 stderr=True glob=True
> Traceback (most recent call last):
>   File "exception_handler.py", line *, in <module>
>     raiser.execute()
>   ...
>   File "exception_handler.py", line *, in raiser
>     raise RuntimeError('Raiser: RuntimeError')
> RuntimeError: Raiser: RuntimeError

$ exception_handler.py --error=custom  # returncode=1 stderr=True
This is a custom exception
'''

import sys

from hashbang import command


class CustomException(Exception):
    def message(self):
        return 'This is a custom exception'


def exception_handler(exception):
    try:
        raise exception
    except CustomException as e:
        print(e.message(), file=sys.stderr)


@command(exception_handler=exception_handler)
def raiser(*, error=None):
    if error == 'runtime':
        raise RuntimeError('Raiser: RuntimeError')
    elif error == 'custom':
        raise CustomException()
    else:
        raise Exception('Raiser: Exception')


if __name__ == '__main__':
    raiser.execute()

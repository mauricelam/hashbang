#!/usr/bin/env python3

'''
$ error.py  # returncode=1 stderr=True
Error: runtime error

$ error.py --error=subprocess # returncode=1 stderr=True glob=True
Error: Command 'exit 132' returned non-zero exit status 132*

$ error.py --error=custom. # returncode=1 stderr=True glob=True
> Traceback (most recent call last):
>   File "error.py", *
>     main.execute()
>   ...
>   File "error.py", *
>     raise CustomError('custom error')
> __main__.CustomError: custom error
'''

from hashbang import command
import subprocess


@command
def main(*, error='runtime'):
    if error == 'subprocess':
        subprocess.check_call('exit 132', shell=True)
    elif error == 'runtime':
        raise RuntimeError('runtime error')
    else:
        raise CustomError('custom error')


class CustomError(Exception):
    pass


if __name__ == '__main__':
    main.execute()

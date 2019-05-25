#!/usr/bin/env python3

'''
$ decorator_arguments.py --<TAB>
--arg\x0b--file

$ decorator_arguments.py --arg <TAB>
app\x0bapk\x0bexe

$ decorator_arguments.py --arg a<TAB>
app\x0bapk

$ decorator_arguments.py -f /u/b/e<TAB>
/usr/bin/env 
'''

from hashbang import command, Argument
from hashbang.completion import fuzzy_path_validator


@command(
    Argument('arg', completer=lambda **_: ('app', 'apk', 'exe')),
    Argument('file',
             aliases=('f',),
             completer=lambda **_: ('/usr/bin/env', '/usr/bin/python'),
             completion_validator=fuzzy_path_validator))
def main(*, arg='one', file=None):
    print('arg={}'.format(arg))


if __name__ == '__main__':
    main.execute()

#!/usr/bin/env python3

'''
$ completer.py --<TAB>
--arg\x0b--file

$ completer.py --arg <TAB>
app\x0bapk\x0bexe

$ completer.py --arg a<TAB>
app\x0bapk

$ completer.py -f /u/b/e<TAB>
/usr/bin/env 
'''

from hashbang import command, Argument, fuzzy_path_validator


@command
def main(
        *,
        arg: Argument(
            completer=lambda **_: ('app', 'apk', 'exe')) = 'one',
        file: Argument(
            aliases=('f',),
            completer=lambda **_: ('/usr/bin/env', '/usr/bin/python'),
            validator=fuzzy_path_validator) = None):
    print('arg={}'.format(arg))


if __name__ == '__main__':
    main.execute()

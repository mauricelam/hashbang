#!/usr/bin/env python3

'''
$ disallow_abbrev.py --o  # returncode=2 stderr=True minpython=3.5
usage: disallow_abbrev.py [--one] [--two] [--three] [-h]
disallow_abbrev.py: error: unrecognized arguments: --o

$ disallow_abbrev.py --t  # returncode=2 stderr=True minpython=3.5
usage: disallow_abbrev.py [--one] [--two] [--three] [-h]
disallow_abbrev.py: error: unrecognized arguments: --t

$ disallow_abbrev.py --two --three # minpython=3.5
one=False two=True three=True
'''

from hashbang import command


@command(allow_abbrev=False)
def main(*, one=False, two=False, three=False):
    print('one={} two={} three={}'.format(*map(repr, (one, two, three))))


if __name__ == '__main__':
    main.execute()

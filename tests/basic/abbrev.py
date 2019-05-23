#!/usr/bin/env python3

'''
$ abbrev.py --o
one=True two=False three=False

$ abbrev.py --t  # returncode=2 stderr=True
usage: abbrev.py [--one] [--two] [--three] [-h]
abbrev.py: error: ambiguous option: --t could match --two, --three

$ abbrev.py --tw --thr
one=False two=True three=True
'''

from hashbang import command


@command
def main(*, one=False, two=False, three=False):
    print('one={} two={} three={}'.format(one, two, three))


if __name__ == '__main__':
    main.execute()

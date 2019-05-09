#!/usr/bin/env python3

'''
$ aliases.py -f -F
flag1=True flag2=True

$ aliases.py
flag1=False flag2=True

$ aliases.py -f --noflag2
flag1=True flag2=False

$ aliases.py -t --nof
flag1=False flag2=True

# Last flag wins, so --noF overrides -t
$ aliases.py -t --noF
flag1=False flag2=False

$ aliases.py --noF -t
flag1=False flag2=True

$ aliases.py --flagone
flag1=True flag2=True

$ aliases.py --f  # returncode=2 stderr=True glob=True
usage: aliases.py [--flag1] [--flag2] [-h]
aliases.py: error: ambiguous option: --f could match *
'''

from hashbang import command, Argument


@command
def main(*,
         flag1: Argument(aliases=('f', 'flagone')) = False,
         flag2: Argument(aliases='Ft') = True):
    '''
    Aliases are sequences, so a normal string will be split into characters
    for each alias, while multi-character aliases should use tuples.
    '''
    print('flag1={} flag2={}'.format(flag1, flag2))


if __name__ == '__main__':
    main.execute()

#!/usr/bin/env python3

'''
$ custom_prefix.py ++one ++two
one=True two=True three=False

$ custom_prefix.py +2 --three
one=False two=True three=True
'''

from hashbang import command, Argument


class PlusArgument(Argument):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)

    def get_flag_names(self, name):
        return ['++' + name] + [('+' if len(i) == 1 else '++') + i
                                for i in self.aliases]

    def get_negative_flag_names(self, name):
        return ['++no' + name] + ['++no' + i for i in self.aliases]

    def apply_hashbang_extension(self, cmd):
        super().apply_hashbang_extension(cmd)
        prefix_chars = cmd.argparse_kwargs.get('prefix_chars', '-')
        if '+' not in prefix_chars:
            cmd.argparse_kwargs['prefix_chars'] = prefix_chars + '+'


@command(
    PlusArgument('one'),
    PlusArgument('two', aliases=('2',)))
def main(*, one=False, two=False, three=False):
    print('one={} two={} three={}'.format(*map(repr, (one, two, three))))


if __name__ == '__main__':
    main.execute()

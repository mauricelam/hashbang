#!/usr/bin/env python3

'''
$ mutually_exclusive.py --help
> usage: mutually_exclusive.py [--flag1 | --flag2 | --flag3] [-h]
>
> optional arguments:
>   --flag1
>   --flag2
>   --flag3
>   -h, --help  show this help message and exit

$ mutually_exclusive.py
flag1=False flag2=False flag3=False

$ mutually_exclusive.py --flag1
flag1=True flag2=False flag3=False

$ mutually_exclusive.py --noflag1 --flag2  # returncode=2 stderr=True
usage: mutually_exclusive.py [--flag1 | --flag2 | --flag3] [-h]
mutually_exclusive.py: error: argument --flag2: not allowed with argument \
--noflag1

$ mutually_exclusive.py --flag1 --flag3  # returncode=2 stderr=True
usage: mutually_exclusive.py [--flag1 | --flag2 | --flag3] [-h]
mutually_exclusive.py: error: argument --flag3: not allowed with argument \
--flag1
'''

from hashbang import command, Argument


class MutuallyExclusiveGroup:
    def __init__(self, name, *, required=False):
        self.name = name
        self.group = None
        self.required = required

    def apply_hashbang_extension(self, cmd):
        cmd.__groups = \
            getattr(cmd, '_MutuallyExclusiveGroup__groups', None) or {}
        if self.name not in cmd.__groups:
            cmd.__groups[self.name] = self

    def create_group(self, parser):
        if self.group is None:
            self.group = parser.add_mutually_exclusive_group(
                required=self.required)
        return self.group


class GroupArgument(Argument):
    def __init__(self, name, *args, group=None, **kwargs):
        super().__init__(name, *args, **kwargs)
        if group is None:
            raise RuntimeError('Group name cannot be none')
        self.group = group

    def add_argument(self, cmd, parser, param):
        parser = cmd._MutuallyExclusiveGroup__groups[self.group]\
            .create_group(parser)
        super().add_argument(cmd, parser, param)


@command(
    MutuallyExclusiveGroup('one'),
    GroupArgument('flag1', group='one'),
    GroupArgument('flag2', group='one'),
    GroupArgument('flag3', group='one'))
def main(*, flag1=False, flag2=False, flag3=False):
    print('flag1={} flag2={} flag3={}'.format(
        *map(repr, (flag1, flag2, flag3))))


if __name__ == '__main__':
    main.execute()

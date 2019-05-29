#!/usr/bin/env python3

'''
$ argument_group.py --help
> usage: argument_group.py --flag1 [--flag2] [-h] pos1 [pos2] [args [args ...]]
>
> positional arguments:
>   args
>
> optional arguments:
>   -h, --help  show this help message and exit
>
> Group #1:
>   First group.
>
>   pos1        First positional argument
>   --flag1     First flag
>
> Group #2:
>   pos2        Second positional argument
>   --flag2     Second flag

$ argument_group.py 123  # returncode=2 stderr=True
usage: argument_group.py --flag1 [--flag2] [-h] pos1 [pos2] [args [args ...]]
argument_group.py: error: one of the arguments --flag1 is required

$ argument_group.py 123 --noflag1 --flag2
pos1='123' pos2=None args=() flag1=False flag2=True
'''

from hashbang import command, Argument


class Group:
    def __init__(self, name, *, title=None, description=None):
        self.name = name
        self.title = title
        self.description = description
        self.group = None

    def apply_hashbang_extension(self, cmd):
        cmd.__groups = getattr(cmd, '_Group__groups', None) or {}
        if self.name not in cmd.__groups:
            cmd.__groups[self.name] = self

    def create_group(self, parser):
        if self.group is None:
            self.group = parser.add_argument_group(
                self.title, self.description)
        return self.group


class GroupArgument(Argument):
    def __init__(self, name, *args, group=None, **kwargs):
        super().__init__(name, *args, **kwargs)
        if group is None:
            raise RuntimeError('Group name cannot be none')
        self.group = group

    def add_argument(self, cmd, parser, param):
        parser = cmd._Group__groups[self.group].create_group(parser)
        super().add_argument(cmd, parser, param)


@command(
    Group('one', title='Group #1', description='First group.'),
    Group('two', title='Group #2'),
    GroupArgument('pos1', group='one', help='First positional argument'),
    GroupArgument('pos2', group='two', help='Second positional argument'),
    GroupArgument('flag1', group='one', help='First flag', required=True),
    GroupArgument('flag2', group='two', help='Second flag'))
def main(pos1, pos2=None, *args, flag1=False, flag2=False):
    print('pos1={} pos2={} args={} flag1={} flag2={}'.format(
        *map(repr, (pos1, pos2, args, flag1, flag2))))


if __name__ == '__main__':
    main.execute()

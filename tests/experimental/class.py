#!/usr/bin/env python3

'''
$ class.py --help
> usage: class.py subcommand
>
> positional arguments:
>   subcommand

$ class.py branch --help
> usage: class.py branch [newbranch]
>
> List, create, or delete branches
>
> positional arguments:
>   newbranch

$ class.py log --help
> usage: class.py log [--graph]
>
> Show commit logs
>
> optional arguments:
>   --graph


#### ADD TESTS FOR REGULAR USAGE
'''

import functools

from hashbang import command, Argument, NoMatchingDelegate


def wrap_callable(callable_):
    '''
    Bound methods don't allow setting new attributes (and some other callables
    may have side effects when setting attributes on them). So instead we
    wrap the given callable in a regular delegating function before applying
    decorators on it.
    '''
    @functools.wraps(callable_)
    def _newfunc(*args, **kwargs):
        return callable_(*args, **kwargs)
    return _newfunc


class DecorateDuringBinding:

    def __init__(self, func, decorator):
        self.func = func
        self.decorator = decorator

    def __get__(self, obj, objtype):
        boundmethod = self.func.__get__(obj, objtype)
        return self.decorator(wrap_callable(boundmethod))

    def __call__(self, *args, **kwargs):
        return self.execute(*args, **kwargs)


def method_decorator(decorator):
    '''
    This only works if this is the outermost decorator of a class method. See
    the discussion in
    https://groups.google.com/forum/#!msg/django-developers/MCSxSkf1QE0/s768z_V2afMJ
    '''
    @functools.wraps(decorator)
    def new_decorator(func):
        return functools.update_wrapper(
            DecorateDuringBinding(func, decorator), func)
    return new_decorator


class Repo:

    def __init__(self, path):
        super().__init__()
        self.path = path

    @method_decorator(command)
    def branch(self, newbranch=None):
        '''
        List, create, or delete branches
        '''
        cmd = 'git branch'
        if newbranch is not None:
            cmd += ' ' + newbranch
        return cmd + ' on ' + self.path

    @method_decorator(command)
    def log(self, *, graph=False):
        '''
        Show commit logs
        '''
        cmd = 'git log'
        if graph:
            cmd += ' --graph'
        return cmd + ' on ' + self.path


@command.delegator
def main(subcommand, *_REMAINDER_):
    repo = Repo('/path/to/pwd')
    if subcommand == 'branch':
        repo.branch.execute(_REMAINDER_)
    elif subcommand == 'log':
        repo.log.execute(_REMAINDER_)
    else:
        raise NoMatchingDelegate()


if __name__ == '__main__':
    main.execute()

import functools
import sys


def optionalarg(decorator):
    '''
    Transforms a decorator `decorator(func, args)` into a decorator that can be
    executed both with @decorator and @decorator(args)
    '''
    @functools.wraps(decorator)
    def __decorator(*args, **kwargs):
        if len(args) == 1 and callable(args[0]) and not kwargs:
            # Execute the decorator immediately
            func = args[0]
            return decorator(func, **kwargs)
        else:
            def __impl(func):
                return decorator(func, args, **kwargs)
            return __impl

    return __decorator

import argparse
import inspect
import os
import re
import subprocess
import sys
import traceback

from collections import OrderedDict
from inspect import Parameter
from itertools import chain, islice, repeat
from pathlib import Path
from ._utils import optionalarg, log
from . import _completion


class _CommandParser(argparse.ArgumentParser):

    parse_known = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.arguments = {}

    def add_argument(self, *args, **kwargs):
        return super().add_argument(*args, **kwargs)

    def parse(self, args=None, namespace=None):
        if self.parse_known:
            return self.parse_known_args(args, namespace)
        else:
            return (self.parse_args(args, namespace), ())


@optionalarg
def command(func, mixins=(), *, prog=None):
    '''
    Usage:

    @command
    def main(arg1, *, flag1=False):
        # Do stuff
    '''
    func._command = _CommandObj(func, mixins, prog=prog)
    return func


@optionalarg
def _commanddelegator(func, mixins=(), *, prog=None):
    '''
    Usage:

    @command.delegator
    def main(arg1, *, flag1=False):
        # Do stuff


    If you are implementing a delegator, the implementation should either call
    .execute() on another command, or raise NoMatchingDelegate exception. Any
    other side-effects are undesired.
    '''
    func._command = _DelegatingCommandObj(func, mixins, prog=prog)
    return func


command.delegator = _commanddelegator


class Argument:
    '''
    Usage:

    @command
    def main(
        arg1:Argument(...),
        *,
        flag1=False):
        # Do stuff
    '''

    def __init__(
            self,
            *,
            choices=None,
            completer=None,
            aliases=(),
            help=None,
            type=None,
            remainder=False):
        self.choices = choices
        self.completer = completer
        self.aliases = aliases
        self.help = help
        self.type = type
        self.remainder = remainder

    def add_argument(self, parser, argname, param, *, partial=False):
        argument = None
        name = argname.rstrip('_')

        # Validation
        if self.remainder and param.kind is not Parameter.VAR_POSITIONAL:
            raise RuntimeError('Remainder arg "{}" must be variadic (*arg)'
                               .format(argname))

        # Add arguments
        if (param.kind is Parameter.POSITIONAL_ONLY or
                param.kind is Parameter.POSITIONAL_OR_KEYWORD):
            if param.default is Parameter.empty:
                # Most basic argument: def run(name)
                if not partial:
                    argument = parser.add_argument(
                            name,
                            choices=self.choices,
                            help=self.help,
                            type=self.type)
                else:
                    argument = parser.add_argument(
                            name,
                            nargs='?',
                            default=None,
                            choices=self.choices,
                            help=self.help,
                            type=self.type)
            else:
                # Optional argument: def run(name='foo')
                argument = parser.add_argument(
                        name,
                        nargs='?',
                        default=param.default,
                        choices=self.choices,
                        help=self.help,
                        type=self.type)
        elif param.kind is Parameter.VAR_POSITIONAL:
            if argname == '_REMAINDER_':
                self.remainder = True
            if self.remainder:
                # Special argument that will capture any remaining entries
                # in argv e.g. def run(*_REMAINDER_)
                parser.parse_known = True
            else:
                # Repeated argument: def run(*paths)
                argument = parser.add_argument(
                    name,
                    nargs='*',
                    choices=self.choices,
                    help=self.help,
                    type=self.type)
        elif param.kind is Parameter.KEYWORD_ONLY:
            names = ['--' + name]
            nonames = ['--no' + name]
            if self.aliases:
                names += [
                    ('-' if len(i) == 1 else '--') + i for i in self.aliases]
                nonames += ['--no' + i for i in self.aliases]
            if type(param.default) is bool:
                if self.choices is not None:
                    raise RuntimeError(
                            'Choices cannot be specified for boolean flag "{}"'
                            .format(argname))

                # Flag to store true or false:
                #   def run(*, wipe=True, verbose=False)
                # Generates --wipe and --nowipe
                argument = parser.add_argument(
                    *names,
                    action='store_true',
                    default=param.default,
                    dest=argname,
                    help=self.help)

                argument = parser.add_argument(
                    *nonames,
                    action='store_false',
                    dest=argname,
                    default=param.default,
                    help=argparse.SUPPRESS)
            else:
                # Capture any other keyword arguments: def run(*, arg=None)
                # e.g. prog --arg1 val1 --arg2 val2
                argument = parser.add_argument(
                    *names,
                    action='store',
                    default=param.default,
                    dest=argname,
                    choices=self.choices,
                    help=self.help,
                    type=self.type)
        else:
            raise Exception(
                'Unsupported kind of argument ' + str(param.kind))

        return argument


class _CommandObj:

    def __init__(self, func, mixins, prog=None):
        self.func = func
        self.prog = prog

        self.signature = inspect.signature(func)
        self.parser = None

        self.func.execute = self.execute

        self.mixins = mixins

    def get_parser(self, func, prog, partial, description, usage, arguments):
        '''
        Translate introspected Python function signature into argparse
        '''
        parser = _CommandParser(
            prog=prog,
            description=description,
            usage=usage,
            add_help=False)

        for name, param, argument in arguments:
            retargument = argument.add_argument(
                    parser, name, param, partial=partial)
            _completion.add_argument(argument, retargument)

        return parser

    def get_args(self, opts, remaining):
        '''
        Turns the return values from argparse.parse_args or parse_known_args
        into Python (*args, **kwargs) format.
        '''
        args = []
        kwargs = {}
        for argname, param, argument in self.arguments:
            name = argname
            value = opts.get(name, None)
            if argument.remainder:
                args.extend(remaining)
            elif (param.kind is Parameter.POSITIONAL_ONLY or
                    param.kind is Parameter.POSITIONAL_OR_KEYWORD):
                args.append(value if value is not None else param.default)
            elif param.kind is Parameter.VAR_POSITIONAL and value is not None:
                args.extend(value)
            elif value is not None:
                kwargs[argname] = value
        return (args, kwargs)

    @staticmethod
    def parse_doc(func):
        doc = inspect.getdoc(func)
        if doc is None:
            return (None, None)
        description, usage, *_ = (
                re.split('usage: ', doc, flags=re.IGNORECASE) + [None]
        )
        return (description, usage)

    def execute(self, args=None):
        return self.execute_mode(_CommandObj.exec_mode, args=args)

    def execute_mode(self, mode, args=None):
        if mode == 'execute':
            return self._execute_with_error_handling(args)
        elif mode == 'help':
            return self.help(args)
        elif mode == 'complete':
            return self.complete(args)
        else:
            raise RuntimeError('Unknown execution mode {}'.format(mode))

    def _execute_with_error_handling(self, args=None):
        try:
            try:
                import setproctitle
                setproctitle.setproctitle(sys.argv[0])
            except Exception:
                pass
            retval = self._execute_with_list(args=args)
            retval and print(retval)
            sys.exit(0)
        except (subprocess.CalledProcessError, RuntimeError) as e:
            print('Error:', str(e), file=sys.stderr)
        except NoMatchingDelegate as e:
            print(str(e), file=sys.stderr)
        except KeyboardInterrupt as e:
            print('^C', file=sys.stderr)
        sys.exit(1)

    def create_parser(self, args, partial=False):
        if self.prog is None and args is not None:
            # Try to create a sensible default for prog name
            argv = sys.argv
            argv[0] = Path(argv[0]).name
            guess_prog = ' '.join(arg for arg in argv if arg not in args)
            self.prog = guess_prog
        description, usage = _CommandObj.parse_doc(self.func)

        self.arguments = [
                (
                    argname,
                    param,
                    param.annotation
                    if param.annotation is not Parameter.empty
                    else Argument()
                )
                for argname, param in self.signature.parameters.items()]

        self.parser = self.get_parser(
                self.func,
                self.prog,
                partial,
                description,
                usage,
                self.arguments)
        return self.parser

    def execute_partial(self, args=None):
        self.create_parser(args, partial=True)
        parsed, remaining = self.parser.parse(args)
        func_args, func_kwargs = self.get_args(vars(parsed), remaining)
        func_args = [arg if arg is not Parameter.empty else None
                     for arg in func_args]
        return self.func(*func_args, **func_kwargs)

    def help(self, args):
        if self.parser is None:
            self.create_parser(args, partial=True)
        self.parser.print_help()
        self.parser.exit(100)

    def complete(self, args):
        return _completion.execute_complete(self, args)

    def _make_help_action(self, args):
        class HelpAction(argparse.Action):

            def __init__(_,
                         option_strings,
                         dest=argparse.SUPPRESS,
                         default=argparse.SUPPRESS,
                         help=None):
                super().__init__(
                    option_strings=option_strings,
                    dest=dest,
                    default=default,
                    nargs=0,
                    help=help)

            def __call__(_, parser, namespace, values, option_string=None):
                self.help(args)

        return HelpAction

    def _execute_with_list(self, args=None):
        '''
        Turns the given list of arguments (in argv format) into python
        parameters (*args, **kwargs) and run self.func
        '''

        self.create_parser(args)
        self.parser.add_argument(
                '-h', '--help',
                action=self._make_help_action(args), default=argparse.SUPPRESS,
                help='show this help message and exit')

        _completion.modify_parser(self, self.parser, args)

        parsed, remaining = self.parser.parse(
                args if args is not None else sys.argv[1:])
        func_args, func_kwargs = self.get_args(vars(parsed), remaining)
        return self.func(*func_args, **func_kwargs)


_CommandObj.exec_mode = 'execute'


class _DelegatingCommandObj(_CommandObj):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def help(self, args):
        _CommandObj.exec_mode = 'help'
        try:
            return super().execute_partial(args)
        except NoMatchingDelegate as e:
            return super().help(args)
        self.parser.exit(100)

    def complete(self, args):
        _CommandObj.exec_mode = 'complete'
        try:
            return super().execute_partial(args)
        except NoMatchingDelegate as e:
            return super().complete(args)


class NoMatchingDelegate(Exception):

    def __init__(self, msg='No matching delegate'):
        super().__init__(msg)


def subcommands(*args, **kwargs):
    if sys.version_info >= (3, 6):
        # On Python 3.6 or above, kwargs are sorted (PEP 468)
        cmds = OrderedDict(args or kwargs)
    else:
        cmds = OrderedDict(args or sorted(kwargs.items()))

    @command.delegator
    def _run(
            subcommand: Argument(choices=cmds.keys()),
            *_REMAINDER_):
        cmd = cmds.get(subcommand, None)
        if cmd is None:
            raise NoMatchingDelegate()
        return cmd.execute(_REMAINDER_)

    return _run

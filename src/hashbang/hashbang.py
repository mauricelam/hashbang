try:
    import argcomplete
except ImportError:
    argcomplete = None
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


class _CommandParser(argparse.ArgumentParser):

    parse_known = False

    def parse(self, args=None, namespace=None):
        if self.parse_known:
            return self.parse_known_args(args, namespace)
        else:
            return (self.parse_args(args, namespace), ())


class CommandSpec:
    def __init__(self, func, partial=False):
        self.func = func
        self.signature = inspect.signature(func)
        self.description, self.usage = CommandSpec.parse_doc(func)
        self.partial = partial

    def add_arguments(self, parser):
        '''
        Translate introspected Python function signature into argparse
        '''
        for argname, param in self.signature.parameters.items():
            if argname == 'self':
                continue  # Skip "self" arguments

            def add_argument(*args, **kwargs):
                '''
                Support inverted control: By adding parameter to the decorator
                and implementing the add function.

                e.g.
                class Argument:
                    def add(self, parser, argument):
                        parser.add_argument(...)

                @command(Argument('myarg'))
                def run() {
                    ...
                }
                '''
                argconfig = param.annotation

                if hasattr(argconfig, 'add_argument'):
                    argconfig.add_argument(parser, args=args, kwargs=kwargs)
                else:
                    parser.add_argument(*args, **kwargs)

            # Allow adding '_' at the end to avoid keyword collision
            name = argname.rstrip('_')
            if (param.kind is Parameter.POSITIONAL_ONLY or
                    param.kind is Parameter.POSITIONAL_OR_KEYWORD):
                if param.default is Parameter.empty:
                    # Most basic argument: def run(name)
                    if not self.partial:
                        add_argument(name)
                    else:
                        add_argument(name, nargs='?', default=None)
                else:
                    # Optional argument: def run(name='foo')
                    add_argument(name, nargs='?', default=param.default)
            elif param.kind is Parameter.VAR_POSITIONAL:
                if argname == '__rest__':
                    # Special argument that will capture any remaining entries
                    # in argv e.g. def run(*__rest__)
                    parser.parse_known = True
                else:
                    # Repeated argument: def run(*paths)
                    add_argument(name, nargs='*')
            elif param.kind is Parameter.KEYWORD_ONLY:
                if type(param.default) is bool:
                    # Flag to store true or false:
                    #   def run(*, wipe=True, verbose=False)
                    # Generates --wipe and --nowipe
                    add_argument(
                        '--' + name,
                        action='store_true',
                        default=param.default,
                        dest=argname)

                    # TODO: Need to allow Argument customization of this?
                    # (i.e. support --nof in addition to --nofile)?
                    parser.add_argument(
                        '--no' + name,
                        action='store_false',
                        dest=argname,
                        default=param.default,
                        help=argparse.SUPPRESS)
                else:
                    # Capture any other keyword arguments: def run(*, **kwargs)
                    # e.g. prog --arg1 val1 --arg2 val2
                    add_argument(
                        '--' + name,
                        action='store',
                        default=param.default,
                        dest=argname)
            else:
                raise Exception(
                    'Unsupported kind of argument ' + str(param.kind))

    def get_parser(self, prog=None):
        parser = _CommandParser(
            prog=prog,
            description=self.description,
            usage=self.usage,
            add_help=False)
        self.add_arguments(parser)
        return parser

    def get_args(self, opts, remaining):
        args = []
        kwargs = {}
        for argname, param in self.signature.parameters.items():
            if argname == 'self':
                continue
            name = argname
            value = opts.get(name, None)
            if argname == '__rest__':
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


@optionalarg
def command(func, args=(), *, prog=None):
    '''
    Usage:

    @command
    def main(arg1, *, flag1=False):
        # Do stuff
    '''
    func._command = _CommandObj(func, args, prog=prog)
    return func


@optionalarg
def _commanddelegator(func, args=(), *, prog=None):
    '''
    Usage:

    @command.delegator
    def main(arg1, *, flag1=False):
        # Do stuff


    If you are implementing a delegator, the implementation should either call
    .execute() on another command, or raise NoMatchingDelegate exception. Any
    other side-effects are undesired.
    '''
    func._command = _DelegatingCommandObj(func, args, prog=prog)
    return func


command.delegator = _commanddelegator


def prefix_filter(choices, cword):
    return [choice for choice in choices
            if choice.lower().startswith(cword.lower())]


def substring_filter(choices, cword):
    return [choice for choice in choices
            if cword.lower() in choice.lower()]


def fuzzy_path_filter(choices, cword):
    def path_match(subpath, fullpath):
        fullpath_parts = fullpath.split('/')
        return all(
            any(
                fullpath_part.lower().startswith(subpath_part.lower())
                for fullpath_part in fullpath_parts)
            for subpath_part in subpath.split('/')
        )
    # TODO: Support Windows
    return [choice for choice in choices if path_match(cword, choice)]


def completer(command, *, filter=prefix_filter):
    def _decorator(func):
        command.completer = func
        command.completion_filter = filter
        return func

    return _decorator


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

    def __init__(self, *, choices=None, completer=None, aliases=(), help=None):
        self.choices = choices
        self.completer = completer
        self.aliases = aliases
        self.help = help

    def add_argument(self, parser, args, kwargs):
        if self.aliases:
            args += tuple(
                ('-' if len(i) == 1 else '--') + i for i in self.aliases)
        if 'help' not in kwargs:
            kwargs['help'] = self.help
        if self.choices:
            kwargs['choices'] = self.choices
        argument = parser.add_argument(*args, **kwargs)
        if argcomplete is not None:
            if self.completer is not None:
                argument.completer = self.completer
            elif self.choices is not None:
                argument.completer = argcomplete.completers.ChoicesCompleter(
                        self.choices)


class _CommandObj:

    def __init__(self, func, configs, prog=None):
        self.func = func
        self.prog = prog

        self.commandspec = None
        self.parser = None

        self.unbound_func.execute = self.execute
        self.unbound_func.complete = self.complete

        for config in configs:
            config.apply(self)

    def execute(self, args=None):
        if _CommandObj.exec_mode == 'execute':
            return self.__execute(args)
        elif _CommandObj.exec_mode == 'complete':
            # subcommand propagation doesn't work for completing partial
            # queries, but included here anyway for completeness
            return self.complete(args)
        elif _CommandObj.exec_mode == 'help':
            return self.help(args)
        else:
            raise RuntimeError('Unknown mode {}'.format(_CommandObj.exec_mode))

    def __execute(self, args=None):
        try:
            try:
                import setproctitle
                setproctitle.setproctitle(sys.argv[0])
            except Exception:
                pass
            retval = self.execute_with_list(args=args)
            retval and print(retval)
            sys.exit(0)
        except (subprocess.CalledProcessError, RuntimeError) as e:
            print('Error:', str(e), file=sys.stderr)
        except NoMatchingDelegate as e:
            print(str(e), file=sys.stderr)
        except KeyboardInterrupt as e:
            print('^C', file=sys.stderr)
        sys.exit(1)

    @property
    def unbound_func(self):
        return getattr(self.func, '__func__', self.func)

    def complete(self, args):
        if argcomplete is None:
            return

        global _command_complete
        cword_prefix, debug = _command_complete

        self.create_parser(args)
        finder = argcomplete.CompletionFinder(
            argument_parser=self.parser,
            always_complete_options=False)

        active_parsers = finder._patch_argument_parser()
        parsed_args = argparse.Namespace()

        remaining = None

        finder.completing = True
        try:
            with argcomplete.mute_stderr():
                parsed_args, remaining = finder._parser.parse_known_args(
                        args, namespace=parsed_args)
        except BaseException as e:
            # argcomplete.warn(
            #         'Exception in parsing args',
            #         e,
            #         traceback.format_exc())
            pass
        finder.completing = False

        # When the arguments are unmatched (e.g. --optional without a value),
        # an exception will be thrown and remaining will be None.
        remaining = remaining or ()
        #####

        results = None
        completer = getattr(self.unbound_func, 'completer', None)
        if completer:
            func_args, func_kwargs = self.commandspec.get_args(
                    vars(parsed_args), remaining)
            func_args = [arg if arg is not Parameter.empty else None
                         for arg in func_args]
            results = completer(*func_args, **func_kwargs)
        if results is not None:
            return results
        else:
            return finder.collect_completions(
                active_parsers=active_parsers,
                parsed_args=parsed_args,
                cword_prefix=cword_prefix,
                debug=debug)

    def create_parser(self, args, partial=False):
        if self.prog is None and args is not None:
            # Try to create a sensible default for prog name
            argv = sys.argv
            argv[0] = Path(argv[0]).name
            guess_prog = ' '.join(arg for arg in argv if arg not in args)
            self.prog = guess_prog
        self.commandspec = CommandSpec(self.func, partial=partial)
        self.parser = self.commandspec.get_parser(prog=self.prog)

    def execute_partial(self, args=None):
        self.create_parser(args, partial=True)
        parsed = argparse.Namespace()
        parsed, remaining = self.parser.parse_known_args(
                args, namespace=parsed)
        func_args, func_kwargs = self.commandspec.get_args(
                vars(parsed), remaining)
        func_args = [arg if arg is not Parameter.empty else None
                     for arg in func_args]
        return self.func(*func_args, **func_kwargs)

    def help(self, args):
        if self.parser is None:
            self.create_parser(args, partial=True)
        self.parser.print_help()
        self.parser.exit(100)

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

    def execute_with_list(self, args=None):
        '''
        Turns the given list of arguments (in argv format) into python
        parameters (*args, **kwargs) and run self.func
        '''

        # Defer CommandSpec initialization until command execution
        # (lazy loading!)
        self.create_parser(args)
        self.parser.add_argument(
                '-h', '--help',
                action=self._make_help_action(args), default=argparse.SUPPRESS,
                help='show this help message and exit')

        if argcomplete is not None:
            _command = self
            completion_filter = getattr(
                    self.unbound_func, 'completion_filter', prefix_filter)

            class CompletionFinder(argcomplete.CompletionFinder):
                def _get_completions(
                        self,
                        comp_words,
                        cword_prefix,
                        cword_prequote,
                        first_colon_pos):
                    '''
                    Intercept argcomplete and allow attaching our own
                    completers (which can be attached to functions in addition
                    to arguments)
                    '''
                    try:
                        global _command_complete
                        _command_complete = (cword_prefix, (lambda *_: None))

                        choices = _command.complete(
                                args if args is not None else comp_words[1:])
                        completions = list(completion_filter(
                                choices, cword_prefix))
                        completions = self.filter_completions(completions)
                        completions = self.quote_completions(
                                completions, cword_prequote, first_colon_pos)

                        _command_complete = None

                        return completions
                    except BaseException as e:
                        argcomplete.warn(e, traceback.print_exc())

            CompletionFinder()(
                    self.parser,
                    exclude=['--help', '-h'],
                    always_complete_options=False)

        parsed, remaining = self.parser.parse(
                args if args is not None else sys.argv[1:])
        func_args, func_kwargs = self.commandspec.get_args(
                vars(parsed), remaining)
        return self.func(*func_args, **func_kwargs)


_CommandObj.exec_mode = 'execute'


class _DelegatingCommandObj(_CommandObj):

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


def MasterCommand(**kwargs):
    '''
    Can probably deprecate this once the syntax is polished nicer
    '''

    @command.delegator
    def _run(
            subcommand: Argument(choices=kwargs.keys()),
            *__rest__):
        try:
            return kwargs[subcommand].execute(__rest__)
        except KeyError:
            raise NoMatchingDelegate()

    # Fill in the subcommand as the prog name so the help message shows the
    # correct prog name
    for key, subcommand in kwargs.items():
        subcommand._command.prog = '{} {}'.format(
                _run._command.prog or Path(sys.argv[0]).name, key)

    return _run._command

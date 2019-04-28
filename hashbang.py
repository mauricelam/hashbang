try:
    import argcomplete
except ImportError:
    argcomplete = None
import argparse
import functools
import inspect
import os
import re
import subprocess
import sys
import traceback

from collections import OrderedDict
from pathlib import Path
from itertools import chain, islice, repeat


def optionalarg(decorator):
    '''
    Transforms a decorator `decorator(func, args)` into a decorator that can be
    executed both with @decorator and @decorator(args)
    '''
    @functools.wraps(decorator)
    def __decorator(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            # Execute the decorator immediately
            func = args[0]
            return decorator(func, **kwargs)
        else:
            def __impl(func):
                return decorator(func, args, **kwargs)
            return __impl

    return __decorator


def log(*objects, **kwargs):
    if log.verbose:
        print(*objects, file=log.file, **kwargs)


log.verbose = False
log.file = sys.stderr


class CommandParser(argparse.ArgumentParser):

    parse_known = False

    def parse(self, args=None, namespace=None):
        if self.parse_known:
            return self.parse_known_args(args, namespace)
        else:
            return (self.parse_args(args, namespace), ())


class CommandSpec:
    def __init__(self, func, arguments=None, partial=False):
        self.func = func
        self.signature = Signature.inspect(func)
        self.description, self.usage, self.param_docs = CommandSpec.parse_doc(func)
        self.arguments = arguments or {}
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
                if not hasattr(argconfig, 'add_argument'):
                    argconfig = self.arguments.get(argname)

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
        parser = CommandParser(
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
            name = argname.rstrip('_')
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
            return (None, None, {})
        description, usage, *_ = (
                re.split('usage: ', doc, flags=re.IGNORECASE) + [None]
        )
        # TODO: parse and provide parameter docs
        return (description, usage, {})


@optionalarg
def command(func, args=(), *, prog=None):
    '''
    Usage:

    @command
    def main(arg1, *, flag1=False):
        # Do stuff
    '''
    func._command = CommandObj(func, args, prog=prog)
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
    func._command = DelegatingCommandObj(func, args, prog=prog)
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

    def __init__(self, name=None, *, choices=None, completer=None, aliases=()):
        # Name is only necessary for the config type (i.e. as a parameter in
        # @command)
        self.name = name
        self.choices = choices
        self.completer = completer
        self.aliases = aliases

    def apply(self, command):
        command.arguments[self.name] = self

    def add_argument(self, parser, args, kwargs):
        if self.aliases:
            args += tuple(
                ('-' if len(i) == 1 else '--') + i for i in self.aliases)
        if 'help' not in kwargs:
            kwargs['help'] = ('<{}>'.format('|'.join(self.choices))
                              if self.choices else None)
        argument = parser.add_argument(*args, **kwargs)
        if argcomplete is not None:
            if self.completer is not None:
                argument.completer = self.completer
            elif self.choices is not None:
                argument.completer = argcomplete.completers.ChoicesCompleter(
                        self.choices)


class ArgumentDict(dict):

    def __missing__(self, key):
        self[key] = Argument(key)
        return self[key]


class CommandObj:

    def __init__(self, func, configs, prog=None):
        self.func = func
        self.arguments = ArgumentDict()
        self.prog = prog

        self.commandspec = None
        self.parser = None

        self.unbound_func.execute = self.execute
        self.unbound_func.complete = self.complete
        self.unbound_func.arguments = self.arguments

        for config in configs:
            config.apply(self)

    def execute(self, args=None):
        if CommandObj.exec_mode == 'execute':
            return self.__execute(args)
        elif CommandObj.exec_mode == 'complete':
            # subcommand propagation doesn't work for completing partial
            # queries, but included here anyway for completeness
            return self.complete(args)
        elif CommandObj.exec_mode == 'help':
            return self.help(args)
        else:
            raise RuntimeError('Unknown mode {}'.format(CommandObj.exec_mode))

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
        except subprocess.CalledProcessError as e:
            print('Error:', str(e), file=sys.stderr)
        except RuntimeError as e:
            print('Error:', str(e), file=sys.stderr)
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

        self.create_parser()
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

    def create_parser(self, partial=False):
        self.commandspec = CommandSpec(
                self.func,
                arguments=self.arguments,
                partial=partial)
        self.parser = self.commandspec.get_parser(prog=self.prog)

    def execute_partial(self, args=None):
        self.create_parser(partial=True)
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
            self.create_parser(partial=True)
        self.parser.print_help()
        self.parser.exit(100)

    def _make_help_action(self, args):
        class HelpAction(argparse.Action):

            def __init__(_, option_strings,
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
        self.create_parser()
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


CommandObj.exec_mode = 'execute'


class DelegatingCommandObj(CommandObj):

    def help(self, args):
        CommandObj.exec_mode = 'help'
        try:
            return super().execute_partial(args)
        except NoMatchingDelegate as e:
            return super().help(args)
        self.parser.exit(100)

    def complete(self, args):
        CommandObj.exec_mode = 'complete'
        try:
            return super().execute_partial(args)
        except NoMatchingDelegate as e:
            return super().complete(args)


class NoMatchingDelegate(Exception):

    def __str__(self):
        return 'No matching delegate'


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


# SIGNATURE BLOCK


class Atom:
    def __init__(self, description='Atom'):
        self.description = description

    def __eq__(self, other):
        return self is other

    def __str__(self):
        return self.description


class Parameter:
    empty = Atom('empty parameter')

    POSITIONAL_ONLY = Atom('positional_only')
    POSITIONAL_OR_KEYWORD = Atom('positional_or_keyword')
    VAR_POSITIONAL = Atom('var_positional')
    KEYWORD_ONLY = Atom('keyword_only')
    VAR_KEYWORD = Atom('var_keyword')

    def __init__(self, name, kind, *, default=empty, annotation=empty):
        self.name = name
        self.kind = kind
        self.default = default
        self.annotation = annotation


class Signature:
    empty = Atom('empty annotation')

    def __init__(self, parameters=None, *, return_annotation=empty):
        self.parameters = parameters
        self.return_annotation = return_annotation

    @staticmethod
    def inspect(func):
        args, varargs, varkw, \
                defaults, kwonlyargs, \
                kwonlydefaults, annotations = inspect.getfullargspec(func)
        defaults = defaults or []
        kwonlydefaults = kwonlydefaults or {}
        parameters = OrderedDict()
        for arg, default in _zipright(args, defaults, filler=Parameter.empty):
            parameters[arg] = Parameter(
                    arg,
                    Parameter.POSITIONAL_OR_KEYWORD,
                    default=default,
                    annotation=annotations.get(arg, Parameter.empty))
        if varargs:
            parameters[varargs] = Parameter(
                    varargs,
                    Parameter.VAR_POSITIONAL,
                    annotation=annotations.get(varargs, Parameter.empty))
        for arg in kwonlyargs:
            # Iterate on kwonlyargs because it is ordered
            default = kwonlydefaults[arg]
            parameters[arg] = Parameter(
                    arg,
                    Parameter.KEYWORD_ONLY,
                    default=default,
                    annotation=annotations.get(arg, Parameter.empty))
        if varkw:
            parameters[varkw] = Parameter(
                    varkw,
                    Parameter.VAR_KEYWORD,
                    annotation=annotations.get(varkw, Parameter.empty))
        return Signature(parameters)


# UTILS BLOCK


def _zipright(seq1, seq2, filler=None):
    '''
    Zips seq1 and seq2 together. If seq1 and seq2 have different lengths, the
    shorter one will be padded on the left side before zipping.
    '''
    maxlen = max(len(seq1), len(seq2))
    return zip(
            chain(([filler] * (maxlen - len(seq1))), seq1),
            chain(([filler] * (maxlen - len(seq2))), seq2))

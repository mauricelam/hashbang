import argparse
import functools
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
from ._utils import optionalarg
from . import completion

__all__ = [
    'command',
    'Argument',
    'NoMatchingDelegate',
    'subcommands',
]


class _CommandParser(argparse.ArgumentParser):

    parse_known = False
    delegation = False

    def add_argument(self, *args, **kwargs):
        return super().add_argument(*args, **kwargs)

    def parse(self, args=None, namespace=None):
        if self.parse_known:
            return self.parse_known_args(args, namespace)
        else:
            return (self.parse_args(args, namespace), ())

    def error(self, message):
        if self.delegation:
            raise NoMatchingDelegate()
        else:
            super().error(message)


@optionalarg
def command(func, extensions=(), **kwargs):
    '''
    A decorator to add command line parsing functionality to the function. The
    returned function is the same as the original one, but with the `execute`
    function added to it. Usage example:

    ```python3
    @command
    def main(arg1, *, flag1=False):
        # Do stuff
    ```

    Arguments are added according to the parameters of the wrapped function:

    -   Positional parameters, which are any parameter before `*` or `*args` in
        the argument list, are interpreted as positional arguments in the
        parser.
        These arguments can be required if the default values are omitted
        (`def func(arg)`), or optional if a default value is provided
        (`def func(arg=None)`).
    -   Variadic parameters, which are parameters in the form `*args`, are
        interpreted as a list argument which will take all the remaining
        position arguments when parsing from command line.
        A special case is when the argument is named `_REMAINDER_`, or if
        `Argument(remainder=True)` is specified. In which case, this argument
        will be a sequence capturing all remaining arguments, including
        optional ones (e.g. `--foo`).
    -   Keyword parameters, which are any parameter after `*` or `*args` in the
        argument list, are interpreted as optional arguments, or sometimes
        known as flags. By default the argument name is taken as the flag name,
        with any trailing underscores (`_`) stripped out. For example, if the
        parameter name is `foo`, the flag name is `--foo`.

        The action of the flag varies by the type of the default value. If the
        default value is `False`, the action will be `argparse`'s `store_true`,
        which means the parameter's value will be `True` if `--foo` is
        specified, or `False` otherwise. Similarly, if the default value is
        `True`, the parameter value will be `True` unless `--nofoo` is
        specified. If the default value is not a bool, optional argument value
        will be assigned to the parameter. For example, `--foo bar` will set
        the value of `foo` to `bar`.

    ```python3
    <main>.execute(args=None)
    ```

    The `execute` method is also added to the decorated function, so it can be
    run using `func.execute()`. This method will execute the decorated function
    with the given command line arguments in `args`, or in `sys.argv` if `args`
    is `None`.

    ### API

    ```python3
    @command(*extensions,
             prog=None, formatter_class=None, allow_abbrev=True,
             return_value_processor=None, exception_handler=None)
    ```

    #### Keyword arguments parsed to `argparse.ArgumentParser()`
    -   `prog` - The program name as a string. This is used in the usage and
        help messages.
    -   `formatter_class` - Formatter for the help message, which controls
        behaviors like dedenting and string wrapping. See
        [`argparse`](https://docs.python.org/3/library/argparse.html#formatter-class)
        for details.
    -   `allow-abbrev` - (Python 3.5 or above only) Allows long options to be
        abbreviated if the abbreviation is unambiguous. Default is `True`. When
        this is `True`, the parser will perform a prefix match on flags, and if
        there is only one match it will be treated as the flag. For example, in
        the function `def main(*, foo, bar, baz)`, `--f` will match `--foo`,
        whereas `--ba` will raise an exception.

    #### Other keyword arguments
    -   `return_value_processor` - A callable that takes the return value of
        the decorated function and processes it. When this is `None`, the
        default implementation is used, which is to `print()` the result to
        stdout.

    ```python3
    def _default_return_value_processor(val):
        if val is not None:
            print(val)
    ```

    -   `exception_handler` - A callable that takes the exception raised by the
        decorated function and processes it. This method should re-raise any
        exceptions it does not handle. When this is `None`, the default
        implementation is used, which is to handle
        `subprocess.CalledProcessError`, `NoMatchingDelegate`, and
        `KeyboardInterrupt` to print the error messages instead of printing the
        entire stack trace.

    ```python3
    def _default_exception_handler(exception):
        try:
            raise exception
        except (subprocess.CalledProcessError, RuntimeError) as e:
            print('Error:', str(e), file=sys.stderr)
        except NoMatchingDelegate as e:
            print(str(e), file=sys.stderr)
        except KeyboardInterrupt as e:
            print('^C', file=sys.stderr)
    ```

    #### Using extensions

    `@command` can also optionally take extensions as positional arguments, and
    keyword arguments to customize the `HashbangCommand` or the parser. See
    [Extensions](https://github.com/mauricelam/hashbang/wiki/Extensions) and
    documentation for `HashbangCommand` below for more.

    ```python3
    @command(
        Argument('arg', choices=('one', 'two')),
        exception_handler=handle_exception)
    def main(arg, *, flag=False):
        # Do stuff
    ```
    '''
    cmd = HashbangCommand(func, extensions, **kwargs)
    func._hashbang_command = cmd
    func.execute = cmd.execute
    return func


@optionalarg
def _commanddelegator(func, extensions=(), **kwargs):
    '''
    `@command.delegator` works the same way as a `@command`, but when `--help`
    or tab-completion is invoked, instead of running its own help or completion
    methods immediately, it will first try to delegate to a subcommand, so that
    a command like `git branch --help` will show the help page of `git branch`,
    not `git` itself.

    When implementing a delegator, the implementation must either call
    `.execute()` on another command, or raise NoMatchingDelegate exception. Any
    other side-effects, like printing to the terminal or writing to any files,
    are undesired.

    Also see the `subcommands` function which will is a convenience function to
    create delegating commands based on key-value pairs.
    '''
    cmd = _DelegatingHashbangCommand(func, extensions, **kwargs)
    func._hashbang_command = cmd
    func.execute = cmd.execute
    return func


command.delegator = _commanddelegator


class _StoreBooleanAction(argparse.Action):
    '''
    Same as argparse's store_const, but includes an extra "type" argument. This
    is useful when set_defaults is used, where if the default is provided as a
    string, it will pass through "type" to parse the value.
    '''

    def __init__(self,
                 option_strings,
                 dest,
                 const,
                 default=None,
                 required=False,
                 help=None,
                 metavar=None):
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            const=const,
            nargs=0,
            default=default,
            required=required,
            type=lambda x: x == 'True',
            help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, self.const)


class _StoreTrueAction(_StoreBooleanAction):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, const=True, **kwargs)


class _StoreFalseAction(_StoreBooleanAction):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, const=False, **kwargs)


class Argument:
    '''
    The `Argument` class allows additional configurations to be added to the
    argument. It can be added in one of the following two ways:

    1. As decorator parameter
    ```python3
    @command(
        Argument('arg', choices=('one', 'two')),
        Argument('flag', aliases=('f', 'F')))
    def main(arg, *, flag):
        # Do stuff
    ```

    As many arguments as needed can be added to the `@command` decorator, in
    any order. Just ensure that the first argument of `Argument` matches the
    name of the function parameter.

    2. As argument annotation, as defined in
       [PEP 3107](https://www.python.org/dev/peps/pep-3107/).
    ```python3
    def main(
            arg: Argument(choices=('one', 'two')),
            *,
            flag: Argument(aliases=('f', 'F'))):
        # Do stuff
    ```

    There is no behavioral difference between these two ways in hashbang. I
    find the second way to be slightly more pleasing to the eye and reduces
    repetition, but it may go away in future versions of Python from
    [PEP 563](https://www.python.org/dev/peps/pep-0563/#non-typing-usage-of-annotations).
    Hence the first way is also provided, and is the encouraged way to specify
    `Argument` configurations.

    ```python3
    Argument(name=None, *, choices=None, completer=None, aliases=(),
             append=False, help=None, type=None, required=False,
             remainder=False)
    ```
    -   `name` - The name of the argument. This is required when using
        `Argument` as a parameter to `@command`, and it must match the name of
        a parameter in the decorated function. When using `Argument` as an
        argument annotation, `name` should be omitted, and will be ignored if
        specified.
    -   `choices` - A sequence of strings that corresponds to the possible
        values of the argument. This is used in both the help message and in
        tab completion.
    -   `completer` - A callable with the keyword arguments `prefix`, `action`,
        `parser`, and `parsed_args`. This callable should return a list of
        possible completion values. This is only used in tab-completion.
        -   `prefix`: The prefix text of the last word before the cursor on the
            command line. For dynamic completers, this can be used to reduce
            the work required to generate possible completions.
        -   `action`: The `argparse.Action` instance that this completer was
            called for.
        -   `parser`: The `argparse.ArgumentParser` instance that the action
            was taken by.
        -   `parsed_args`: The result of argument parsing so far (the
            `argparse.Namespace` args object normally returned by
            `ArgumentParser.parse_args()`).
    -   `completion_validator` - A callable that takes
        `(current_input, keyword_to_check_against)` and returns a boolean
        indicating whether `keyword_to_check_against` should be part of the
        completion. `current_input` is the partial word that the user tabbed
        on. `keyword_to_check_against` is one of the choices or output from
        `completer`. The default validator performs a simple prefix match.
    -   `aliases` - A sequence of strings that are aliases of this argument.
        This is only applicable to optional arguments. For example, if an
        argument `foobar` has aliases `('f', 'eggspam')`, then `--foobar`,
        `-f`, and `--eggspam` will all do the same thing. Notice that if an
        alias is only one character, only one dash is added before it.
    -   `append` - Whether to append the given arguments to a list instead of
        overwriting the value. For example, `--val foobar --val eggspam` will
        create the value `val=['foobar', 'eggspam']`. The default value of this
        argument should be empty tuple `()` in most typical cases. Non-empty
        default values are not allowed to avoid the surprising behavior
        described in https://bugs.python.org/issue16399.
    -   `help` - The string help message for this argument.
    -   `type` - A callable takes a single string input from command line, and
        returns the converted value. A common usage is to use `int` or `float`
        to convert to the desired type. `argparse.FileType` can also be used
        here. This can also be used to validate the input, but raising an
        exception if the input doesn't match expectations.
    -   `required` - Whether the argument is required. This is applicable only
        to optional arguments. For boolean flags, you will need to specify
        either `--flag` or `--noflag` in the command line. For other flags, you
        must provide a value like `--foo bar`.
    -   `remainder` - Boolean indicating whether this is argument should
        capture all remainders from command line, including unparsed optional
        arguments. This is applicable only to the var positional argument
        `*arg`. Default value is `False`, unless the argument is named
        `_REMAINDER_`, in which case remainder is `True`.
    '''

    def __init__(
            self,
            name=None,
            *,
            choices=None,
            completer=None,
            completion_validator=None,
            aliases=(),
            append=False,
            help=None,
            type=None,
            required=False,
            remainder=False):
        self.name = name
        self.choices = choices
        self.completer = completer
        self.aliases = aliases
        self.help = help
        self.type = type
        self.remainder = remainder
        self.required = required
        self.completion_validator = completion_validator
        self.append = append

    def add_argument(self, cmd, arg_container, param):
        '''
        ```python3
        Argument.add_argument(cmd, arg_container, param)
        ```

        -   `cmd` - The `HashbangCommand` object using this argument. This can
            be used as a vector for communication across extension instances,
            or to retrieve values set in the prior call to
            `apply_hashbang_command`. For example, an argument group can be
            placed in the command object, and multiple arguments can be added
            to the same argument group. Any fields added by the argument to
            this `HashbangCommand` should be prefixed with `_ClassName__` to
            avoid namespace collision.
        -   `arg_container` - The argument container, which can be an
            `argparse.ArgumentParser`, or the returned group of
            `ArgumentParser.add_argument_group()` or
            `ArgumentParser.add_mutually_exclusive_group()`. The argument
            implementation should call
            [`add_argument`](https://docs.python.org/3/library/argparse.html#the-add-argument-method)
            on this parameter.
        -   `param` - The `inspect.Parameter` object describing the parameter
            in the Python function. This can be `None` for arguments added by
            extensions, but is guaranteed to not be `None` for regular
            arguments.
        '''
        argument = None
        name = param.name.rstrip('_')

        # Validation
        if self.remainder and param.kind is not Parameter.VAR_POSITIONAL:
            raise RuntimeError('Remainder arg "{}" must be variadic (*arg)'
                               .format(param.name))
        if self.required and param.kind is not Parameter.KEYWORD_ONLY:
            raise RuntimeError(
                '"required" does not apply to positional arguments. Specify a '
                'default value if you want optional positional args.\n'
                'e.g. def func(foo=123)')

        # Add arguments
        if (param.kind is Parameter.POSITIONAL_ONLY or
                param.kind is Parameter.POSITIONAL_OR_KEYWORD):
            if param.default is Parameter.empty:
                # Most basic argument: def run(name)
                argument = arg_container.add_argument(
                        param.name,
                        metavar=name if not self.choices else None,
                        nargs=None,
                        default=None,
                        choices=self.choices,
                        help=self.help,
                        type=self.type)
            else:
                # Optional argument: def run(name='foo')
                argument = arg_container.add_argument(
                        param.name,
                        metavar=name if not self.choices else None,
                        nargs='?',
                        default=param.default,
                        choices=self.choices,
                        help=self.help,
                        type=self.type)
        elif param.kind is Parameter.VAR_POSITIONAL:
            if param.name == '_REMAINDER_':
                self.remainder = True
            if self.remainder:
                # Special argument that will capture any remaining entries
                # in argv e.g. def run(*_REMAINDER_)
                arg_container.parse_known = True
            else:
                # Repeated argument: def run(*paths)
                argument = arg_container.add_argument(
                    param.name,
                    metavar=name if not self.choices else None,
                    nargs='*',
                    choices=self.choices,
                    help=self.help,
                    type=self.type)
        elif param.kind is Parameter.KEYWORD_ONLY:
            names = self.get_flag_names(name)
            nonames = self.get_negative_flag_names(name)
            if type(param.default) is bool:
                if self.choices is not None:
                    raise RuntimeError(
                            'Choices cannot be specified for boolean flag "{}"'
                            .format(param.name))

                flag_arg_container = arg_container
                if self.required:
                    flag_arg_container = \
                        arg_container.add_mutually_exclusive_group(
                            required=self.required)

                # Flag to store true or false:
                #   def run(*, wipe=True, verbose=False)
                # Generates --wipe and --nowipe
                argument = flag_arg_container.add_argument(
                    *names,
                    action=_StoreTrueAction,
                    default=param.default,
                    dest=param.name,
                    help=self.help)

                argument = flag_arg_container.add_argument(
                    *nonames,
                    action=_StoreFalseAction,
                    dest=param.name,
                    default=param.default,
                    help=argparse.SUPPRESS)
            else:
                if self.append and len(param.default) > 0:
                    raise RuntimeError(
                        'When "append" is true, the default value of the '
                        'argument must be empty to avoid the surprising '
                        'behavior described in '
                        'https://bugs.python.org/issue16399.\n'
                        'Instead, use `arg = arg or ("default value")` in '
                        'your implementation.')
                # Capture any other keyword arguments: def run(*, arg=None)
                # e.g. prog --arg1 val1 --arg2 val2
                argument = arg_container.add_argument(
                    *names,
                    action='store' if not self.append else 'append',
                    # For append arguments, argparse calls append() directly
                    # on the default, so make sure we don't reuse the default
                    # value, and convert to list to allow tuples as defaults
                    default=(param.default if not self.append
                             else list(param.default)),
                    dest=param.name,
                    choices=self.choices,
                    help=self.help,
                    type=self.type,
                    required=self.required)
        else:
            raise Exception(
                'Unsupported kind of argument ' + str(param.kind))

        return argument

    def get_flag_names(self, name):
        '''
        Return a list of names to use when this argument is used as flags.
        '''
        return ['--' + name] + [('-' if len(i) == 1 else '--') + i
                                for i in self.aliases]

    def get_negative_flag_names(self, name):
        '''
        Return a list of negative names to use when this argument is used as a
        boolean flag. The default implementation adds the prefix 'no' to the
        name and all aliases
        '''
        return ['--no' + name] + ['--no' + i for i in self.aliases]

    def apply_hashbang_extension(self, cmd):
        if self.name is None:
            raise RuntimeError('Name must be defined for Argument used in '
                               'decorators')
        cmd.arguments[self.name] = (
                cmd.signature.parameters[self.name], self)


def _default_return_value_processor(val):
    if val is not None:
        print(val)


def _default_exception_handler(exception):
    try:
        raise exception
    except (subprocess.CalledProcessError, RuntimeError) as e:
        print('Error:', str(e), file=sys.stderr)
    except NoMatchingDelegate as e:
        print(str(e), file=sys.stderr)
    except KeyboardInterrupt as e:
        print('^C', file=sys.stderr)


class HashbangCommand:
    '''
    When a function is decorated with `@command`, a `HashbangCommand` is
    created to inspect its function signature, generating the parser, and
    eventually executing the parsing. Its operations are transparent to the
    regular user, but its APIs are useful for developing extensions.

    `HashbangCommand` has the following attributes which extensions can use
    to customize the command's behavior:
    -   `arguments` - An ordered dictionary of the arguments to add to the
        `argparse` parser. The order of the arguments should match the order
        in which they are declared in the function. The order is preserved in
        the help message.

        The keys of the map are the function names, whereas the values are a
        pair `(param, argument)`. `param` is the `inspect.Parameter` object,
        which can be `None` if the argument doesn't correspond to any parameter
        (i.e. injected by an extension). `argument` is an instance of
        `Argument` which is responsible for calling `add_argument` to the
        `argparse` parser.
    -   `argparse_kwargs` - a dict of keyword arguments to add to the
        constructor `argparse.ArgumentParser`.
    -   `return_value_processor` - A callable that takes the return value of
        the decorated function and processes it. When this is `None`, the
        default implementation is used, which is to `print()` the result to
        stdout.
    -   `exception_handler` - A callable that takes the exception raised by the
        decorated function and processes it. This method should re-raise any
        exceptions it does not handle. When this is `None`, the default
        implementation is used, which is to handle
        `subprocess.CalledProcessError`, `NoMatchingDelegate`, and
        `KeyboardInterrupt` to print the error messages instead of printing the
        entire stack trace.
    -   `default_values` - A dictionary of default values to be used, if the
        user did not supply a corresponding value from command line. To ensure
        extension operability, you should update or insert the dictionary with
        your values, rather than replacing the entire dictionary.

    In addition, the following read-only fields are also available to allow
    extensions to get context on the function this command is running on:
    -   `func` - The decorated function
    -   `signature` - The `inspect.Signature` object created by inspecting
        `func`.
    -   `extensions` - The list of extensions applied to this command.

    ### Implementing an extension

    Extensions are regular objects implementing the function
    `apply_hashbang_extension(hashbang_cmd)`. This function is called after
    all the information from the decorated function has been gathered,
    before creating the `argparse.ArgumentParser`. Extensions are expected to
    modify one the of attributes described above to modify the behavior of the
    command.
    '''

    def __init__(self, func, extensions=(), **kwargs):
        # Read only by extensions (not enforced)
        self.func = func
        self.signature = inspect.signature(func)
        self.parser = None
        self.extensions = extensions

        # Modifiable by extensions
        self.arguments = OrderedDict()
        self.argparse_kwargs = {}
        self.default_values = {}

        # Modifiable by extensions and via kwargs
        self.return_value_processor = _default_return_value_processor
        self.exception_handler = _default_exception_handler

        for key, value in kwargs.items():
            if key in ['prog', 'formatter_class', 'allow_abbrev']:
                self.argparse_kwargs[key] = value
            elif (key in ['return_value_processor', 'exception_handler']
                    and hasattr(self, key)):
                setattr(self, key, value)
            else:
                raise RuntimeError(
                    'Command property "{}" cannot be set'.format(key))

    def _get_args(self, opts, remaining):
        '''
        Turns the return values from argparse.parse_args or parse_known_args
        into Python (*args, **kwargs) format.
        '''
        args = []
        kwargs = {}
        for argname, (param, argument) in self.arguments.items():
            if param is None:
                # Ignore params that doesn't exist in the signature (added by
                # extensions)
                continue
            value = opts.get(argname, None)
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

    def execute(self, args=None):
        return self._execute_mode(HashbangCommand.exec_mode, args=args)

    def _execute_mode(self, mode, args=None):
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
            return_value = self._execute_with_list(args=args)
            self.return_value_processor(return_value)
            sys.exit(0)
        except BaseException as e:
            self.exception_handler(e)
        sys.exit(1)

    def _create_parser(self, args, delegation=False):
        if 'prog' not in self.argparse_kwargs and args is not None:
            # Try to create a sensible default for prog name
            argv = sys.argv
            argv[0] = Path(argv[0]).name
            guess_prog = ' '.join(arg for arg in argv
                                  if arg not in (list(args) + ['--']))
            self.argparse_kwargs['prog'] = guess_prog

        # Parse the description and usage from the docstring
        doc = inspect.getdoc(self.func)
        if doc is None:
            description, usage = (None, None)
        else:
            description, usage, *_ = (
                    re.split('usage:', doc, flags=re.IGNORECASE) + [None]
            )
            usage = usage.lstrip() if usage else None

        self.arguments = OrderedDict(
            (param.name, (
                param,
                param.annotation if isinstance(param.annotation, Argument)
                else Argument()))
            for _, param in self.signature.parameters.items())

        for extension in self.extensions:
            if not callable(getattr(extension, 'apply_hashbang_extension')):
                raise RuntimeError(
                    'extensions passed in @command must implement the method '
                    '"apply_hashbang_extension"')
            extension.apply_hashbang_extension(self)

        self.parser = _CommandParser(
            description=description,
            usage=usage,
            add_help=False,
            **self.argparse_kwargs)
        self.parser.delegation = delegation

        for name, (param, argument) in self.arguments.items():
            retargument = argument.add_argument(self, self.parser, param)
            completion._add_argument(argument, retargument)

        self.parser.set_defaults(**self.default_values)

        return self.parser

    def _execute_delegation(self, args=None):
        self._create_parser(args, delegation=True)
        parsed, remaining = self.parser.parse(args)
        func_args, func_kwargs = self._get_args(vars(parsed), remaining)
        func_args = [arg if arg is not Parameter.empty else None
                     for arg in func_args]
        return self.func(*func_args, **func_kwargs)

    def help(self, args):
        if self.parser is None:
            self._create_parser(args, delegation=True)
        self.parser.print_help()
        self.parser.exit(0)

    def complete(self, args):
        return completion._execute_complete(self, args)

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

        self._create_parser(args)
        self.parser.add_argument(
                '-h', '--help',
                action=self._make_help_action(args), default=argparse.SUPPRESS,
                help='show this help message and exit')

        completion._modify_parser(self, self.parser, args)

        parsed, remaining = self.parser.parse(
                args if args is not None else sys.argv[1:])
        func_args, func_kwargs = self._get_args(vars(parsed), remaining)
        return self.func(*func_args, **func_kwargs)


HashbangCommand.exec_mode = 'execute'


class _DelegatingHashbangCommand(HashbangCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def help(self, args):
        HashbangCommand.exec_mode = 'help'
        try:
            return super()._execute_delegation(args)
        except NoMatchingDelegate as e:
            return super().help(args)
        raise RuntimeError('Delegate command should call sys.exit')

    def complete(self, args):
        HashbangCommand.exec_mode = 'complete'
        try:
            return super()._execute_delegation(args)
        except NoMatchingDelegate as e:
            return super().complete(args)


class NoMatchingDelegate(Exception):
    '''
    An exception that should be raised when implementing a `@command.delegator`
    when a matching delegator could not be found.
    '''

    def __init__(self, msg='No matching delegate'):
        super().__init__(msg)


def subcommands(*args, **kwargs):
    '''
    A convenience method to create a `@command.delegator` that delegates using
    the given keyword arguments or pairs. For example, using
    `git = subcommands(commit=commit_func, branch=branch_func)`, a parent
    command "git" with "commit" and "branch" subcommands are created. When
    `git.py commit` is executed, it will call `commit_func.execute(...)` with
    all the remaining arguments. `commit_func` and `branch_func` should also be
    a `@command`.
    '''

    if sys.version_info >= (3, 6):
        # On Python 3.6 or above, kwargs are sorted (PEP 468)
        cmds = OrderedDict(args or kwargs)
    else:
        # On lower versions, kwargs are unordered, so we just sort them by
        # natural order to keep the order predictable
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

try:
    import argcomplete
except ImportError:
    argcomplete = None

import argparse
import os
import sys
import traceback
from inspect import Parameter


def add_argument(argument, argparse_argument):
    if argcomplete is not None:
        if argument.completer is not None:
            argparse_argument.completer = argument.completer
        elif argument.choices is not None:
            # Cannot use argparse's built in choices, since we may be parsing
            # partial arguments in completion mode
            argparse_argument.completer = (
                    argcomplete.completers.ChoicesCompleter(argument.choices))


def execute_complete(commandobj, args):
    if argcomplete is None:
        return

    global _command_complete
    cword_prefix, debug = _command_complete

    parser = commandobj.create_parser(args)
    finder = argcomplete.CompletionFinder(
        argument_parser=parser,
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
    completer = getattr(commandobj.func, 'completer', None)
    if completer:
        func_args, func_kwargs = commandobj.get_args(
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


def modify_parser(commandobj, parser, args):
    if argcomplete is not None:
        completion_filter = getattr(
                commandobj.func, 'completion_filter', prefix_filter)

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

                    choices = commandobj.complete(
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

        CompletionFinder(parser)(
                parser,
                output_stream=(sys.stdout.buffer
                               if os.getenv('_COMPLETE_TO_STDOUT') == '1'
                               else None),
                exclude=['--help', '-h'],
                always_complete_options=False)


def prefix_filter(choices, cword):
    return [choice for choice in choices
            if choice.lower().startswith(cword.lower())]


def substring_filter(choices, cword):
    return [choice for choice in choices
            if cword.lower() in choice.lower()]


def fuzzy_path_filter(choices, cword):
    def path_match(subpath, fullpath):
        fullpath_parts = fullpath.split(os.sep)
        return all(
            any(
                fullpath_part.lower().startswith(subpath_part.lower())
                for fullpath_part in fullpath_parts)
            for subpath_part in subpath.split(os.sep)
        )
    return [choice for choice in choices if path_match(cword, choice)]


def completer(command, *, filter=prefix_filter):
    def _decorator(func):
        command.completer = func
        command.completion_filter = filter
        return func

    return _decorator

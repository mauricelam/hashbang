try:
    import argcomplete
except ImportError:
    argcomplete = None

import argparse
import os
import sys
import traceback
from inspect import Parameter

__all__ = [
    'prefix_validator',
    'fuzzy_path_validator'
]


def _add_argument(argument, argparse_argument):
    if argcomplete is not None:
        completer = argument.completer
        if completer is None and argument.choices is not None:
            completer = argcomplete.completers.\
                        ChoicesCompleter(argument.choices)
        if completer is not None:
            validator = argument.completion_validator or prefix_validator

            def validated(prefix, **kwargs):
                choices = completer(**kwargs)
                return [c for c in choices if validator(c, prefix)]
            argparse_argument.completer = validated


def _execute_complete(commandobj, args):
    if argcomplete is None:
        return

    global _command_complete
    cword_prefix, debug = _command_complete

    parser = commandobj._create_parser(args)
    finder = argcomplete.CompletionFinder(
        argument_parser=parser,
        always_complete_options=False,
        validator=lambda *_: True)

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


def _modify_parser(commandobj, parser, args):
    if argcomplete is not None:

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
                to arguments). This allows us to do command delegation without
                knowing their relationship ahead of time.
                '''
                try:
                    global _command_complete
                    _command_complete = (cword_prefix, (lambda *_: None))

                    completions = commandobj.complete(
                            args if args is not None else comp_words[1:])
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


def prefix_validator(completion, cword):
    return completion.startswith(cword)


def fuzzy_path_validator(completion, cword):
    for full, sub in zip(completion.split(os.sep), cword.split(os.sep)):
        if not full.lower().startswith(sub.lower()):
            return False
    return True

import argcomplete
import code
import functools
import hashbang
import importlib
import io
from js import console
import js
import os
import pathlib
import shlex
import subprocess
import sys
from unittest.mock import patch


argcomplete.CompletionFinder.__call__ = functools.partialmethod(
    argcomplete.CompletionFinder.__call__, exit_method=sys.exit)

# This function removes the prefix "--arg=", which jquery terminal doesn't
# expect. Nerf it so we get the expected result.
argcomplete.CompletionFinder.quote_completions = \
    lambda self, completions, *_, **kwargs: completions


class Interpreter(code.InteractiveInterpreter):

    def __init__(self, file):
        super().__init__(locals={
            '__name__': '__main__',
            '__file__': file,
        })
        self.fds = {}
        self._file = file
        self.term = js.term
        hashbang.hashbang.HashbangCommand.exec_mode = 'execute'

    def runshell(self, cmd, code):
        with patch.multiple('sys',
                            stdout=io.StringIO(),
                            stderr=io.StringIO(),
                            argv=shlex.split(cmd)),\
                patch('hashbang.completion.argcomplete', new=None):
            if not sys.argv:
                return
            stem = pathlib.Path(self._file).stem
            basename = pathlib.Path(self._file).name
            try:
                try:
                    if sys.argv[0] not in (stem, basename):
                        print(f'{sys.argv[0]}: command not found. '
                              f'Expecting "{stem}" or "{basename}"',
                              file=sys.stderr)
                        sys.exit(127)
                    retval = self.runcode(code)
                finally:
                    console.log({
                        'stdout': self.iovalue(sys.stdout),
                        'stderr': self.iovalue(sys.stderr),
                    })
                    stdout = sys.stdout.getvalue()
                    stderr = sys.stderr.getvalue()
                    self.term.echoFormatted(stdout)
                    self.term.echoFormatted(stderr, 'red')
            except SystemExit as e:
                self.term.printExitCode(e.code)

    def get_fd(self, fd, mode='r'):
        if fd not in self.fds:
            self.fds[fd] = io.BytesIO() if 'b' in mode else io.StringIO()
        return self.fds[fd]

    def iovalue(self, stream):
        if isinstance(stream, io.StringIO):
            return stream.getvalue()
        return repr(stream.getvalue())

    def runcomplete(self, cmd, cursor_pos, code):
        import argcomplete
        argcomplete._DEBUG = True
        with patch.multiple('sys',
                            stdout=io.StringIO(),
                            stderr=io.StringIO(),
                            argv=shlex.split(cmd)),\
            patch('os.fdopen', self.get_fd),\
            patch('subprocess.check_output', new=fake_subprocess),\
            patch.dict(os.environ,
                       _ARGCOMPLETE_IFS='\013',
                       _ARGCOMPLETE='1',
                       _ARGCOMPLETE_SUPPRESS_SPACE='0',
                       _ARGCOMPLETE_COMP_WORDBREAKS=' \t\n"\'@><=;|&(:',
                       COMP_POINT=str(cursor_pos),
                       COMP_LINE=cmd,
                       COMP_TYPE=''):
            stem = pathlib.Path(self._file).stem
            if not sys.argv:
                return [stem]
            basename = pathlib.Path(self._file).name
            if len(sys.argv) < 2 and not cmd.endswith(' '):
                return [stem]
            try:
                try:
                    self.runcode(code)
                finally:
                    console.log({
                        'stdout': self.iovalue(sys.stdout),
                        'stderr': self.iovalue(sys.stderr),
                        'fd8': self.iovalue(self.get_fd(8)),
                        'fd9': self.iovalue(self.get_fd(9)),
                    })
                    completion_result = self.get_fd(8).getvalue()
                    if isinstance(completion_result, bytes):
                        completion_result = completion_result.decode('utf-8')
                    completion_result = completion_result.split('\013')
                    if len(completion_result) == 1:
                        return [completion_result[0].rstrip(' ')]
                    return completion_result
            except SystemExit as e:
                pass


class DictDelete:

    def __init__(self, dictionary, *keys):
        self.dictionary = dictionary
        self.original_dict = dictionary.copy()
        self.keys = keys

    def __enter__(self):
        for key in self.keys:
            del self.dictionary[key]

    def __exit__(self, *args, **kwargs):
        self.dictionary.clear()
        self.dictionary.update(self.original_dict)


def fake_subprocess(command, *args, **kwargs):
    if command[0] == 'bash':
        with DictDelete(os.environ, '_ARGCOMPLETE'):
            # Normal execute() processes and prints out the result, but here
            # we need to return it
            return bash._hashbang_command._execute_with_list(command)
    raise NotImplementedError('Generic subprocess is not supported')


@hashbang.command(
    hashbang.Argument('command', aliases='c'))
def bash(*_REMAINDER_, command=None):
    if command is not None:
        command = shlex.split(command)
        if command[0] == 'compgen':
            # Normal execute() processes and prints out the result, but here
            # we need to return it
            return compgen._hashbang_command._execute_with_list(command)
    raise NotImplementedError('Generic bash command not supported')


@hashbang.command(
    hashbang.Argument('action', aliases='A'))
def compgen(*_REMAINDER_, action=None):
    if action == 'file':
        return b'hashbang_test.py\013local_test_setup.sh'
    elif action == 'directory':
        return b'argument\013basic\013delegate\013experimental\013extension'
    return b''

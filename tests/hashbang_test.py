import ast
import unittest
import os
import subprocess
from subprocess import CalledProcessError
import sys
import re
import textwrap
from pathlib import Path
from importlib.machinery import SourceFileLoader
from importlib import util as importutil


class TestCase:
    def __init__(self, testfile, **kwargs):
        self.testfile = testfile


TEST_DIR = Path(__file__).parent
TEST_GLOBS = [
    (TEST_DIR/'basic').glob('*.py'),
    (TEST_DIR/'argument').glob('*.py'),
    (TEST_DIR/'delegate').glob('*.py'),
    (TEST_DIR/'extension').glob('*.py'),
    (TEST_DIR/'regression').glob('*.py'),
]
TEST_FILES = [file for glob in TEST_GLOBS for file in list(glob)]

DOC_MATCH = r'^\$ ?(.*[\w\W]*?)(?:^$|\Z)'
SET_MATCH = r'\{\{(.*)\}\}'


class Test(unittest.TestCase):

    def _Popen(self, command, *, cwd):
        return subprocess.Popen(
                sys.executable + ' ' + command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={'PYTHONPATH': str(Path.cwd())},
                cwd=cwd,
                shell=True,
                universal_newlines=True)

    def _test_completion(self, command, *, cwd):
        cmd = sys.executable + ' ' + command.strip().split(' ')[0]
        return subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={
                    'PYTHONPATH': str(Path.cwd()),
                    '_ARC_DEBUG': '1',
                    '_ARGCOMPLETE': '1',
                    '_COMPLETE_TO_STDOUT': '1',
                    'COMP_LINE': command,
                    'COMP_POINT': str(len(command)),
                },
                cwd=cwd,
                shell=True,
                universal_newlines=True)

    def is_argcomplete_available(self):
        return importutil.find_spec('argcomplete') is not None

    def test(self):
        for t in TEST_FILES:
            with t.open('r') as f:
                for doctest in DocTest.fromfile(f):
                    if doctest.get_config('completion', False):
                        if not self.is_argcomplete_available():
                            print('argcomplete not installed. '
                                  'Skipping completion test', file=sys.stderr)
                            continue
                    minpython = doctest.get_config('minpython', '3.0')
                    minpython = tuple(int(i) for i in minpython.split('.'))
                    if sys.version_info < minpython:
                        print('Skipping test because minpythonversion not met',
                              file=sys.stderr)
                        continue

                    with self.subTest(
                                testfile=doctest.testfile,
                                command=doctest.command):
                        print(doctest.describe())
                        if doctest.get_config('completion', False):
                            p = self._test_completion(
                                    doctest.command, cwd=str(t.parent))
                        else:
                            p = self._Popen(doctest.command, cwd=str(t.parent))
                        stdout, stderr = p.communicate()
                        self.assertEqual(
                            p.returncode,
                            doctest.get_config('returncode', 0),
                            msg=stderr)
                        doctest.make_assertion(self, stdout, stderr)

    def test_decorator(self):
        noarg = SourceFileLoader(
            'module.name',
            str(TEST_DIR/'basic'/'no_arguments.py')).load_module()
        self.assertEqual(noarg.main.__name__, 'main')
        self.assertEqual(noarg.main.__doc__, 'Function with no arguments')

    def test_callable(self):
        callabletest = SourceFileLoader(
            'module.name',
            str(TEST_DIR/'basic'/'callable.py')).load_module()
        self.assertEqual(callabletest.main.attribute1, 'attr1')


class DocTest:
    '''
    Representation of a test in the module documentation of the file. Tests
    must be defined in a docstring before any imports.

    Each test follows this format:
    $ <command to execute>  # config=value config2=value
    Output in stdout or stderr

    The first line prefixed by '$ ' is executed in a subprocess, with possible
    configs listed on the same line after a '#' in key=value format.

    Subsequent lines are the expected output in stdout or stderr, until a blank
    line is reached. If a blank line needs to be matched, '> ' can be added to
    the entire block to be matched, with the expected blank lines replaced by
    the character '>'.
    '''

    @staticmethod
    def fromfile(file):
        tree = ast.parse(file.read())
        testdoc = ast.get_docstring(tree)
        matches = None
        if testdoc is not None:
            matches = re.findall(DOC_MATCH, testdoc, re.MULTILINE)
        if not matches:
            raise RuntimeError('Cannot find tests in {}'.format(file.name))
        for match in matches:
            command, expected = match.split('\n', 1)
            if not expected.endswith('\n'):
                # docstring strips out the trailing newline. Add it back to
                # match with the shell output
                expected += '\n'
            # Remove prefix '> ', which is used to test outputs with blank
            # lines
            expected = re.sub(r'^>( |$)', '', expected, flags=re.MULTILINE)
            command, configs, *_ = command.split('#', 1) + [None]
            configs = (dict(e.split('=', 1) for e in configs.split(' ') if e)
                       if configs else {})

            if '<TAB>' in command:
                command = command.strip()[:-5]
                configs['completion'] = True
                expected = expected.rstrip('\n')

            yield DocTest(file.name, command, expected, configs)

    def __init__(self, testfile, command, expected, configs):
        self.testfile = testfile
        self.command = command
        self.expected = expected
        self.configs = configs

    def get_config(self, key, default):
        '''
        Configs are defined in key=value format, in the prompt line, after
        the comment marker '#'

        Supported configs are:
        1. returncode - the return code of the subprocess call. The default
                        expected is 0.
        2. stderr - whether to match the output against stderr instead of
                    stdout. The default is False.
        3. glob - whether to allow wildcard matches. If this is true, '?' will
                  match any single character, '*' will match any number of
                  characters except newlines, and '...' will match any number
                  of characters including newlines.
        '''
        return type(default)(self.configs.get(key, default))

    def make_assertion(self, testcase, stdout, stderr):
        actual = stderr if self.get_config('stderr', False) else stdout

        if self.get_config('glob', False):
            re_expected = re.compile(
                '^{}$'.format(
                    re.escape(self.expected)
                    # ... matches multiple lines
                    .replace('\\.\\.\\.', r'[\w\W]*')
                    # ? matches a single character except newlines
                    .replace('\\?', r'.')
                    # * matches all characters except newlines
                    .replace('\\*', r'.*')))
            testcase.assertRegex(
                    actual,
                    re_expected,
                    msg='Glob match failed. STDERR:\n{}'.format(stderr))
        else:
            testcase.assertEqual(
                    actual,
                    self.expected,
                    msg='String match failed. STDERR:\n{}'.format(stderr))

    def describe(self):
        return textwrap.dedent(
                'Executing {testfile}\n'
                '$ {command}\n'
                '{expected}').format(testfile=self.testfile,
                                     command=self.command,
                                     expected=self.expected)


if __name__ == '__main__':
    unittest.main()

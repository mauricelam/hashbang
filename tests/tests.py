import ast
import unittest
import os
import subprocess
from subprocess import CalledProcessError
import sys
import re
from pathlib import Path
from importlib.machinery import SourceFileLoader


class TestCase:
    def __init__(self, testfile, **kwargs):
        self.testfile = testfile


TEST_DIR = Path(__file__).parent
TEST_GLOBS = [
    (TEST_DIR/'basic').glob('*.py'),
    (TEST_DIR/'argument').glob('*.py'),
]
TEST_FILES = [file for glob in TEST_GLOBS for file in list(glob)]

DOC_MATCH = r'^\$(.*[\w\W]*?)(?:^$|\Z)'
SET_MATCH = r'\{\{(.*)\}\}'


class Test(unittest.TestCase):

    def _Popen(self, command, *, cwd):
        return subprocess.Popen(
                sys.executable + ' ' + command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={'PYTHONPATH': str(Path.cwd()/'src')},
                cwd=cwd,
                shell=True,
                universal_newlines=True)

    def getdoctest(self, file):
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
            command, expectations, *_ = command.split('#', 1) + [None]
            expectations = (dict(e.split('=', 1)
                                 for e in expectations.split(' ') if e)
                            if expectations else {})
            yield DocTest(file.name, command, expected, expectations)

    def test(self):
        for t in TEST_FILES:
            with t.open('r') as f:
                for doctest in self.getdoctest(f):
                    with self.subTest(
                                      testfile=doctest.testfile,
                                      command=doctest.command):
                        print(doctest.describe())
                        p = self._Popen(doctest.command, cwd=str(t.parent))
                        stdout, stderr = p.communicate()
                        self.assertEqual(
                            p.returncode,
                            doctest.get_expectation('returncode', 0),
                            msg=stderr)
                        doctest.make_assertion(self, stdout, stderr)

    def test_decorator(self):
        sys.path.append('src')
        noarg = SourceFileLoader(
            'module.name',
            str(TEST_DIR/'basic'/'no_arguments.py')).load_module()
        self.assertEqual(noarg.main.__name__, 'main')
        self.assertEqual(noarg.main.__doc__, 'Function with no arguments')


class DocTest:
    def __init__(self, testfile, command, expected, expectations):
        self.testfile = testfile
        self.command = command
        self.expected = expected
        self.expectations = expectations

    def get_expectation(self, key, default):
        return type(default)(self.expectations.get(key, default))

    def make_assertion(self, testcase, stdout, stderr):
        actual = stderr if self.get_expectation('stderr', False) else stdout

        if self.get_expectation('glob', False):
            re_expected = re.compile(
                '^' +
                re.escape(self.expected)
                # ... matches multiple lines
                .replace('\\.\\.\\.', r'[\w\W]*')
                # ? matches a single character except newlines
                .replace('\\?', r'.')
                # * matches all characters except newlines
                .replace('\\*', r'.*') +
                '$')
            testcase.assertRegex(actual, re_expected)
        else:
            testcase.assertEqual(actual, self.expected)

    def describe(self):
        return '''Executing {testfile}
        $ {command}
        {expected}
        '''.format(testfile=self.testfile,
                   command=self.command,
                   expected=self.expected)


if __name__ == '__main__':
    unittest.main()

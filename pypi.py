#!/usr/bin/env python3

from hashbang import command, Argument
from pathlib import Path

import subprocess
import sys
import tempfile

DIR = Path(__file__).parent.resolve()

VERSION_COMPONENTS = ('major', 'minor', 'patch')


def version_bump(current_version, bump):
    parts = current_version.split('.')
    bump_index = VERSION_COMPONENTS.index(bump)
    parts[bump_index] = str(int(parts[bump_index]) + 1)
    return '.'.join(parts)


@command(
    Argument('bump', choices=VERSION_COMPONENTS),
    Argument('upload', help='Whether to upload the created package to PyPI'),
    Argument('version', help='Specify the version name explicitly instead of '
                             'bumping'),
    Argument('git_status_check', help='Whether to check and return a failure '
                                      'if the current git repo has unstaged, '
                                      'untracked, or uncommitted files'))
def main(bump=None, *, upload=True, version=None, git_status_check=True):
    '''
    Package and upload a new version of Hashbang. This will bump the version
    number, package using setuptools, upload the new files to PyPI, create a
    git tag with the version number, and push that tag to origin.

    Usage: pypi.py {major,minor,patch}
           pypi.py --version VERSION
    '''
    if git_status_check:
        gitstatus = subprocess.check_output(['git', 'status', '--porcelain'])
        if len(gitstatus) != 0:
            print('Git directory not clean. Please commit your changes first')
            sys.exit(2)
    if version is None:
        if bump is None:
            print('Please specify a version bump level '
                  '("major", "minor", "patch")')
            sys.exit(2)
        with (DIR/'version.txt').open('r') as f:
            current_version = f.read()
            version = version_bump(current_version, bump)
    with (DIR/'version.txt').open('w') as f:
        f.write(version)
    subprocess.check_call(['git', 'commit', '-a', '-m',
                           'Tag version "{}"'.format(version)])
    with tempfile.TemporaryDirectory() as tempdir:
        print(DIR)
        subprocess.check_call(
            ['python3', str(DIR/'setup.py'), 'sdist', 'bdist_wheel'],
            cwd=tempdir)
        if upload:
            subprocess.check_call(
                ['python3', '-m', 'twine', 'upload', 'dist/*'],
                cwd=tempdir)
    subprocess.check_call(['git', 'tag', '-a', version, '-m',
                           'Tag version "{}"'.format(version)])
    subprocess.check_call(['git', 'push', '--tags'])


if __name__ == '__main__':
    main.execute()

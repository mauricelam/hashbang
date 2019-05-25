#!/usr/bin/env python3

from hashbang import command
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


@command
def main(bump=None, *, upload=True, version=None, git_status_check=True):
    '''
    Package and upload the built artifact to PyPI
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

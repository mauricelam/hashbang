#!/usr/bin/env python3

from hashbang import command, Argument
from pathlib import Path

import shutil
import subprocess
import sys
import tempfile

DIR = Path(__file__).parent.resolve()

VERSION_COMPONENTS = ('major', 'minor', 'patch')


def version_bump(current_version, bump):
    if bump == 'nobump':
        return current_version
    parts = current_version.split('.')
    bump_index = VERSION_COMPONENTS.index(bump)
    int_parts = (int(p) for p in parts)
    int_parts_bumped = (p if i < bump_index  # part before bump, keep unchanged
                        else p + 1 if i == bump_index  # part to bump
                        else 0  # part after bump, zero out
                        for i, p in enumerate(int_parts))
    parts = (str(p) for p in int_parts_bumped)
    return '.'.join(parts)


@command(
    Argument('bump', choices=VERSION_COMPONENTS + ('nobump',)),
    Argument('upload', help='Whether to upload the created package to PyPI'),
    Argument('version', help='Specify the version name explicitly instead of '
                             'bumping'),
    Argument('git_status_check', help='Whether to check and return a failure '
                                      'if the current git repo has unstaged, '
                                      'untracked, or uncommitted files'))
def main(bump=None, *, upload=True, version=None, git_status_check=True,
         test=False, dryrun=False, cleanup=True):
    '''
    Package and upload a new version of Hashbang. This will bump the version
    number, package using setuptools, upload the new files to PyPI, create a
    git tag with the version number, and push that tag to origin.

    Usage: pypi.py {major,minor,patch}
           pypi.py --version VERSION
    '''

    if dryrun:
        upload = False
        bump = 'nobump'
        git_status_check = False

    if git_status_check:
        gitstatus = subprocess.check_output(['git', 'status', '--porcelain'])
        if len(gitstatus) != 0:
            print('Git directory not clean. Please commit your changes first')
            sys.exit(2)
    if bump != 'nobump':
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
    subprocess.check_call(
        ['python3', str(DIR/'setup.py'), 'sdist', 'bdist_wheel'])
    if upload:
        subprocess.check_call(
            ['python3', '-m', 'twine', 'upload', 'dist/*'])
    if bump != 'nobump':
        subprocess.check_call(['git', 'tag', '-a', version, '-m',
                               'Tag version "{}"'.format(version)])
        subprocess.check_call(['git', 'push', '--tags'])

    # clean up
    if cleanup:
        shutil.rmtree('build')
        shutil.rmtree('dist')


if __name__ == '__main__':
    main.execute()

#!/usr/bin/env python3

from hashbang import command
from pathlib import Path

import subprocess
import sys
import tempfile

DIR = Path(__file__).parent.resolve()


@command
def main(version, *, upload=True):
    '''
    Package and upload the built artifact to PyPI
    '''
    gitstatus = subprocess.check_output(['git', 'status', '--porcelain'])
    if len(gitstatus) != 0:
        print('Git directory not clean. Please commit your changes first')
        sys.exit(2)
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


if __name__ == '__main__':
    main.execute()

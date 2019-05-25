#!/usr/bin/env python3

from hashbang import command

import subprocess


@command
def main():
    '''
    Package and upload the built artifact to PyPI
    '''
    subprocess.call(['python3', 'setup.py', 'sdist', 'bdist_wheel'])
    subprocess.call(['python3', '-m', 'twine', 'upload', 'dist/*'])


if __name__ == '__main__':
    main.execute()

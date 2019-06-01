import setuptools
from pathlib import Path

DIR = Path(__file__).resolve().parent
README = DIR/'README.md'
with README.open('r') as f:
    long_description = f.read()

with (DIR/'version.txt').open('r') as f:
    version = f.read()

setuptools.setup(
    name="hashbang",
    version=version,
    author="Maurice Lam",
    author_email="mauriceprograms@gmail.com",
    description="Turn Python functions into command line interfaces",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mauricelam/hashbang",
    packages=['hashbang'],
    test_suite="tests/hashbang_test.py",
    install_requires=[],
    extras_require={
        "completion": ["argcomplete"]
    },
    python_requires='~=3.4',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: System :: Shells",
    ],
)

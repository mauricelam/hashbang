import setuptools
import os

DIR = os.path.dirname(__file__)
README = os.path.join(DIR, 'README.md')
with open(README, 'r') as f:
    long_description = f.read()

setuptools.setup(
    name="hashbang",
    version="0.0.2",
    author="Maurice Lam",
    author_email="mauriceprograms@gmail.com",
    description="Create command line arguments with just an annotation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mauricelam/hashbang",
    packages=["src/hashbang"],
    test_suite="tests/hashbang_test.py",
    install_requires=[
        'pathlib;python_version<"3.4"',
    ],
    extras_require={
        "completion": ["argcomplete"]
    },
    python_requires='~=3.2',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: System :: Shells",
    ],
)

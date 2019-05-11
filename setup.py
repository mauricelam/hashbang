import setuptools
from pathlib import Path

DIR = Path(__file__).parent
README = DIR/'README.md'

setuptools.setup(
    name="hashbang",
    version="0.0.2",
    author="Maurice Lam",
    author_email="mauriceprograms@gmail.com",
    description="Create command line arguments with just an annotation",
    long_description=README.read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/mauricelam/hashbang",
    packages=["src/hashbang"],
    install_requires=[
        'pathlib;python_version<"3.4"',
    ],
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

# Hashbang ![Build status](https://travis-ci.com/mauricelam/hashbang.svg?branch=master)
Create command line arguments with just an annotation


-----

Hashbang is a Python 3 library for quickly creating command-line ready scripts. In the most basic form, a simple hashbang command can be just a simple annotation. For more complex types, it relies on Python3's [keyword-only arguments](https://www.python.org/dev/peps/pep-3102/) to provide a seamless syntax for command line usage.

```python3
#!/usr/bin/env python3

from hashbang import command

@command
def echo(message):
  print(message)
  
if __name__ == '__main__':
  echo.execute()
```

Installation
------------

Hashbang can be installed from pip

```sh
python3 -m pip install hashbang[completion]
```

This will also include [argcomplete](https://github.com/kislyuk/argcomplete) which powers the autocomplete for hashbang. The completion feature is optional; if you would like to exclude it, install using `pip install hashbang`.

Examples
--------

Let's start with some examples.

#### Simple, no argument script
```python3
#!/usr/bin/env python3

import os
from hashbang import command

@command
def pwd():
    return os.getcwd()

if __name__ == '__main__':
    pwd.execute()
```

<details><summary>result</summary>

```sh
$ pwd.py
/home/mauricelam/code/hashbang
```

</details>

The return value from the function is printed to stdout.

The additional value you get from using hashbang in this simple case is the help message, and the usage message when unexpected arguments are supplied.

<details><summary>result</summary>

```sh
$ pwd.py --help
usage: pwd.py [-h]

optional arguments:
  -h, --help  show this help message and exit
```

</details>

#### Positional argument (`nargs='?'`)

```python3
@command
def ls(dir=None):
  return os.listdir(path=dir)
```

<details><summary>result</summary>

```sh
$ ls.py
bin
etc
home
usr
var
```

```sh
$ ls.py bin
cp
df
echo
mkdir
mv
pwd
rm
```
</details>

#### Multiple positional argument (`nargs=None`)

```python3
@command
def cp(src, dest):
  shutil.copy2(src, dest)
```

<details><summary>result</summary>

```sh
$ cp.py textfile.txt copy_of_textfile.txt
```

</details>

#### Variadic positional argument (`nargs='*'`)

```python3
@command
def echo(*message):
  print(' '.join(message))
```

<details><summary>result</summary>

```sh
$ echo.py Hello world
Hello world
```

</details>

#### Boolean flag (default False) (`action='store_true'`)

```python3
@command
def pwd(*, resolve_symlink=False):
  cwd = os.cwd()
  if resolve_symlink:
    cwd = os.path.realpath(cwd)
  return cwd
```

<details><summary>result</summary>

```sh
$ pwd.py
/var
$ pwd.py --resolve_symlink
/private/var
```

</details>

#### Boolean flag (default True) (`action='store_false'`)

```python3
@command
def echo(*message, trailing_newline=True):
  print(' '.join(message), end=('\n' if trailing_newline else ''))
```

<details><summary>result</summary>

```sh
$ echo.py Hello world && echo '.'
Hello world
.
```

```sh
$ echo.py --notrailing_newline Hello world && echo '.'
Hello world.
```

</details>

#### Keyword argument (`action='store'`)

```python3
@command
def cut(*, fields=None, chars=None, delimeter='\t'):
  result = []
  for line in sys.stdin:
    seq = line.strip('\n').split(delimeter) if fields else line.strip('\n')
    pos = fields or chars
    result.append(''.join(seq[int(p)] for p in pos.split(',')))
  return '\n'.join(result)
```

<details><summary>result</summary>

```sh
$ echo -e 'a,b,c,d\ne,f,g,h' | cut.py --fields '1,2,3' --delimeter=','
bc
fg
```

</details>

Cheatsheet
----------

```python3
def func(positional_only, /, positional_or_keyword, *var_positional, keyword_only=None, **var_keyword):
  pass
```

| Parameter type                                               | Command line example     | argparse equivalent    |
| ------------------------------------------------------------ | ------------------------ | ---------------------- |
| Positional-only / positional-or-keyword (no default value)   | `command.py foo`         | `nargs=None`           |
| Positional-only / positional-or-keyword (with default value) | `command.py foo`         | `nargs='?'`            |
| Var positional                                               | `command.py foo bar baz` | `nargs='*'`            |
| Keyword-only (default false)                                 | `command.py --foo`       | `action='store_true'`  |
| Keyword-only (default true)                                  | `command.py --nofoo`     | `action='store_false'` |
| Keyword-only (other default types)                           | `command.py --foo value` | `action='store'`       |
| Var keyword                                                  | Not allowed in hashbang  |                        |

Command delegation
------------------

Argument annotations
--------------------

Help message
------------

Completion
----------

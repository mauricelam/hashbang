# Hashbang ![Build status](https://travis-ci.com/mauricelam/hashbang.svg?branch=master)
Create command line arguments with just an annotation


-----

Hashbang is a Python 3 library for quickly creating command-line ready scripts. In the most basic form, a simple hashbang command can be just a simple annotation.

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

#### Positional argument

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

#### Multiple positional argument

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

#### Variadic positional argument

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

#### Boolean flag (default False)

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

#### Boolean flag (default True)

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

#### Keyword argument

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

Usage
-----

Hashbang is built around Python's native function signature. In Python 3, an argument can be positional-only, positional-or-keyword, var-positional, keyword-only, or var-keyword.

```python3
def func(positional_only, /, positional_or_keyword, *var_positional, keyword_only=None, **var_keyword):
  pass
```

In hashbang, positional-only and positional-or-keyword arguments are treated as positional arguments in command line, and corresponds to `$1` or `$2` etc in shell scripting.

The var-positional argument captures zero or more positional argument from the command line

Argument annotations
--------------------

Help message
------------

Completion
----------

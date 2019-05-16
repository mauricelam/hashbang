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

```
$ pwd.py
/home/mauricelam/code/hashbang
```

</details>

The return value from the function is printed to stdout.

The additional value you get from using hashbang in this simple case is the help message, and the usage message when unexpected arguments are supplied.

<details><summary>result</summary>

```
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

```
$ ls.py
bin
etc
home
usr
var
```

```
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

```
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

```
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

```
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

```
$ echo.py Hello world && echo '.'
Hello world
.
```

```
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

```
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

| Parameter type                                               | Command line example     | argparse equivalent        |
| ------------------------------------------------------------ | ------------------------ | -------------------------- |
| Positional-only / positional-or-keyword (no default value)   | `command.py foo`         | `nargs=None`               |
| Positional-only / positional-or-keyword (with default value) | `command.py foo`         | `nargs='?'`                |
| Var positional                                               | `command.py foo bar baz` | `nargs='*'`                |
| Var positional (when named '\_REMAINDER\_')                  |                          | `nargs=argparse.REMAINDER` |
| Keyword-only (default false)                                 | `command.py --foo`       | `action='store_true'`      |
| Keyword-only (default true)                                  | `command.py --nofoo`     | `action='store_false'`     |
| Keyword-only (other default types)                           | `command.py --foo value` | `action='store'`           |
| Var keyword                                                  | Not allowed in hashbang  |                            |

Command delegation
------------------

The `hashbang.subcommands` function can be used to create a chain of commands, like `git branch`.

```python3
@command
def branch(newbranch=None):
  if newbranch is None:
    return '\n'.join(Repository('.').heads.keys())
  return Repository('.').create_head(newbranch)

@command
def log(*, max_count=None, graph=False):
  logs = Repository('.').log()
  if graph:
    return format_as_graph(logs)
  else:
    return '\n'.join(logs)
    
if __name__ == '__main__':
  subcommands(branch=branch, log=log).execute()
```

<details><summary>result</summary>
  
```
$ git.py branch
master
```

```
$ git.py branch hello
$ git.py branch
master
hello
```

```
$ git.py log
commit 602cbd7c68b0980ab1dbe0d3b9e83b69c04d9698 (HEAD -> master, origin/master)
Merge: 333d617 34c0a0f
Author: Maurice Lam <me@mauricelam.com>
Date:   Mon May 13 23:32:56 2019 -0700

    Merge branch 'master' of ssh://github.com/mauricelam/hashbang
    
commit 333d6172a8afa9e81baea0d753d6cfdc7751d38d
Author: Maurice Lam <me@mauricelam.com>
Date:   Mon May 13 23:31:17 2019 -0700

    Move directory structure to match pypi import
```
  
</details>

#### Custom command delegator

If `subocommands` is not sufficient for your purposes, you can use the `@command.delegator` decorator. Its usage is the same as the `@command` decorator, but the implementing function must then either call `.execute(_REMAINDER_)` on another command, or raise `NoMatchingDelegate` exception.

```python3
@command
def normal_who(*, print_dead_process=False, print_runlevel=False):
  return ...

@command
def whoami():
  '''
  Prints who I am.
  '''
  return getpass.getuser()

@command.delegator
def who(am=None, i=None, *_REMAINDER_):
  if (am, i) == ('am', 'i'):
    return whoami.execute([])
  elif (am, i) == (None, None):
    return normal_who.execute(_REMAINDER_)
  else:
    raise NoMatchingDelegate
```

<details><summary>result</summary>

```
$ who.py
mauricelam console  May  8 00:02 
mauricelam ttys000  May  8 00:03 
mauricelam ttys001  May  8 00:04
```

```
$ who.py am i 
mauricelam ttys001  May  8 00:04
```

```
$ who.py --print_dead_process
mauricelam ttys002  May  8 00:40 	term=0 exit=0
```

```
$ who.py are you
Error: No matching delegate
```

</details>

While using the regular `@command` decorator will still work in this situation, but tab-completion and help message will be wrong.

<details><summary>✓ Using <code>@command.delegator</code></summary>

```
$ who.py --help
usage: who.py [--print_dead_process] [--print_runlevel]

optional arguments:
  --print_dead_process
  --print_runlevel
```

```
$ who.py am i --help
usage: who.py am i

Prints who I am.
```

</details>

<details><summary>✗ Using <code>@command</code></summary>
  
```
$ who.py am i --help
usage: who.py [-h] [am] [i]

positional arguments:
  am
  i

optional arguments:
  -h, --help  show this help message and exit
```
  
</details>

Argument annotation
-------------------

An argument can be further customized using the argument annotation defined in [PEP 3107](https://www.python.org/dev/peps/pep-3107/).

For example, an alias can be added to the argument.

```python3
@command
def echo(
    *message,
    trailing_newline: Argument(aliases=('n',)) = True):
  print(' '.join(message), end=('\n' if trailing_newline else ''))
```

<details><summary>result</summary>

```
$ echo.py Hello world && echo '.'
Hello world
.
```

```
$ echo.py -n Hello world && echo '.'
Hello world.
```

</details>

```python3
Argument(*, choices=None, completer=None, aliases=(), help=None, type=None, remainder=False)
```

- `choices` – A sequence of strings representing possible values for the argument. This is used in the help message and also in tab-completion.
- `completer` – A function that returns a sequence of possible choices for this argument. This can be used for arguments where the choices are too expensive to generate ahead of time.
- `aliases` – A sequence of strings that are aliases of the option. If the alias has only one character, it is specified with one dash `-f`. If the alias has multiple characters, it is specified with two dashes `--foo`.
- `help` – The help message for this argument.
- `type` – A function that takes a string, and its return value will be used as the parameter value instead of the raw input string.
- `remainder` – Boolean indicating whether this argument should capture all the remaining arguments. This is True by default if the argument is named `_REMAINDER_`.

Help message
------------
The help message for the command is take directly from the docstring of the function. Additionally, the `help` argument in `Argument` can be used to document each argument. A paragraph in the docstring prefixed with `usage:` (case insensitive) is used as the usage message.

```python3
@command
def git(
    command: Argument(help='Possible commands are "branch", "log", etc', choices=('branch', 'log')),
    *_REMAINDER_):
  '''
  git - the stupid content tracker
  
  Usage:  git [--version] [--help] [-C <path>] [-c <name>=<value>]
           [--exec-path[=<path>]] [--html-path] [--man-path] [--info-path]
           [-p|--paginate|-P|--no-pager] [--no-replace-objects] [--bare]
           [--git-dir=<path>] [--work-tree=<path>] [--namespace=<name>]
           [--super-prefix=<path>]
           <command> [<args>]
  '''
  return ...
```

<details><summary>result</summary>

```
$ git.py --help
usage:  git [--version] [--help] [-C <path>] [-c <name>=<value>]
         [--exec-path[=<path>]] [--html-path] [--man-path] [--info-path]
         [-p|--paginate|-P|--no-pager] [--no-replace-objects] [--bare]
         [--git-dir=<path>] [--work-tree=<path>] [--namespace=<name>]
         [--super-prefix=<path>]
         <command> [<args>]

git - the stupid content tracker

positional arguments:
  {branch,log}  Possible commands are "branch", "log", etc

optional arguments:
  -h, --help    show this help message and exit
```

```
$ git.py --foobar
unknown option: --foobar
usage: git [--version] [--help] [-C <path>] [-c <name>=<value>]
           [--exec-path[=<path>]] [--html-path] [--man-path] [--info-path]
           [-p | --paginate | -P | --no-pager] [--no-replace-objects] [--bare]
           [--git-dir=<path>] [--work-tree=<path>] [--namespace=<name>]
           <command> [<args>]
```

</details>

Tab completion
--------------

Exit code
---------

# Hashbang 
[![Build status](https://travis-ci.com/mauricelam/hashbang.svg?branch=master)](https://travis-ci.com/mauricelam/hashbang)
[![PyPI](https://img.shields.io/pypi/v/hashbang.svg?color=%230073b7)](https://pypi.org/project/hashbang/)

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

Quick Start Examples
--------------------

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

<details><summary><code>$ pwd.py</code></summary>

```
$ pwd.py
/home/mauricelam/code/hashbang
```

</details>

The return value from the function is printed to stdout.

The additional value you get from using hashbang in this simple case is the help message, and the usage message when unexpected arguments are supplied.

<details><summary><code>$ pwd.py --help</code></summary>

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

<details><summary><code>$ ls.py</code></summary>

```
$ ls.py
bin
etc
home
usr
var
```

</details>
<details><summary><code>$ ls.py bin</code></summary>

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

<details><summary><code>$ cp.py textfile.txt copy_of_textfile.txt</code></summary>

```
$ cp.py textfile.txt copy_of_textfile.txt
$ ls
textfile.txt    copy_of_textfile.txt
```

</details>

#### Variadic positional argument (`nargs='*'`)

```python3
@command
def echo(*message):
  print(' '.join(message))
```

<details><summary><code>$ echo.py Hello world</code></summary>

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

<details><summary><code>$ pwd.py</code></summary>

```
$ pwd.py
/var
```

</details>

<details><summary><code>$ pwd.py --resolve_symlink</code></summary>

```
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

<details><summary><code>$ echo.py Hello world && echo '.'</code></summary>

```
$ echo.py Hello world && echo '.'
Hello world
.
```

</details>

<details><summary><code>$ echo.py --notrailing_newline Hello world && echo '.'</code></summary>

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

<details><summary><code>$ echo -e 'a,b,c,d\ne,f,g,h' | cut.py --fields '1,2,3' --delimeter=','</code></summary>

```
$ echo -e 'a,b,c,d\ne,f,g,h' | cut.py --fields '1,2,3' --delimeter=','
bc
fg
```

</details>

Cheatsheet
----------

| Parameter type                         | Python syntax            | Command line example     | argparse equivalent        |
| -------------------------------------- | ------------------------ | ------------------------ | -------------------------- |
| Positional (no default value)          | `def func(foo)`          | `command.py foo`         | `nargs=None`               |
| Positional (with default value)        | `def func(foo=None)`     | `command.py foo`         | `nargs='?'`                |
| Var positional                         | `def func(*foo)`         | `command.py foo bar baz` | `nargs='*'`                |
| Var positional (named `\_REMAINDER\_`) | `def func(*_REMAINDER_)` |                          | `nargs=argparse.REMAINDER` |
| Keyword-only (default false)           | `def func(*, foo=False)` | `command.py --foo`       | `action='store_true'`      |
| Keyword-only (default true)            | `def func(*, foo=True)`  | `command.py --nofoo`     | `action='store_false'`     |
| Keyword-only (other default types)     | `def func(*, foo='bar')` | `command.py --foo value` | `action='store'`           |
| Var keyword                            | `def func(**kwargs)`     | Not allowed in hashbang  |                            |

See the [API reference](https://github.com/mauricelam/hashbang/wiki/API-reference) wiki page for the full APIs.

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

<details><summary><code>$ git.py branch</code></summary>
  
```
$ git.py branch
master
```

</details>

<details><summary><code>$ git.py branch hello</code></summary>

```
$ git.py branch hello
$ git.py branch
master
hello
```

</details>

<details><summary><code>$ git.py log</code></summary>

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

<details><summary><code>$ who.py</code></summary>

```
$ who.py
mauricelam console  May  8 00:02 
mauricelam ttys000  May  8 00:03 
mauricelam ttys001  May  8 00:04
```

</details>

<details><summary><code>$ who.py am i</code></summary>

```
$ who.py am i 
mauricelam ttys001  May  8 00:04
```

</details>

<details><summary><code>$ who.py --print_dead_process</code></summary>

```
$ who.py --print_dead_process
mauricelam ttys002  May  8 00:40 	term=0 exit=0
```

</details>

<details><summary><code>$ who.py are you</code></summary>

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

Argument customization
----------------------

An argument can be further customized using the `Argument` class in the `@command` decorator.

For example, an alias can be added to the argument.

```python3
@command(Argument('trailing_newline', aliases=('n',))
def echo(*message, trailing_newline=True):
  print(' '.join(message), end=('\n' if trailing_newline else ''))
```

<details><summary><code>$ echo.py Hello world && echo '.'</code></summary>

```
$ echo.py Hello world && echo '.'
Hello world
.
```

</details>

<details><summary><code>$ echo.py -n Hello world && echo '.'</code></summary>

```
$ echo.py -n Hello world && echo '.'
Hello world.
```

</details>

<details><summary>Alternatively, you can also choose to specify the <code>Argument</code> using argument annotation syntax defined in <a href="https://www.python.org/dev/peps/pep-3107/">PEP 3107</a>.</summary>

```python3
@command
def echo(
    *message,
    trailing_newline: Argument(aliases=('n',)) = True):
  print(' '.join(message), end=('\n' if trailing_newline else ''))
```

</details>

> See https://github.com/mauricelam/hashbang/wiki/API-reference#argument for the full `Argument` API.

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

<details><summary><code>$ git.py --help</code></summary>

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

</details>

<details><summary><code>$ git.py --nonexistent</code></summary>

```
$ git.py --nonexistent
unknown option: --nonexistent
usage: git [--version] [--help] [-C <path>] [-c <name>=<value>]
           [--exec-path[=<path>]] [--html-path] [--man-path] [--info-path]
           [-p | --paginate | -P | --no-pager] [--no-replace-objects] [--bare]
           [--git-dir=<path>] [--work-tree=<path>] [--namespace=<name>]
           <command> [<args>]
```

</details>

Tab completion
--------------

#### Setup

Hashbang also comes with tab completion functionality, powered by [argcomplete](https://github.com/kislyuk/argcomplete). Since argcomplete is an optional dependency of hashbang, you can install the completion feature using

```sh
python3 -m pip install hashbang[completion]
```

After installing, to register a command for tab-completion, run

```sh
eval "$(register-python-argcomplete my-awesome-script)"
```

Alternatively, to activate global completion for all commands, follow the one-time setup directions in the [Global completion](https://github.com/kislyuk/argcomplete#global-completion) section of argcomplete's documentation, and then add the string `PYTHON_ARGCOMPLETE_OK` to the top of the file as a comment (after the `#!` line).

#### Specifying the choices

The simplest way to use tab completion is via the `choices` argument in the `Argument` constructor.

```python3
@command
def apt_get(command: Argument(choices=('update', 'upgrade', 'install', 'remove')), *_REMAINDER_):
  return subprocess.check_output(['apt-get', command, *_REMAINDER])
```

<details><summary><code>$ apt_get.py &lt;TAB&gt;&lt;TAB&gt;</code></summary>

```
$ apt_get.py <TAB><TAB>
update    upgrade    install    remove
```
```
$ apt_get.py up<TAB><TAB>
update    upgrade
```
```
$ apt_get.py upg<TAB>
$ apt_get.py upgrade
```

</details>

#### Using a completer

If the choices are not known ahead of time (before execution), or is too expensive to precompute, you can instead specify a completer for the argument.

```python3
@command
def cp(src: Argument(completer=lambda x: os.listdir()), dest):
  shutils.copy2(src, dest)
```

<details><summary><code>$ cp.py &lt;TAB&gt;&lt;TAB&gt;</code></summary>

```
$ cp.py <TAB><TAB>
LICENSE           build             hashbang          requirements.txt  tests
```
```
$ cp.py LIC<TAB>
$ cp.py LICENSE 
```

</details>

Exit codes
----------

Just like normal Python programs, the preferred way to set an exit code is using `sys.exit()`. By default, exit code `0` is returned for functions that run without raising an exception, or printed a help message with `help`. If a function raises an exception, the result code is `1`. If a function quits with `sys.exit()`, the exit code of is preserved.

In addition, you can also call `sys.exit()` inside the `exception_handler` if you want to return different exit codes based on the exception that was thrown. See `tests/extension/custom_exit_codes.py` for an example.

Further reading
---------------

For further reading, check out the [wiki](https://github.com/mauricelam/hashbang/wiki) pages.

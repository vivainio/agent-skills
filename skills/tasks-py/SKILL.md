---
name: tasks-py
description: Create and maintain tasks.py task runner files. Use when user wants to add project automation, create a tasks.py file, add tasks, or mentions "tasks.py".
---

# tasks.py Task Runner

A zero-dependency Python task runner using `do_` prefixed functions.

## Creating a New tasks.py

When asked to create a tasks.py, use this template:

```python
"""Simple, fast and fun task runner, not unlike gulp / grunt (but zero dep)"""

import os
import shutil
import subprocess
import sys
import textwrap


# === TASKS (add your do_ functions here) ===


def do_check(args) -> None:
    """Run linting and type checking"""
    c("ruff check")


def do_format(args) -> None:
    """Format code with ruff"""
    c("ruff format .")


def do_test(args) -> None:
    """Run tests"""
    c("pytest")


def default() -> None:
    show_help()


# === LIBRARY FUNCTIONS ===

emit = print


def c(cmd):
    """Run command, raise on failure"""
    emit(">", cmd)
    subprocess.check_call(cmd, shell=True)


def c_ignore(cmd):
    """Run command, ignore failures"""
    emit(">", cmd)
    subprocess.call(cmd, shell=True)


def c_dir(cmd, dir):
    """Run command in specific directory"""
    emit("%s > %s" % (dir, cmd))
    subprocess.check_call(cmd, cwd=dir, shell=True)


def c_spawn(cmd, cwd=None):
    """Spawn command in background"""
    emit(">", cmd)
    subprocess.Popen(cmd, cwd=cwd, shell=True)


def copy_files(sources, destinations):
    """Copy each source to each destination"""
    for src in sources:
        for dest in destinations:
            src = os.path.abspath(src)
            dest = os.path.abspath(dest)
            emit("cp %s -> %s" % (src, dest))
            if not os.path.isdir(dest):
                emit("Directory not found", dest)
                continue
            shutil.copy(src, dest)


# === LAUNCHER (do not edit below) ===


def show_help() -> None:
    g = globals()
    emit(
        "Command not found, try",
        sys.argv[0],
        " | ".join([n[3:] for n in g if n.startswith("do_")]),
        "| <command> -h",
    )


def main() -> None:
    if len(sys.argv) < 2:
        default()
        return
    func = sys.argv[1]
    f = globals().get("do_" + func)
    if sys.argv[-1] == "-h":
        emit(
            textwrap.dedent(f.__doc__).strip()
            if f.__doc__
            else "No documentation for this command",
        )
        return
    if not f:
        show_help()
        return
    f(sys.argv[2:])


if __name__ == "__main__":
    main()
```

## Adding Tasks

Add new tasks by creating `do_<name>` functions:

```python
def do_build(args) -> None:
    """Build the project"""
    c("python -m build")
```

## Common Task Patterns

### Publishing to PyPI
```python
def do_publish(args) -> None:
    """Publish package to PyPI"""
    shutil.rmtree("dist", ignore_errors=True)
    c("python -m build")
    c("twine upload dist/*")
```

### Running in subdirectory
```python
def do_test(args) -> None:
    """Run tests in test directory"""
    os.chdir("test")
    c("pytest")
```

### Using c_dir for directory-scoped commands
```python
def do_frontend(args) -> None:
    """Build frontend"""
    c_dir("npm run build", "frontend")
```

### Task with arguments
```python
def do_greet(args) -> None:
    """Greet someone: greet <name>"""
    name = args[0] if args else "World"
    print(f"Hello, {name}!")
```

## Usage

```bash
python tasks.py              # Show available tasks
python tasks.py check        # Run the check task
python tasks.py test -h      # Show help for test task
```

## Library Functions Reference

| Function | Purpose |
|----------|---------|
| `c(cmd)` | Run command, fail on error |
| `c_ignore(cmd)` | Run command, ignore errors |
| `c_dir(cmd, dir)` | Run command in directory |
| `c_spawn(cmd, cwd)` | Run command in background |
| `copy_files(src, dest)` | Copy files to destinations |

## Guidelines

- Keep tasks.py at project root
- Only use standard library imports
- Document tasks with docstrings
- Use `c()` for commands that must succeed
- Use `c_ignore()` for optional/cleanup commands

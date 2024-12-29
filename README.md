# Circular Imports

If you see an error like this:

```
ImportError: cannot import name 'some_module'
```

or 

```
ImportError: cannot import name 'some_module' from partially initialized module 'path.to.module' (most likely due to a circular import)
```

then you have a circular import in your code.

This library helps you to detect circular imports in Python code to fix them.

## Installation

```bash
pip install circular-imports
```

## Usage

### CLI

Example:

```bash
circular-imports path/to/python/project/dir --output output_file.dot --exclude .venv,build
```

Parameters:

- `path`: path to the Python project directory
- `--output`: output file, this can be a [`.dot`](https://graphviz.org/docs/layouts/dot/), [`.mermaid`](https://mermaid.js.org/). When empty, the output will be printed to the console.
- `--exclude`: comma-separated list of directories to exclude from the search

Exits with code 0 if no circular imports are found, 1 otherwise.

### Python

```python
from unittest import TestCase

from circular_imports import cycles_in_path


class TestCircularDeps(TestCase):
    def test_no_cycles(self):
        cycles = cycles_in_path(".", exclude=".venv,build")
        self.assertEqual(cycles, set())
```

## License

MIT
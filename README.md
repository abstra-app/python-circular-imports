# Circular Imports

If you see an error like this:

```
ImportError: cannot import name 'some_module'
```

or 

```
"ImportError: cannot import name 'some_module' from partially initialized module 'path.to.module' (most likely due to a circular import) "
```

then you have a circular import in your code.

This library helps you to detect circular imports in Python code.

## Installation

```bash
pip install circular-imports
```

## Usage

### CLI

```bash
circular-imports path/to/python/project/dir
```

### Python

```python
from circular_imports import find_circular_imports

circular_imports = find_circular_imports('path/to/python/project/dir')
print(circular_imports)
```

## License

MIT
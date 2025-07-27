# Difference Finder

```{eval-rst}
.. automodule:: jsonschema_diff.diff_finder
   :members:
   :undoc-members:
   :show-inheritance:
```

## Overview

The `diff_finder` module is the first stage in the comparison pipeline. It recursively compares two JSON schemas and identifies raw differences.

## Key Classes

### DiffFinder

The main class that performs the low-level difference detection.

## Features

- Recursive schema comparison
- Path tracking for nested differences
- Operation type detection (add, remove, change)
- Order preservation

## Examples

```python
from jsonschema_diff.diff_finder import DiffFinder

finder = DiffFinder()
differences = finder.find_differences(old_schema, new_schema)
```

# Difference Processor

```{eval-rst}
.. automodule:: jsonschema_diff.diff_processor
   :members:
   :undoc-members:
   :show-inheritance:
```

## Overview

The `diff_processor` module is the second stage in the comparison pipeline. It processes raw differences from the diff finder and converts add/remove pairs into more meaningful change operations.

## Key Classes

### DiffProcessor

The main class that processes and consolidates differences.

## Features

- Converts add/remove pairs to change operations
- Maintains difference order
- Preserves path information
- Handles complex nested structures

## Examples

```python
from jsonschema_diff.diff_processor import DiffProcessor

processor = DiffProcessor()
processed_diffs = processor.process_differences(raw_differences)
```

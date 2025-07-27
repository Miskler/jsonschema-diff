# Output Formatter

```{eval-rst}
.. automodule:: jsonschema_diff.formatter
   :members:
   :undoc-members:
   :show-inheritance:
```

## Overview

The `formatter` module handles the final formatting of differences for display. It converts the internal difference representation into human-readable output with proper spacing and grouping.

## Key Classes

### Formatter

The main class responsible for formatting output.

## Features

- Proper line spacing and grouping
- Support for different output formats
- Context information display
- Color coding support

## Examples

```python
from jsonschema_diff.formatter import Formatter

formatter = Formatter()
output = formatter.format_groups(diff_groups)
```

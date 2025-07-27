# Path Utilities

```{eval-rst}
.. automodule:: jsonschema_diff.path_utils
   :members:
   :undoc-members:
   :show-inheritance:
```

## Overview

The `path_utils` module provides utilities for working with JSON Schema paths. It handles path formatting, parsing, and value retrieval.

## Key Functions

### format_path
### parse_path
### get_value_at_path

## Features

- Human-readable path formatting
- Support for nested properties
- Array index handling
- Special character escaping
- Unicode support

## Examples

```python
from jsonschema_diff.path_utils import format_path, parse_path

# Format a path for display
formatted = format_path(['properties', 'user', 'properties', 'name'])
# Result: "user.name"

# Parse a formatted path back to components
components = parse_path("user.address[0].street")
```

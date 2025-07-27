# Context Manager

```{eval-rst}
.. automodule:: jsonschema_diff.context_manager
   :members:
   :undoc-members:
   :show-inheritance:
```

## Overview

The `context_manager` module provides context information for schema differences. It helps users understand the broader context around changes by showing related parameter values.

## Key Classes

### ContextManager

## Features

- Context value extraction from schemas
- Operation-specific filtering
- Path-based context lookup
- Integration with configuration system

## Examples

```python
from jsonschema_diff.context_manager import ContextManager

manager = ContextManager(old_schema, new_schema)
manager.add_context_information(differences)
```

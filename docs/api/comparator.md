# Comparator Module

The `comparator` module provides the main interface for comparing JSON schemas.

## Overview

The `SchemaComparator` class orchestrates the entire comparison pipeline, coordinating all other modules to produce the final formatted output.

## Classes

```{eval-rst}
.. automodule:: jsonschema_diff.comparator
   :members:
   :undoc-members:
   :show-inheritance:
```

## Usage Examples

### Basic Comparison

```python
from jsonschema_diff import SchemaComparator

old_schema = {"type": "object", "properties": {"name": {"type": "string"}}}
new_schema = {"type": "object", "properties": {"name": {"type": "integer"}}}

comparator = SchemaComparator(old_schema, new_schema)
result = comparator.compare()
print(result)
```

### Pipeline Steps

The `compare()` method executes these steps:

1. **DiffFinder**: Finds raw differences between wrapped schemas
2. **DiffProcessor**: Converts add/remove pairs to change operations  
3. **Combiner**: Applies combination rules to related parameters
4. **RenderProcessor**: Adds context and structures for rendering
5. **Formatter**: Produces final formatted output with colors

### Convenience Function

```python
from jsonschema_diff import compare_schemas

# Equivalent to creating SchemaComparator and calling compare()
result = compare_schemas(old_schema, new_schema)
```

## Implementation Details

### Schema Wrapping

The comparator wraps schemas in a `{"properties": ...}` structure before passing to `DiffFinder`. This ensures consistent handling regardless of the input schema structure.

### Component Initialization

- `ParameterCombiner`: Initialized with both schemas for virtual parameter creation
- `RenderProcessor`: Initialized with both schemas for context value lookup

### Error Handling

The comparator gracefully handles:
- Missing `properties` keys in schemas
- Empty schemas
- Malformed schema structures

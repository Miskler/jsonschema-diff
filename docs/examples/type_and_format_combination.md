# Type and Format Combination

Shows how type and format changes are combined into a single display.

## Schemas

### Old Schema

```json
{
  "type": "object",
  "properties": {
    "email": {
      "type": "string",
      "format": "email"
    }
  }
}
```

### New Schema

```json
{
  "type": "object",
  "properties": {
    "email": {
      "type": "integer",
      "format": "number"
    }
  }
}
```

## Comparison Result

### Using compare_schemas()

```python
from jsonschema_diff import compare_schemas

old_schema = {
  "type": "object",
  "properties": {
    "email": {
      "type": "string",
      "format": "email"
    }
  }
}

new_schema = {
  "type": "object",
  "properties": {
    "email": {
      "type": "integer",
      "format": "number"
    }
  }
}

result = compare_schemas(old_schema, new_schema)
print(result)
```

### Output

```
[36m[1mr ["email"].type: "string/email" -> "integer/number"[0m
[39m[1m  ["email"].format: "email"[0m
```

### Using SchemaComparator class

```python
from jsonschema_diff import SchemaComparator

comparator = SchemaComparator(old_schema, new_schema)
result = comparator.compare()
```

## Analysis

This example demonstrates:

- **Type Changes**: How the library handles changes to field types
- **Format Changes**: Detection of format attribute modifications
- **Parameter Combination**: How related parameters are combined for clarity

# Basic Type Change

Simple example showing how type changes are displayed.

## Schemas

### Old Schema

```json
{
  "type": "object",
  "properties": {
    "age": {
      "type": "string"
    }
  }
}
```

### New Schema

```json
{
  "type": "object",
  "properties": {
    "age": {
      "type": "integer"
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
    "age": {
      "type": "string"
    }
  }
}

new_schema = {
  "type": "object",
  "properties": {
    "age": {
      "type": "integer"
    }
  }
}

result = compare_schemas(old_schema, new_schema)
print(result)
```

### Output

```
[36m[1mr ["age"].type: "string" -> "integer"[0m
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

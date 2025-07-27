# Context Display

Demonstrates how related context information is shown when important fields change.

## Schemas

### Old Schema

```json
{
  "type": "object",
  "properties": {
    "name": {
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
    "name": {
      "type": "integer",
      "format": "email"
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
    "name": {
      "type": "string",
      "format": "email"
    }
  }
}

new_schema = {
  "type": "object",
  "properties": {
    "name": {
      "type": "integer",
      "format": "email"
    }
  }
}

result = compare_schemas(old_schema, new_schema)
print(result)
```

### Output

```
[36m[1mr ["name"].type: "string/email" -> "integer/email"[0m
[39m[1m  ["name"].format: "email"[0m
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
- **Context Display**: Showing related fields for better understanding

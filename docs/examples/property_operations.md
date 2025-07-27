# Property Operations

Demonstrates addition and removal of properties.

## Schemas

### Old Schema

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string"
    },
    "old_field": {
      "type": "string"
    },
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
    "name": {
      "type": "string"
    },
    "new_field": {
      "type": "string"
    },
    "phone": {
      "type": "string"
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
      "type": "string"
    },
    "old_field": {
      "type": "string"
    },
    "email": {
      "type": "string",
      "format": "email"
    }
  }
}

new_schema = {
  "type": "object",
  "properties": {
    "name": {
      "type": "string"
    },
    "new_field": {
      "type": "string"
    },
    "phone": {
      "type": "string"
    }
  }
}

result = compare_schemas(old_schema, new_schema)
print(result)
```

### Output

```
[31m[1m- ["old_field"]: {"type": "string"}[0m

[31m[1m- ["email"]: {"type": "string", "format": "email"}[0m

[32m[1m+ ["new_field"]: {"type": "string"}[0m

[32m[1m+ ["phone"]: {"type": "string"}[0m
```

### Using SchemaComparator class

```python
from jsonschema_diff import SchemaComparator

comparator = SchemaComparator(old_schema, new_schema)
result = comparator.compare()
```

## Analysis

This example demonstrates:

- **Property Addition**: How new properties are displayed
- **Property Removal**: Detection and display of removed properties

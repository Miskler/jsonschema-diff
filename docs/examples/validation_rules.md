# Validation Rules

Shows changes to validation constraints like minimum and maximum values.

## Schemas

### Old Schema

```json
{
  "type": "object",
  "properties": {
    "age": {
      "type": "integer",
      "minimum": 0,
      "maximum": 120
    },
    "score": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 100.0
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
      "type": "integer",
      "minimum": 18,
      "maximum": 65
    },
    "score": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 10.0
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
      "type": "integer",
      "minimum": 0,
      "maximum": 120
    },
    "score": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 100.0
    }
  }
}

new_schema = {
  "type": "object",
  "properties": {
    "age": {
      "type": "integer",
      "minimum": 18,
      "maximum": 65
    },
    "score": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 10.0
    }
  }
}

result = compare_schemas(old_schema, new_schema)
print(result)
```

### Output

```
[36m[1mr ["age"].range: "0-120" -> "18-65"[0m

[36m[1mr ["score"].maximum: 100.0 -> 10.0[0m
```

### Using SchemaComparator class

```python
from jsonschema_diff import SchemaComparator

comparator = SchemaComparator(old_schema, new_schema)
result = comparator.compare()
```

## Analysis

This example demonstrates:

- **Context Display**: Showing related fields for better understanding
- **Validation Rules**: Changes to validation constraints

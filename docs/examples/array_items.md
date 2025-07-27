# Array Items

Shows how changes to array item schemas are handled.

## Schemas

### Old Schema

```json
{
  "type": "object",
  "properties": {
    "tags": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "scores": {
      "type": "array",
      "items": {
        "type": "integer",
        "minimum": 0
      }
    }
  }
}
```

### New Schema

```json
{
  "type": "object",
  "properties": {
    "tags": {
      "type": "array",
      "items": {
        "type": "string",
        "format": "uri"
      }
    },
    "scores": {
      "type": "array",
      "items": {
        "type": "number",
        "minimum": 0.0
      }
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
    "tags": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "scores": {
      "type": "array",
      "items": {
        "type": "integer",
        "minimum": 0
      }
    }
  }
}

new_schema = {
  "type": "object",
  "properties": {
    "tags": {
      "type": "array",
      "items": {
        "type": "string",
        "format": "uri"
      }
    },
    "scores": {
      "type": "array",
      "items": {
        "type": "number",
        "minimum": 0.0
      }
    }
  }
}

result = compare_schemas(old_schema, new_schema)
print(result)
```

### Output

```
[36m[1mr ["tags"].items.type: "string" -> "string/uri"[0m
[39m[1m  ["tags"].items.format: "uri"[0m

[36m[1mr ["scores"].items.type: "integer" -> "number"[0m
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
- **Array Handling**: Changes in array items and their schemas

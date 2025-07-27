# Nested Objects

Complex example with nested object structures.

## Schemas

### Old Schema

```json
{
  "type": "object",
  "properties": {
    "user": {
      "type": "object",
      "properties": {
        "profile": {
          "type": "object",
          "properties": {
            "name": {
              "type": "string"
            },
            "age": {
              "type": "integer",
              "minimum": 0
            }
          }
        }
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
    "user": {
      "type": "object",
      "properties": {
        "profile": {
          "type": "object",
          "properties": {
            "name": {
              "type": "string",
              "format": "email"
            },
            "age": {
              "type": "integer",
              "minimum": 18
            }
          }
        }
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
    "user": {
      "type": "object",
      "properties": {
        "profile": {
          "type": "object",
          "properties": {
            "name": {
              "type": "string"
            },
            "age": {
              "type": "integer",
              "minimum": 0
            }
          }
        }
      }
    }
  }
}

new_schema = {
  "type": "object",
  "properties": {
    "user": {
      "type": "object",
      "properties": {
        "profile": {
          "type": "object",
          "properties": {
            "name": {
              "type": "string",
              "format": "email"
            },
            "age": {
              "type": "integer",
              "minimum": 18
            }
          }
        }
      }
    }
  }
}

result = compare_schemas(old_schema, new_schema)
print(result)
```

### Output

```
[36m[1mr ["user"]["profile"]["name"].type: "string" -> "string/email"[0m
[39m[1m  ["user"]["profile"]["name"].format: "email"[0m

[36m[1mr ["user"]["profile"]["age"].minimum: 0 -> 18[0m
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
- **Nested Objects**: Handling of complex nested schema structures
- **Validation Rules**: Changes to validation constraints

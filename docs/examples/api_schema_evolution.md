# API Schema Evolution

Real-world example showing API schema evolution between versions.

## Schemas

### Old Schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer"
    },
    "name": {
      "type": "string"
    },
    "email": {
      "type": "string",
      "format": "email"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "settings": {
      "type": "object",
      "properties": {
        "notifications": {
          "type": "boolean"
        },
        "theme": {
          "type": "string",
          "enum": [
            "light",
            "dark"
          ]
        }
      }
    }
  },
  "required": [
    "id",
    "name",
    "email"
  ]
}
```

### New Schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string"
    },
    "name": {
      "type": "string"
    },
    "email": {
      "type": "string",
      "format": "email"
    },
    "phone": {
      "type": "string"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time"
    },
    "settings": {
      "type": "object",
      "properties": {
        "notifications": {
          "type": "boolean"
        },
        "theme": {
          "type": "string",
          "enum": [
            "light",
            "dark",
            "auto"
          ]
        },
        "language": {
          "type": "string",
          "default": "en"
        }
      }
    }
  },
  "required": [
    "id",
    "name",
    "email",
    "phone"
  ]
}
```

## Comparison Result

### Using compare_schemas()

```python
from jsonschema_diff import compare_schemas

old_schema = {
  "type": "object",
  "properties": {
    "id": {
      "type": "integer"
    },
    "name": {
      "type": "string"
    },
    "email": {
      "type": "string",
      "format": "email"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "settings": {
      "type": "object",
      "properties": {
        "notifications": {
          "type": "boolean"
        },
        "theme": {
          "type": "string",
          "enum": [
            "light",
            "dark"
          ]
        }
      }
    }
  },
  "required": [
    "id",
    "name",
    "email"
  ]
}

new_schema = {
  "type": "object",
  "properties": {
    "id": {
      "type": "string"
    },
    "name": {
      "type": "string"
    },
    "email": {
      "type": "string",
      "format": "email"
    },
    "phone": {
      "type": "string"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time"
    },
    "settings": {
      "type": "object",
      "properties": {
        "notifications": {
          "type": "boolean"
        },
        "theme": {
          "type": "string",
          "enum": [
            "light",
            "dark",
            "auto"
          ]
        },
        "language": {
          "type": "string",
          "default": "en"
        }
      }
    }
  },
  "required": [
    "id",
    "name",
    "email",
    "phone"
  ]
}

result = compare_schemas(old_schema, new_schema)
print(result)
```

### Output

```
[36m[1mr ["id"].type: "integer" -> "string"[0m

[36m[1mr ["settings"]["theme"].enum: ["light", "dark"] -> ["light", "dark", "auto"][0m

[32m[1m+ ["settings"]["language"]: {"type": "string", "default": "en"}[0m

[32m[1m+ ["phone"]: {"type": "string"}[0m

[32m[1m+ ["updated_at"]: {"type": "string", "format": "date-time"}[0m
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
- **Property Addition**: How new properties are displayed

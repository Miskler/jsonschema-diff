# Quick Start Guide

This guide will get you up and running with JSON Schema Diff in minutes.

## Installation

Install from PyPI:

```bash
pip install jsonschema-diff
```

Or install from source:

```bash
git clone https://github.com/your-username/jsonschema-diff.git
cd jsonschema-diff
pip install -e .
```

## Basic Usage

### Comparing Schemas in Python

The simplest way to compare schemas is using the `compare_schemas` function:

```python
from jsonschema_diff import compare_schemas

# Define your schemas
old_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer", "minimum": 0}
    },
    "required": ["name"]
}

new_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "format": "email"},  # format added
        "age": {"type": "integer", "minimum": 18},      # minimum changed
        "city": {"type": "string"}                      # new property
    },
    "required": ["name", "city"]  # city now required
}

# Compare and get formatted output
result = compare_schemas(old_schema, new_schema)
print(result)
```

### Using the SchemaComparator Class

For more control, use the `SchemaComparator` class directly:

```python
from jsonschema_diff import SchemaComparator

comparator = SchemaComparator(old_schema, new_schema)
result = comparator.compare()
print(result)
```

### Command Line Interface

Compare schema files directly from the command line:

```bash
# Compare two JSON files
jsonschema-diff old_schema.json new_schema.json

# Show help
jsonschema-diff --help
```

Example schema files:

**old_schema.json:**
```json
{
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer", "minimum": 0}
    }
}
```

**new_schema.json:**
```json
{
    "type": "object",
    "properties": {
        "name": {"type": "string", "format": "email"},
        "age": {"type": "integer", "minimum": 18},
        "email": {"type": "string", "format": "email"}
    }
}
```

## Understanding the Output

JSON Schema Diff produces colored, formatted output showing the differences:

```
+ ["email"]: "string/email"
r ["name"].format: "email"
r ["age"].minimum: 0 -> 18
```

### Output Format Legend

- `+` (green): Added property or value
- `-` (red): Removed property or value  
- `r` (cyan): Changed/replaced value
- ` ` (no symbol): Context information (unchanged but relevant)

### Path Format

Paths show the location of changes in the schema:

- `["name"]`: Property `name` in the root object
- `["user"].type`: The `type` property of the `user` object
- `.items[0].type`: The `type` of the first item in an array

## Key Features

### 1. Parameter Combination

Related parameters are automatically combined for cleaner output:

```python
# Instead of two separate changes:
# type: "string" -> "integer"
# format: "email" -> "number"

# Shows as one combined change:
# type: "string/email" -> "integer/number"
```

### 2. Context Information

When important properties change, related context is shown:

```python
# When type changes, format is shown for context
# type: "string" -> "integer"
#   format: "email"  # context - shows what format was
```

### 3. Intelligent Grouping

Changes are grouped logically with proper spacing:

```python
# Related changes are grouped together
# type: "string" -> "integer"
#   format: "email"

# Separated from other field changes
# minimum: 0 -> 18
```

## Advanced Usage

### Custom Configuration

You can access and understand the configuration:

```python
from jsonschema_diff.config import Config

# See what parameters trigger context display
context_params = Config.get_context_params("type")
print(f"When 'type' changes, show: {context_params}")

# View combination rules
rules = Config.get_combination_rules()
for rule in rules:
    print(f"Combine {rule.main_param} + {rule.sub_param} -> {rule.display_name}")
```

### Working with Complex Schemas

The library handles nested objects, arrays, and complex schema structures:

```python
complex_schema = {
    "type": "object",
    "properties": {
        "user": {
            "type": "object",
            "properties": {
                "profile": {
                    "type": "object",
                    "properties": {
                        "settings": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "key": {"type": "string"},
                                    "value": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

# Handles deep nesting automatically
result = compare_schemas(old_complex, new_complex)
```

## Next Steps

- Check out [Examples](examples/index.md) for more detailed usage scenarios
- Read about [Configuration](configuration.md) to customize behavior
- Explore the [API Reference](api/index.md) for detailed documentation
- See [Contributing](contributing.md) if you want to help improve the project

## Common Use Cases

### API Schema Evolution

Track changes in API schemas across versions:

```python
api_v1 = load_schema("api_v1.json")
api_v2 = load_schema("api_v2.json") 
changes = compare_schemas(api_v1, api_v2)
```

### Database Schema Migration

Compare database schemas represented as JSON:

```python
old_db_schema = load_schema("db_old.json")
new_db_schema = load_schema("db_new.json")
migration_changes = compare_schemas(old_db_schema, new_db_schema)
```

### Configuration Management

Track configuration schema changes:

```python
config_v1 = load_schema("config_v1.json")
config_v2 = load_schema("config_v2.json")
config_diff = compare_schemas(config_v1, config_v2)
```

# JSONSchema Diff

A Python library for comparing JSON schemas and displaying differences in a human-readable format with colored output.

## Features

- Compare two JSON schemas and identify differences
- Colored output using Click for better readability
- Support for nested schemas and complex structures
- Command-line interface for easy integration
- Modular design for programmatic usage

## Installation

### From source

```bash
git clone https://github.com/yourusername/jsonschema-diff.git
cd jsonschema-diff
pip install -e .
```

### For development

```bash
pip install -e ".[dev]"
```

## Usage

### As a Library

```python
from jsonschema_diff import compare_schemas

old_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"}
    }
}

new_schema = {
    "type": "object", 
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "email": {"type": "string"}
    }
}

diff = compare_schemas(old_schema, new_schema)
print(diff)
```

### Command Line Interface

```bash
# Compare two schema files
jsonschema-diff old_schema.json new_schema.json

# Save output to file
jsonschema-diff old_schema.json new_schema.json -o diff.txt

# Disable colored output
jsonschema-diff old_schema.json new_schema.json --no-color
```

## Output Format

The tool shows differences with colored symbols:
- `+` (green): Added properties
- `-` (red): Removed properties  
- `r` (cyan): Changed properties
- ` ` (default): Unchanged context

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black jsonschema_diff/
isort jsonschema_diff/
```

### Type Checking

```bash
mypy jsonschema_diff/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
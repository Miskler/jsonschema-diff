# JSON Schema Diff Documentation

Welcome to **JSON Schema Diff** - a powerful and flexible library for comparing JSON schemas with intelligent difference detection and beautiful formatting.

## 🚀 What is JSON Schema Diff?

JSON Schema Diff is a modern, modular library that provides:

- **Intelligent Comparison**: Detects and categorizes changes between JSON schemas
- **Configurable Parameter Combination**: Combines related parameters (e.g., `type` + `format`)
- **Context Visualization**: Shows related fields for better understanding
- **Beautiful Output**: Colored, formatted differences with proper spacing
- **Modular Architecture**: Clean, testable, and extensible design
- **High Test Coverage**: 99% test coverage ensures reliability

## 🏗️ Architecture Overview

The library uses a 5-stage pipeline architecture:

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│ DiffFinder  │───▶│ DiffProcessor │───▶│  Combiner   │
└─────────────┘    └──────────────┘    └─────────────┘
                                              │
┌─────────────┐    ┌──────────────┐          ▼
│  Formatter  │◀───│RenderProcessor│◀─────────┘
└─────────────┘    └──────────────┘
```

1. **DiffFinder**: Finds raw differences between schemas
2. **DiffProcessor**: Converts add/remove pairs to changes
3. **Combiner**: Combines related parameters using configurable rules
4. **RenderProcessor**: Adds context and prepares for rendering
5. **Formatter**: Formats output with proper spacing and colors

## 📖 Quick Start

### Installation

```bash
pip install jsonschema-diff
```

### Basic Usage

```python
from jsonschema_diff import compare_schemas

old_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "format": "email"},
        "age": {"type": "integer", "minimum": 0}
    }
}

new_schema = {
    "type": "object", 
    "properties": {
        "name": {"type": "string"},  # format removed
        "age": {"type": "integer", "minimum": 18},  # minimum changed
        "email": {"type": "string", "format": "email"}  # new field
    }
}

differences = compare_schemas(old_schema, new_schema)
print(differences)
```

**Output:**
```
- ["name"].format: "email"
r ["age"].minimum: 0 -> 18
+ ["email"]: {"format": "email", "type": "string"}
```
```

### CLI Usage

```bash
# Compare two schema files
jsonschema-diff schema_v1.json schema_v2.json

# Show help
jsonschema-diff --help
```

## 🎯 Key Features

### Parameter Combination

The library can intelligently combine related parameters:

```python
# Instead of showing separate changes:
# - type: "string" -> "integer"  
# - format: "email" -> "number"

# Shows combined change:
# type: "string/email" -> "integer/number"
```

### Context Visualization  

When important parameters change, related context is automatically shown:

```python
# When type changes, format is shown for context:
# type: "string" -> "integer"
#   format: "email"  # shown for context
```

### Configurable Rules

All combination and context rules are configurable through the `Config` class:

```python
from jsonschema_diff.config import Config, CombinationRule, CombineMode

# View current rules
rules = Config.get_combination_rules()
context_params = Config.get_context_params("type")
```

## 📚 Table of Contents

```{toctree}
:maxdepth: 2
:caption: User Guide

quickstart
examples/index
configuration
troubleshooting
```

```{toctree}
:maxdepth: 2
:caption: API Reference

api/index
```

```{toctree}
:maxdepth: 1
:caption: Development

contributing
changelog
```

## 🔗 Quick Links

- [Quick Start Guide](quickstart.md)
- [Examples](examples/index.md) 
- [API Reference](api/index.md)
- [Configuration](configuration.md)
- [GitHub Repository](https://github.com/your-username/jsonschema-diff)

## 📊 Project Stats

- **Test Coverage**: 99%+ 
- **Python Support**: 3.9+
- **Dependencies**: Minimal (optional `click` for colored CLI output)
- **License**: MIT
- **Architecture**: Modular, extensible pipeline

## 🛠️ Advanced Features

### Error Handling
- Graceful handling of malformed schemas
- Detailed error messages with context
- Validation warnings and suggestions

### Performance
- Efficient diff algorithms for large schemas
- Memory-optimized processing
- Lazy evaluation where possible

### Extensibility  
- Plugin architecture for custom formatters
- Configurable combination rules
- Custom context providers

---

*Built with ❤️ for developers working with evolving JSON schemas*

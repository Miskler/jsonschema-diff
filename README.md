# 🔍 JSON Schema Diff

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/your-org/jsonschema-diff)
[![Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen)](https://github.com/your-org/jsonschema-diff)
[![Python](https://img.shields.io/badge/python-3.9+-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

A powerful, intelligent library for comparing JSON schemas with **beautiful formatted output**, **smart parameter combination**, and **contextual information**.

## ✨ Features

- 🎯 **Intelligent Comparison** - Detects and categorizes all types of schema changes
- 🎨 **Beautiful Output** - Colored, formatted differences with clear symbols  
- 🔗 **Smart Combination** - Combines related parameters (e.g., `type` + `format`)
- 📍 **Context Aware** - Shows related fields for better understanding
- ⚡ **High Performance** - Efficient algorithms for large schemas
- 🧪 **99%+ Test Coverage** - Reliable and battle-tested
- 🛠️ **CLI & API** - Use programmatically or from command line
- 🔧 **Highly Configurable** - Customize behavior for your needs

## 🚀 Quick Start

### Installation

```bash
# Standard installation
pip install jsonschema-diff

# With CLI colors (recommended)
pip install "jsonschema-diff[cli]"
```

### 30-Second Example

```python
from jsonschema_diff import compare_schemas

# Your schemas
old = {"type": "string", "format": "email"}  
new = {"type": "integer", "minimum": 0}

# Compare them
print(compare_schemas(old, new))
```

**Output:**
```
r type: "string/email" -> "integer"
+ minimum: 0
```

✨ **Notice**: `type` and `format` were automatically combined for cleaner output!

### CLI Usage

```bash
# Compare schema files
jsonschema-diff schema_v1.json schema_v2.json

# No colors (for logs/CI)
jsonschema-diff --no-color schema_v1.json schema_v2.json
```

## 📊 Output Format

| Symbol | Meaning | Color | Example |
|--------|---------|-------|---------|
| `+` | Added | 🟢 Green | `+ ["new_field"]: "string"` |
| `-` | Removed | 🔴 Red | `- ["old_field"]: "string"` |
| `r` | Changed | 🔵 Cyan | `r ["field"]: "old" -> "new"` |
| ` ` | Context | ⚪ None | `  ["related"]: "unchanged"` |

## 🎯 Real-World Example

```python
old_schema = {
    "type": "object",
    "properties": {
        "user": {
            "type": "object", 
            "properties": {
                "name": {"type": "string", "format": "email"},
                "age": {"type": "integer", "minimum": 0, "maximum": 120}
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
                "name": {"type": "string"},  # format removed
                "age": {"type": "integer", "minimum": 18, "maximum": 120},  # min changed
                "email": {"type": "string", "format": "email"}  # new field
            }
        }
    }
}

print(compare_schemas(old_schema, new_schema))
```

**Output:**
```
- ["user"]["name"].format: "email"
r ["user"]["age"].minimum: 0 -> 18
  ["user"]["age"].maximum: 120                    # context
+ ["user"]["email"]: {"format": "email", "type": "string"}
```

## 🏗️ Architecture

Modern 5-stage pipeline for clean, testable code:

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│ DiffFinder  │───▶│ DiffProcessor │───▶│  Combiner   │
└─────────────┘    └──────────────┘    └─────────────┘
                                              │
┌─────────────┐    ┌──────────────┐          ▼
│  Formatter  │◀───│RenderProcessor│◀─────────┘
└─────────────┘    └──────────────┘
```

1. **DiffFinder**: Finds raw differences
2. **DiffProcessor**: Converts add/remove pairs to changes  
3. **Combiner**: Combines related parameters
4. **RenderProcessor**: Adds context information
5. **Formatter**: Beautiful colored output

## 🛠️ Development

### Setup

```bash
git clone https://github.com/your-org/jsonschema-diff.git
cd jsonschema-diff
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Commands

```bash
make test          # Run tests with coverage
make lint          # Lint code
make type-check    # Type checking  
make format        # Format code
make docs          # Build documentation
make ci-test       # Full CI pipeline
```

## 📚 Documentation

- **[📖 Full Documentation](https://your-org.github.io/jsonschema-diff/)**
- **[🚀 Quick Start Guide](https://your-org.github.io/jsonschema-diff/quickstart.html)**
- **[⚙️ Configuration](https://your-org.github.io/jsonschema-diff/configuration.html)**
- **[🔧 API Reference](https://your-org.github.io/jsonschema-diff/api/)**
- **[🐛 Troubleshooting](https://your-org.github.io/jsonschema-diff/troubleshooting.html)**

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](docs/contributing.md) for details.

### Quick Contribution Setup

```bash
# Fork the repo, then:
git clone https://github.com/your-username/jsonschema-diff.git
cd jsonschema-diff
make install-dev
make test  # Ensure everything works
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

<div align="center">

**[⭐ Star us on GitHub](https://github.com/your-org/jsonschema-diff)** | **[📚 Read the Docs](https://your-org.github.io/jsonschema-diff/)** | **[🐛 Report Bug](https://github.com/your-org/jsonschema-diff/issues)**

*Made with ❤️ for developers working with evolving JSON schemas*

</div>
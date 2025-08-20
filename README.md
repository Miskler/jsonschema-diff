
<div align="center">

# 🔍 JSON Schema Diff

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/your-org/jsonschema-diff)
[![Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen)](https://github.com/your-org/jsonschema-diff)
[![Python](https://img.shields.io/badge/python-3.9+-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

A powerful, intelligent library for comparing JSON schemas with **beautiful formatted output**, **smart parameter combination**, and **contextual information**.

## ✨ Features

</div>

- 🎯 **Intelligent Comparison** - Detects and categorizes all types of schema changes
- 🎨 **Beautiful Output** - Colored, formatted differences with clear symbols  
- 🔗 **Smart Combination** - Combines related parameters (e.g., `minimum` + `maximum` = `range`)
- 📍 **Context Aware** - Shows related fields for better understanding (e.g., `type` + `format`)
- ⚡ **High Performance** - Efficient algorithms for large schemas
- 🛠️ **CLI & Python API & Sphinx Extension** - Use programmatically or from command line or in `.rst`
- 🔧 **Highly Configurable** - Customize behavior for your needs

<div align="center">

## 🚀 Quick Start

</div>

### Installation

```bash
# Standard installation
pip install jsonschema-diff
```

### 30-Second Example

```python
from jsonschema_diff import JsonSchemaDiff, ConfigMaker
from jsonschema_diff.color import HighlighterPipeline
from jsonschema_diff.color.stages import (
    MonoLinesHighlighter, ReplaceGenericHighlighter, PathHighlighter
)

prop = JsonSchemaDiff(
    config=ConfigMaker.make(),
    colorize_pipeline=HighlighterPipeline([
        MonoLinesHighlighter(),
        ReplaceGenericHighlighter(),
        PathHighlighter(),
    ])
)

prop.compare(
    old_schema="context.old.schema.json",
    new_schema="context.new.schema.json"
)

prop.print(with_legend=True)
```

**Output:**
![example_working.svg](./example_working.svg)


### CLI Usage

```bash
# Compare schema files
jsonschema-diff schema_v1.json schema_v2.json

# No colors (for logs/CI) and with exit-code
jsonschema-diff --no-color --exit-code schema_v1.json schema_v2.json

# Compare JSON strings
jsonschema-diff "{\"type\":\"string\"}" "{\"type\":\"number\"}"
```


### Sphinx Extension

Use the extension in your build:

```python
extensions += ["jsonschema_diff.sphinx"]
```

You must also configure the extension. Add the following variable to your `conf.py`:

```python
from jsonschema_diff import ConfigMaker, JsonSchemaDiff
from jsonschema_diff.color import HighlighterPipeline
from jsonschema_diff.color.stages import (
    MonoLinesHighlighter, PathHighlighter, ReplaceGenericHighlighter,
)

jsonschema_diff = JsonSchemaDiff(
    config=ConfigMaker.make(),
    colorize_pipeline=HighlighterPipeline(
        [MonoLinesHighlighter(), ReplaceGenericHighlighter(), PathHighlighter()],
    ),
)
```

After that, you can use it in your `.rst` files:

```rst
.. jsonschemadiff:: path/to/file.old.schema.json path/to/file.new.schema.json # from folder `source`
    :name: filename.svg # optional
    :title: Title in virtual terminal # optional
    :no-legend: # optional
```


<div align="center">

## 📊 Output Format

| Symbol | Meaning | Color | Example |
|--------|---------|-------|---------|
| `+` | Added | 🟢 Green | `+ ["new_field"].field: "string"` |
| `-` | Removed | 🔴 Red | `- ["old_field"].field: "string"` |
| `r` | Changed | 🔵 Cyan | `r ["field"].field: "old" -> "new"` |
| `m` | Modified | 🔵 Cyan | `m ["field"]: ...` |
| ` ` | Context | ⚪ None | `  ["related"]: "unchanged"` |

## 🏗️ Architecture

</div>

Modern 6-stage pipeline for clean, testable code:

```
┌─────────────┐    ┌───────────────┐    ┌──────────────────┐
│ DiffFinder  │───▶│ CompareFinder │───▶│ CombineProcessor │
└─────────────┘    └───────────────┘    └──────────────────┘
                                                  ▼
┌─────────────┐    ┌───────────────┐      ┌───────────────┐
│  Formatter  │◀───│RenderProcessor│◀─────│ DiffProcessor │
└─────────────┘    └───────────────┘      └───────────────┘
```

1. **DiffFinder**: Finds raw differences
2. **CompareProcessor**: Find class-processors
3. **Combiner**: Combines related parameters
4. **RenderProcessor**: Adds context information and render
5. **Formatter**: Beautiful colored output

<div align="center">

## 🛠️ Development

</div>

### Setup

```bash
git clone https://github.com/your-org/jsonschema-diff.git
cd jsonschema-diff
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
make build
make install-dev
```

### Commands

```bash
# Checks
make test          # Run tests with coverage
make lint          # Lint code
make type-check    # Type checking  
# Action
make format        # Format code
make docs          # Build documentation
```

<div align="center">

## 📚 Documentation

</div>

- **[📖 Full Documentation](https://your-org.github.io/jsonschema-diff/)**
- **[🚀 Quick Start Guide](https://your-org.github.io/jsonschema-diff/quickstart.html)**
- **[⚙️ Configuration](https://your-org.github.io/jsonschema-diff/configuration.html)**
- **[🔧 API Reference](https://your-org.github.io/jsonschema-diff/api/)**
- **[🐛 Troubleshooting](https://your-org.github.io/jsonschema-diff/troubleshooting.html)**

<div align="center">

## 🤝 Contributing

### ***We welcome contributions!***

### Quick Contribution Setup

</div>

```bash
# Fork the repo, then:
git clone https://github.com/your-username/jsonschema-diff.git
cd jsonschema-diff
# Install
make build
make install-dev
# Ensure everything works
make test
make lint
make type-check
```

<div align="center">

## 📄 License

</div>

MIT License - see [LICENSE](LICENSE) file for details.

---

<div align="center">

**[⭐ Star us on GitHub](https://github.com/your-org/jsonschema-diff)** | **[📚 Read the Docs](https://your-org.github.io/jsonschema-diff/)** | **[🐛 Report Bug](https://github.com/your-org/jsonschema-diff/issues)**

*Made with ❤️ for developers working with evolving JSON schemas*

</div>
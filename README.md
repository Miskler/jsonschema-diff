
<div align="center">

# 🔍 JSON Schema Diff

<img src="https://raw.githubusercontent.com/Miskler/jsonschema-diff/refs/heads/main/assets/logo.webp" width="70%" alt="logo.webp" />

*A powerful, intelligent library for comparing JSON schemas with **beautiful formatted output**, **smart parameter combination**, and **contextual information**.*

[![Tests](https://miskler.github.io/jsonschema-diff/tests-badge.svg)](https://miskler.github.io/jsonschema-diff/tests/tests-report.html)
[![Coverage](https://miskler.github.io/jsonschema-diff/coverage.svg)](https://miskler.github.io/jsonschema-diff/coverage/)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![PyPI - Package Version](https://img.shields.io/pypi/v/jsonschema-diff?color=blue)](https://pypi.org/project/jsonschema-diff/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![BlackCode](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)
[![mypy](https://img.shields.io/badge/type--checked-mypy-blue?logo=python)](https://mypy.readthedocs.io/en/stable/index.html)
[![Discord](https://img.shields.io/discord/792572437292253224?label=Discord&labelColor=%232c2f33&color=%237289da)](https://discord.gg/UnJnGHNbBp)
[![Telegram](https://img.shields.io/badge/Telegram-24A1DE)](https://t.me/miskler_dev)


**[⭐ Star us on GitHub](https://github.com/Miskler/jsonschema-diff)** | **[📚 Read the Docs](https://miskler.github.io/jsonschema-diff/basic/quick_start/)** | **[🐛 Report Bug](https://github.com/Miskler/jsonschema-diff/issues)**

## ✨ Features

</div>

- 🎯 **Intelligent Comparison** - Detects and categorizes all types of schema changes
- 🎨 **Beautiful Output** - Colored, formatted differences with clear symbols  
- 🔗 **Smart Combination** - Combines related parameters *(e.g., `minimum` + `maximum` = `range`)*
- 📍 **Context Aware** - Shows related fields for better understanding *(e.g., `type` + `format`)*
- 🔄 **Semantic Array Diff** - Ignores pure reorder noise and reports only real adds/removes/changes
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
![./assets/example_working.svg](https://raw.githubusercontent.com/Miskler/jsonschema-diff/refs/heads/main/assets/example_working.svg)

### Why It Beats Line-Based Diffs For Schemas

For array-like schema parts, this library performs a semantic diff:

- Pure reorder does not create noisy changes
- `dict` elements are matched by structure (not by position)
- Scalar elements are matched by value multiplicity (multiset logic)

Example:

```text
[1, 2, 3] -> [3, 1, 2, 1]
```

A line-based diff typically reports multiple moved lines.
`jsonschema-diff` reports just one meaningful change: `+ 1`.


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
git clone https://github.com/Miskler/jsonschema-diff.git
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

- **[📖 Full Documentation](https://miskler.github.io/jsonschema-diff/)**
- **[🚀 Quick Start Guide](https://miskler.github.io/jsonschema-diff/basic/quick_start/)**
- **[🔧 API Reference](https://miskler.github.io/jsonschema-diff/reference/api/index.html)**

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

MIT License - see [LICENSE](LICENSE) file for details.

*Made with ❤️ for developers working with evolving JSON schemas*

</div>

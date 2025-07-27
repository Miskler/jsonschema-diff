# API Reference

This section provides detailed API documentation for all modules and classes in JSON Schema Diff.

## Core Modules

The library is organized into several focused modules:

```{toctree}
:maxdepth: 2

comparator
config
combiner
formatter
diff_finder
diff_processor
render_processor
path_utils
context_manager
cli
```

## Quick Reference

### Main Functions

```{eval-rst}
.. autofunction:: jsonschema_diff.compare_schemas
```

### Core Classes

```{eval-rst}
.. autoclass:: jsonschema_diff.SchemaComparator
   :members:
   :show-inheritance:
```

## Module Overview

| Module | Purpose | Key Classes |
|--------|---------|-------------|
| `comparator` | Main comparison orchestration | `SchemaComparator` |
| `config` | Configuration and rules | `Config`, `CombineMode` |
| `combiner` | Parameter combination logic | `ParameterCombiner` |
| `formatter` | Output formatting | `Formatter` |
| `diff_finder` | Raw difference detection | `DiffFinder` |
| `diff_processor` | Difference processing | `DiffProcessor` |
| `render_processor` | Rendering preparation | `RenderProcessor` |
| `path_utils` | Path utilities | `PathUtils` |
| `context_manager` | Context information | `ContextManager` |
| `cli` | Command line interface | CLI functions |

## Architecture Flow

```
Input Schemas
     ↓
DiffFinder (finds raw differences)
     ↓  
DiffProcessor (converts add/remove to change)
     ↓
Combiner (combines related parameters)
     ↓
RenderProcessor (adds context, groups)
     ↓
Formatter (creates final output)
     ↓
Formatted Result
```

## Configuration System

The library uses a sophisticated configuration system with type-safe dataclasses:

- **DisplayMode**: Controls colors and symbols for different change types
- **CombinationRule**: Defines how parameters should be combined
- **ContextRule**: Specifies when to show context information
- **CombineMode**: Enum controlling when combination should occur

See the [Configuration Guide](../configuration.md) for details on customizing behavior.

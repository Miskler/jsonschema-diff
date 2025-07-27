# Command Line Interface

```{eval-rst}
.. automodule:: jsonschema_diff.cli
   :members:
   :undoc-members:
   :show-inheritance:
```

## Overview

The `cli` module provides the command-line interface for the jsonschema-diff tool. It handles argument parsing, file loading, and output formatting.

## Key Functions

### main

The main entry point for the CLI application.

## Features

- File input/output handling
- Command-line argument parsing
- Error handling and reporting
- Color output control
- Unicode support

## Usage

```bash
# Basic comparison
jsonschema-diff schema1.json schema2.json

# Save output to file
jsonschema-diff schema1.json schema2.json --output diff.txt

# Disable color output
jsonschema-diff schema1.json schema2.json --no-color
```

## Examples

```python
# Direct usage
from jsonschema_diff.cli import main
import sys

sys.argv = ['jsonschema-diff', 'schema1.json', 'schema2.json']
main()
```

# Render Processor

```{eval-rst}
.. automodule:: jsonschema_diff.render_processor
   :members:
   :undoc-members:
   :show-inheritance:
```

## Overview

The `render_processor` module is the fourth stage in the comparison pipeline. It prepares differences for rendering by adding context information and creating structured output groups.

## Key Classes

### RenderProcessor
### DiffLine
### DiffGroup

## Features

- Adds contextual information to differences
- Groups related changes together
- Metadata-driven approach
- Structured output preparation

## Examples

```python
from jsonschema_diff.render_processor import RenderProcessor

processor = RenderProcessor(old_schema, new_schema)
render_groups = processor.process_for_render(differences)
```

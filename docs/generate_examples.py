#!/usr/bin/env python3
"""
Automatic example generator for JSON Schema Diff documentation.

This script generates live examples by running actual comparisons
and capturing the output for documentation.
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from jsonschema_diff import compare_schemas, SchemaComparator
from jsonschema_diff.config import Config


class ExampleGenerator:
    """Generates documentation examples with live output."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.examples = []
        
    def add_example(self, name: str, description: str, old_schema: Dict[str, Any], 
                   new_schema: Dict[str, Any], tags: List[str] = None):
        """Add an example to be generated."""
        example = {
            'name': name,
            'description': description,
            'old_schema': old_schema,
            'new_schema': new_schema,
            'tags': tags or [],
        }
        self.examples.append(example)
        
    def generate_all(self):
        """Generate all examples and create documentation files."""
        # Create examples directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate individual example files
        for example in self.examples:
            self._generate_example_file(example)
            
        # Generate index file
        self._generate_index_file()
        
    def _generate_example_file(self, example: Dict[str, Any]):
        """Generate a single example file."""
        name = example['name']
        safe_name = name.lower().replace(' ', '_').replace('-', '_')
        
        # Disable colors for documentation
        Config.set_use_colors(False)
        
        # Run the actual comparison
        try:
            result = compare_schemas(example['old_schema'], example['new_schema'])
        except Exception as e:
            result = f"Error: {e}"
            
        # Create the markdown content
        content = f"""# {name}

{example['description']}

## Schemas

### Old Schema

```json
{json.dumps(example['old_schema'], indent=2)}
```

### New Schema

```json
{json.dumps(example['new_schema'], indent=2)}
```

## Comparison Result

### Using compare_schemas()

```python
from jsonschema_diff import compare_schemas

old_schema = {json.dumps(example['old_schema'], indent=2)}

new_schema = {json.dumps(example['new_schema'], indent=2)}

result = compare_schemas(old_schema, new_schema)
print(result)
```

### Output

```
{result}
```

### Using SchemaComparator class

```python
from jsonschema_diff import SchemaComparator

comparator = SchemaComparator(old_schema, new_schema)
result = comparator.compare()
```

## Analysis

This example demonstrates:

"""
        
        # Add analysis based on tags
        if 'type_change' in example['tags']:
            content += "- **Type Changes**: How the library handles changes to field types\n"
        if 'format_change' in example['tags']:
            content += "- **Format Changes**: Detection of format attribute modifications\n"
        if 'combination' in example['tags']:
            content += "- **Parameter Combination**: How related parameters are combined for clarity\n"
        if 'context' in example['tags']:
            content += "- **Context Display**: Showing related fields for better understanding\n"
        if 'nested' in example['tags']:
            content += "- **Nested Objects**: Handling of complex nested schema structures\n"
        if 'array' in example['tags']:
            content += "- **Array Handling**: Changes in array items and their schemas\n"
        if 'validation' in example['tags']:
            content += "- **Validation Rules**: Changes to validation constraints\n"
        if 'addition' in example['tags']:
            content += "- **Property Addition**: How new properties are displayed\n"
        if 'removal' in example['tags']:
            content += "- **Property Removal**: Detection and display of removed properties\n"
            
        # Write the file
        file_path = self.output_dir / f"{safe_name}.md"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Generated example: {file_path}")
        
    def _generate_index_file(self):
        """Generate the examples index file."""
        content = """# Examples

This section contains comprehensive examples showing various features and use cases of JSON Schema Diff.

All examples show **live output** generated automatically from the actual library code.

## Categories

### Basic Usage
"""
        
        # Group examples by category
        basic_examples = [ex for ex in self.examples if 'basic' in ex['tags']]
        advanced_examples = [ex for ex in self.examples if 'advanced' in ex['tags']]
        real_world_examples = [ex for ex in self.examples if 'real_world' in ex['tags']]
        
        # Add basic examples
        for example in basic_examples:
            safe_name = example['name'].lower().replace(' ', '_').replace('-', '_')
            content += f"- [{example['name']}]({safe_name}.md): {example['description']}\n"
            
        if advanced_examples:
            content += "\n### Advanced Features\n\n"
            for example in advanced_examples:
                safe_name = example['name'].lower().replace(' ', '_').replace('-', '_')
                content += f"- [{example['name']}]({safe_name}.md): {example['description']}\n"
                
        if real_world_examples:
            content += "\n### Real-World Scenarios\n\n"
            for example in real_world_examples:
                safe_name = example['name'].lower().replace(' ', '_').replace('-', '_')
                content += f"- [{example['name']}]({safe_name}.md): {example['description']}\n"
                
        content += """
## Features Demonstrated

- **Parameter Combination**: See how `type` and `format` are combined
- **Context Display**: Related fields shown for clarity
- **Nested Structures**: Complex object and array handling
- **Validation Rules**: Changes to constraints like `minimum`, `maximum`
- **Array Items**: Modifications to array item schemas
- **Property Operations**: Additions, removals, and modifications

## Interactive Examples

All examples include:
- ✅ Complete schema definitions
- ✅ Live comparison output  
- ✅ Python code snippets
- ✅ Feature analysis
- ✅ Use case explanations

```{toctree}
:maxdepth: 1

"""
        
        # Add all examples to toctree
        for example in self.examples:
            safe_name = example['name'].lower().replace(' ', '_').replace('-', '_')
            content += f"{safe_name}\n"
            
        content += "```\n"
        
        # Write index file
        index_path = self.output_dir / "index.md"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Generated index: {index_path}")


def main():
    """Main function to generate all examples."""
    docs_dir = Path(__file__).parent
    examples_dir = docs_dir / "examples"
    
    generator = ExampleGenerator(examples_dir)
    
    # Basic type change example
    generator.add_example(
        name="Basic Type Change",
        description="Simple example showing how type changes are displayed.",
        old_schema={
            "type": "object",
            "properties": {
                "age": {"type": "string"}
            }
        },
        new_schema={
            "type": "object", 
            "properties": {
                "age": {"type": "integer"}
            }
        },
        tags=['basic', 'type_change']
    )
    
    # Type and format combination
    generator.add_example(
        name="Type and Format Combination",
        description="Shows how type and format changes are combined into a single display.",
        old_schema={
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email"}
            }
        },
        new_schema={
            "type": "object",
            "properties": {
                "email": {"type": "integer", "format": "number"}
            }
        },
        tags=['basic', 'combination', 'type_change', 'format_change']
    )
    
    # Context display example
    generator.add_example(
        name="Context Display",
        description="Demonstrates how related context information is shown when important fields change.",
        old_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "format": "email"}
            }
        },
        new_schema={
            "type": "object",
            "properties": {
                "name": {"type": "integer", "format": "email"}
            }
        },
        tags=['basic', 'context', 'type_change']
    )
    
    # Validation rules
    generator.add_example(
        name="Validation Rules",
        description="Shows changes to validation constraints like minimum and maximum values.",
        old_schema={
            "type": "object",
            "properties": {
                "age": {"type": "integer", "minimum": 0, "maximum": 120},
                "score": {"type": "number", "minimum": 0.0, "maximum": 100.0}
            }
        },
        new_schema={
            "type": "object",
            "properties": {
                "age": {"type": "integer", "minimum": 18, "maximum": 65},
                "score": {"type": "number", "minimum": 0.0, "maximum": 10.0}
            }
        },
        tags=['basic', 'validation', 'context']
    )
    
    # Property addition/removal
    generator.add_example(
        name="Property Operations", 
        description="Demonstrates addition and removal of properties.",
        old_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "old_field": {"type": "string"},
                "email": {"type": "string", "format": "email"}
            }
        },
        new_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "new_field": {"type": "string"},
                "phone": {"type": "string"}
            }
        },
        tags=['basic', 'addition', 'removal']
    )
    
    # Nested objects
    generator.add_example(
        name="Nested Objects",
        description="Complex example with nested object structures.",
        old_schema={
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "profile": {
                            "type": "object", 
                            "properties": {
                                "name": {"type": "string"},
                                "age": {"type": "integer", "minimum": 0}
                            }
                        }
                    }
                }
            }
        },
        new_schema={
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "profile": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "format": "email"},
                                "age": {"type": "integer", "minimum": 18}
                            }
                        }
                    }
                }
            }
        },
        tags=['advanced', 'nested', 'type_change', 'validation']
    )
    
    # Array handling
    generator.add_example(
        name="Array Items",
        description="Shows how changes to array item schemas are handled.",
        old_schema={
            "type": "object",
            "properties": {
                "tags": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "scores": {
                    "type": "array", 
                    "items": {"type": "integer", "minimum": 0}
                }
            }
        },
        new_schema={
            "type": "object",
            "properties": {
                "tags": {
                    "type": "array",
                    "items": {"type": "string", "format": "uri"}
                },
                "scores": {
                    "type": "array",
                    "items": {"type": "number", "minimum": 0.0}
                }
            }
        },
        tags=['advanced', 'array', 'type_change', 'format_change']
    )
    
    # Real-world API example
    generator.add_example(
        name="API Schema Evolution",
        description="Real-world example showing API schema evolution between versions.",
        old_schema={
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "email": {"type": "string", "format": "email"},
                "created_at": {"type": "string", "format": "date-time"},
                "settings": {
                    "type": "object",
                    "properties": {
                        "notifications": {"type": "boolean"},
                        "theme": {"type": "string", "enum": ["light", "dark"]}
                    }
                }
            },
            "required": ["id", "name", "email"]
        },
        new_schema={
            "type": "object",
            "properties": {
                "id": {"type": "string"},  # Changed to string for UUIDs
                "name": {"type": "string"},
                "email": {"type": "string", "format": "email"},
                "phone": {"type": "string"},  # Added phone field
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": "string", "format": "date-time"},  # Added
                "settings": {
                    "type": "object",
                    "properties": {
                        "notifications": {"type": "boolean"},
                        "theme": {"type": "string", "enum": ["light", "dark", "auto"]},  # Added auto
                        "language": {"type": "string", "default": "en"}  # Added language
                    }
                }
            },
            "required": ["id", "name", "email", "phone"]  # Phone now required
        },
        tags=['real_world', 'api', 'type_change', 'addition', 'nested']
    )
    
    # Generate all examples
    generator.generate_all()
    print(f"\n✅ Generated {len(generator.examples)} examples in {examples_dir}")


if __name__ == "__main__":
    main()

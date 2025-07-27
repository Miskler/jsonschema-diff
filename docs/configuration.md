# Configuration Guide

JSON Schema Diff provides extensive configuration options to customize comparison behavior. All configuration is type-safe and uses immutable dataclasses.

## Overview

The configuration system controls:

- **Display Formatting**: Colors and symbols for different change types
- **Parameter Combination**: Which parameters are combined and when
- **Context Display**: What related information to show
- **Operation Behavior**: How different operations are handled

## Display Configuration

### Display Modes

Control how different types of changes are displayed:

```python
from jsonschema_diff.config import Config

# Available display modes
modes = {
    'append': DisplayMode(color="green", symbol="+"),   # Added items
    'remove': DisplayMode(color="red", symbol="-"),     # Removed items  
    'replace': DisplayMode(color="cyan", symbol="r"),   # Changed items
    'no_diff': DisplayMode(color="reset", symbol=" "),  # Context items
}

# Access display modes
append_mode = Config.get_display_mode("append")
print(f"Symbol: {append_mode.symbol}, Color: {append_mode.color}")
```

### Output Format

The display modes control the visual appearance of differences:

```
+ ["new_field"]: "string"           # Green plus for additions
- ["old_field"]: "string"           # Red minus for removals  
r ["changed_field"]: "old" -> "new" # Cyan 'r' for changes
  ["context_field"]: "value"        # No color for context
```

## Parameter Combination

### Combination Rules

Define which parameters should be combined for cleaner output:

```python
from jsonschema_diff.config import Config

# Get all combination rules
rules = Config.get_combination_rules()

for rule in rules:
    print(f"Combine {rule.main_param} + {rule.sub_param}")
    print(f"Display as: {rule.display_name}")
    print(f"Template: {rule.format_template}")
    print(f"Rules: {rule.rules}")
    print("---")
```

### Default Combination Rules

#### Type + Format Combination

```python
# Instead of showing:
# type: "string" -> "integer"
# format: "email" -> "number"

# Shows combined:
# type: "string/email" -> "integer/number"

CombinationRule(
    main_param="type",
    sub_param="format",
    display_name="type",
    format_template="{main}/{sub}",
    rules=CombinationRules(
        removal=CombineMode.ALL,    # Combine for removals
        addition=CombineMode.ALL,   # Combine for additions
        change=CombineMode.ALL      # Combine for changes
    )
)
```

#### Range Combination (Minimum + Maximum)

```python
# For changes only, combines:
# minimum: 0, maximum: 100 -> "0-100"

CombinationRule(
    main_param="minimum",
    sub_param="maximum", 
    display_name="range",
    format_template="{main}-{sub}",
    rules=CombinationRules(
        removal=CombineMode.NONE,   # Don't combine for removals
        addition=CombineMode.NONE,  # Don't combine for additions
        change=CombineMode.ALL      # Only combine for changes
    )
)
```

### Combination Modes

Control when combination should occur:

```python
from jsonschema_diff.config import CombineMode

# Available modes:
CombineMode.ALL        # Always combine both parameters
CombineMode.MAIN_ONLY  # Only combine if main parameter changes
CombineMode.SUB_ONLY   # Only combine if sub parameter changes
CombineMode.NONE       # Never combine
```

## Context Display

### Context Rules

Define what related information to show when important fields change:

```python
from jsonschema_diff.config import Config

# Get context parameters for a field
context_params = Config.get_context_params("type")
print(context_params)  # ["format"]

# When 'type' changes, 'format' is shown for context
```

### Default Context Rules

```python
CONTEXT_RULES = [
    # When type changes, show format for context
    ContextRule(trigger_param="type", context_params=["format"]),
    
    # When minimum changes, show maximum for context
    ContextRule(trigger_param="minimum", context_params=["maximum"]),
    
    # When maximum changes, show minimum for context  
    ContextRule(trigger_param="maximum", context_params=["minimum"]),
    
    # When additionalProperties changes, show type for context
    ContextRule(trigger_param="additionalProperties", context_params=["type"]),
]
```

### Context Display Example

```python
# Schema change:
old_schema = {"type": "string", "format": "email"}
new_schema = {"type": "integer", "format": "email"}

# Output with context:
# type: "string" -> "integer"
#   format: "email"  # shown for context
```

## Understanding Configuration Flow

### 1. Difference Detection

```python
# DiffFinder detects raw differences
differences = [
    (["properties", "email", "type"], "string", "integer"),
    (["properties", "email", "format"], "email", "email")  # no change
]
```

### 2. Combination Processing

```python
# Combiner checks rules and may combine related parameters
# If type+format rule applies:
combined = [
    (["properties", "email", "type"], "string/email", "integer/email")
]
```

### 3. Context Addition

```python
# RenderProcessor adds context based on rules
# If type change triggers format context:
with_context = [
    DiffGroup(
        main_line=DiffLine(path=["properties", "email", "type"], ...),
        context_lines=[
            DiffLine(path=["properties", "email", "format"], ...)
        ]
    )
]
```

### 4. Formatting

```python
# Formatter applies display modes and creates final output
output = """
r ["email"].type: "string/email" -> "integer/email"
  ["email"].format: "email"
"""
```

## Advanced Configuration Scenarios

### Virtual Parameter Creation

When combination rules are active, the system can create "virtual" parameters from schema context:

```python
# If only type changes but format exists in schema:
old_schema = {"type": "string", "format": "email"}
new_schema = {"type": "integer", "format": "email"}

# Combiner creates virtual format difference for combination:
# type: "string/email" -> "integer/email"
```

### Operation-Specific Behavior

Different combination modes for different operations:

```python
# Example: Only combine for changes, not additions/removals
CombinationRules(
    removal=CombineMode.NONE,     # Don't combine when removing
    addition=CombineMode.NONE,    # Don't combine when adding
    change=CombineMode.ALL        # Do combine when changing
)
```

### Context Value Resolution

Context values are resolved from schemas:

```python
# Priority order:
# 1. Try old schema first
# 2. Fall back to new schema
# 3. Return None if not found

context_value = context_manager._find_context_value(context_path)
```

## Configuration Best Practices

### 1. Understanding Combinations

- Use combinations to reduce noise in output
- Combine logically related parameters
- Consider operation-specific rules

### 2. Context Usage

- Show context for important changes
- Avoid excessive context that clutters output
- Focus on truly related information

### 3. Display Clarity

- Use distinct symbols and colors
- Maintain consistency across operations
- Consider accessibility (color-blind users)

## Future Extensibility

The configuration system is designed for future extensibility:

- Type-safe dataclass foundation
- Modular rule system
- Clear separation of concerns
- Immutable configuration prevents accidental changes

```python
# Future: Custom configuration loading
# config = Config.load_from_file("custom_config.json")
# comparator = SchemaComparator(old, new, config=config)
```

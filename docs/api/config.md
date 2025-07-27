# Configuration Module

The `config` module provides type-safe configuration for all aspects of schema comparison.

## Overview

This module defines dataclasses and enums that control:
- Display formatting (colors, symbols)
- Parameter combination rules
- Context display rules
- Operation-specific behavior

## Classes and Enums

```{eval-rst}
.. automodule:: jsonschema_diff.config
   :members:
   :undoc-members:
   :show-inheritance:
```

## Configuration Classes

### CombineMode Enum

Controls when parameter combination should occur:

```python
from jsonschema_diff.config import CombineMode

# Available modes:
CombineMode.ALL        # Combine for all operations
CombineMode.MAIN_ONLY  # Only combine main parameter
CombineMode.SUB_ONLY   # Only combine sub parameter  
CombineMode.NONE       # Never combine
```

### DisplayMode

Defines formatting for different change types:

```python
from jsonschema_diff.config import DisplayMode

# Example display mode
mode = DisplayMode(color="green", symbol="+")
```

### CombinationRule

Defines how parameters should be combined:

```python
from jsonschema_diff.config import CombinationRule, CombinationRules, CombineMode

rule = CombinationRule(
    main_param="type",
    sub_param="format", 
    display_name="type",
    format_template="{main}/{sub}",
    rules=CombinationRules(
        removal=CombineMode.ALL,
        addition=CombineMode.ALL,
        change=CombineMode.ALL
    )
)
```

### ContextRule

Specifies context parameters to show:

```python
from jsonschema_diff.config import ContextRule

rule = ContextRule(
    trigger_param="type",
    context_params=["format"]
)
```

## Default Configuration

### Display Modes

```python
MODES = {
    'append': DisplayMode(color="green", symbol="+"),
    'remove': DisplayMode(color="red", symbol="-"),
    'replace': DisplayMode(color="cyan", symbol="r"),
    'no_diff': DisplayMode(color="reset", symbol=" "),
}
```

### Context Rules

```python
CONTEXT_RULES = [
    ContextRule(trigger_param="type", context_params=["format"]),
    ContextRule(trigger_param="minimum", context_params=["maximum"]),
    ContextRule(trigger_param="maximum", context_params=["minimum"]),
    ContextRule(trigger_param="additionalProperties", context_params=["type"]),
]
```

### Combination Rules

```python
COMBINATION_RULES = [
    # type + format = "string/email"
    CombinationRule(
        main_param="type",
        sub_param="format",
        display_name="type",
        format_template="{main}/{sub}",
        rules=CombinationRules(
            removal=CombineMode.ALL,
            addition=CombineMode.ALL, 
            change=CombineMode.ALL
        )
    ),
    # minimum + maximum = "0-100" (only for changes)
    CombinationRule(
        main_param="minimum",
        sub_param="maximum",
        display_name="range",
        format_template="{main}-{sub}",
        rules=CombinationRules(
            removal=CombineMode.NONE,
            addition=CombineMode.NONE,
            change=CombineMode.ALL
        )
    ),
]
```

## Usage Examples

### Accessing Configuration

```python
from jsonschema_diff.config import Config

# Get context parameters for a trigger
context_params = Config.get_context_params("type")
print(context_params)  # ["format"]

# Get display mode
mode = Config.get_display_mode("append")
print(f"{mode.symbol} {mode.color}")  # + green

# Get all combination rules
rules = Config.get_combination_rules()
for rule in rules:
    print(f"{rule.main_param} + {rule.sub_param}")
```

### Understanding Combination Rules

```python
# Check what gets combined
for rule in Config.get_combination_rules():
    print(f"Main: {rule.main_param}")
    print(f"Sub: {rule.sub_param}")
    print(f"Display as: {rule.display_name}")
    print(f"Template: {rule.format_template}")
    print(f"For changes: {rule.rules.change}")
    print("---")
```

## Type Safety

All configuration uses frozen dataclasses for immutability and type safety:

```python
# This will raise an error - dataclasses are frozen
mode = Config.get_display_mode("append")
mode.color = "blue"  # AttributeError: can't set attribute
```

## Extensibility

While the current configuration is not directly modifiable at runtime, the architecture supports future extension for custom configuration loading.

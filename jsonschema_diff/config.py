"""
Configuration module for JSON schema comparison.

This module contains type mappings and display modes configuration
used throughout the JSON schema comparison library.
"""

from typing import Dict, Any, Type

# Type mapping for Python types to JSON schema types
type_map: Dict[Type, str] = {
    type(None): 'null',
    bool: 'boolean',
    int: 'integer',
    float: 'number',
    str: 'string',
    list: 'array',
    tuple: 'array',
    dict: 'object'
}

# Display modes configuration for different types of changes
modes: Dict[str, Dict[str, str]] = {
    'append': {
        "color": "green",
        "symbol": "+",
    },
    'remove': {
        "color": "red",
        "symbol": "-",
    },
    'replace': {
        "color": "cyan",
        "symbol": "r",
    },
    'no_diff': {
        "color": "reset",
        "symbol": " ",
    }
}

# Context configuration: keys that should show context when changed
# Format: {context_key: [dependent_keys]}
context_config: Dict[str, list[str]] = {
    # When format changes, show type for context
    "format": ["type"],
    # When minimum/maximum changes, show pair for context
    "minimum": ["maximum"],
    "maximum": ["minimum"],
    # When additionalProperties changes, show type for context  
    "additionalProperties": ["type"],
}

# Special combination rules: keys that should be combined when changed together
# Format: {primary_key: [secondary_keys]}
combination_config: Dict[str, list[str]] = {
    # Combine type and format when both change
    "type": ["format"],
}

"""
Configuration module for JSON schema comparison.

This module contains type mappings and display modes configuration
used throughout the JSON schema comparison library.
"""

from typing import Dict, Any, Type, List

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
# Format: {changed_key: [context_keys_to_show]}
context_config: Dict[str, List[str]] = {
    # When format changes, show type for context
    #"format": ["type"],
    "type": ["format"],
    # When minimum/maximum changes, show pair for context
    "minimum": ["maximum"],
    "maximum": ["minimum"],
    # When additionalProperties changes, show type for context  
    "additionalProperties": ["type"],
}

# Combination rules for parameters - combines related parameters into single display
combination_rules: List[Dict[str, Any]] = [
    {
        "main_param": "type",           # Main parameter name
        "sub_param": "format",          # Secondary parameter name  
        "display_name": "type",         # Name to use in display (default: main_param)
        "format_template": "{main}/{sub}",  # How to combine values (default: "{main}/{sub}")
        "rules": {
            # When to apply combination for different operation types
            "removal": {"main": True, "sub": True},      # Combine when either is removed
            "addition": {"main": True, "sub": True},     # Combine when either is added  
            "change": {"main": True, "sub": True}        # Combine when either changes
        }
    },
    {
        "main_param": "minimum",
        "sub_param": "maximum",
        "display_name": "range",
        "format_template": "{main}-{sub}",
        "rules": {
            "removal": {"main": False, "sub": False},    # Don't combine removals
            "addition": {"main": False, "sub": False},   # Don't combine additions
            "change": {"main": True, "sub": True}        # Only combine changes
        }
    }
]

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

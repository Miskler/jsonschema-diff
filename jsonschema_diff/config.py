"""
Configuration module for JSON schema comparison.

This module contains type mappings and display modes configuration
used throughout the JSON schema comparison library.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Type


class CombineMode(Enum):
    """Enum for combination modes."""

    MAIN_ONLY = "main_only"  # Только главный параметр
    SUB_ONLY = "sub_only"  # Только второстепенный параметр
    ALL = "all"  # Оба параметра
    NONE = "none"  # Никого


# Type mapping for Python types to JSON schema types
TYPE_MAP: Dict[Type, str] = {
    type(None): "null",
    bool: "boolean",
    int: "integer",
    float: "number",
    str: "string",
    list: "array",
    tuple: "array",
    dict: "object",
}


@dataclass(frozen=True)
class DisplayMode:
    """Configuration for a display mode (append, remove, replace, etc.)."""

    color: str
    symbol: str


@dataclass(frozen=True)
class ContextRule:
    """Configuration for a context rule."""

    trigger_param: str
    context_params: List[str]


@dataclass(frozen=True)
class CombinationRules:
    """Rules for when to apply combination for different operation types."""

    removal: CombineMode
    addition: CombineMode
    change: CombineMode


@dataclass(frozen=True)
class CombinationRule:
    """Configuration for a parameter combination rule."""

    main_param: str
    sub_param: str
    display_name: str
    format_template: str
    rules: CombinationRules


class Config:
    """Main configuration class containing all schema comparison settings."""

    # Enable colored output using Click library
    # If True but Click is not available, shows warning and uses plain text
    USE_COLORS = True

    # Display modes for different types of changes
    MODES = {
        "append": DisplayMode(color="green", symbol="+"),
        "remove": DisplayMode(color="red", symbol="-"),
        "replace": DisplayMode(color="cyan", symbol="r"),
        "no_diff": DisplayMode(color="reset", symbol=" "),
    }

    # Context rules: when a parameter changes, show these related parameters for context
    CONTEXT_RULES = [
        ContextRule(trigger_param="type", context_params=["format"]),
        ContextRule(trigger_param="minimum", context_params=["maximum"]),
        ContextRule(trigger_param="maximum", context_params=["minimum"]),
        ContextRule(trigger_param="additionalProperties", context_params=["type"]),
    ]

    # Combination rules: combine related parameters into single display
    COMBINATION_RULES = [
        CombinationRule(
            main_param="type",
            sub_param="format",
            display_name="type",
            format_template="{main}/{sub}",
            rules=CombinationRules(
                removal=CombineMode.ALL,
                addition=CombineMode.ALL,
                change=CombineMode.ALL,
            ),
        ),
        CombinationRule(
            main_param="minimum",
            sub_param="maximum",
            display_name="range",
            format_template="{main}-{sub}",
            rules=CombinationRules(
                removal=CombineMode.NONE,
                addition=CombineMode.NONE,
                change=CombineMode.ALL,
            ),
        ),
    ]

    @classmethod
    def get_context_params(cls, trigger_param: str) -> List[str]:
        """Get context parameters for a given trigger parameter."""
        for rule in cls.CONTEXT_RULES:
            if rule.trigger_param == trigger_param:
                return rule.context_params
        return []

    @classmethod
    def get_display_mode(cls, mode_name: str) -> DisplayMode:
        """Get display mode configuration by name."""
        return cls.MODES[mode_name]

    @classmethod
    def get_combination_rules(cls) -> List[CombinationRule]:
        """Get all combination rules."""
        return cls.COMBINATION_RULES

    @classmethod
    def set_use_colors(cls, use_colors: bool) -> None:
        """Enable or disable colored output."""
        cls.USE_COLORS = use_colors

    @classmethod
    def get_use_colors(cls) -> bool:
        """Check if colored output is enabled."""
        return cls.USE_COLORS

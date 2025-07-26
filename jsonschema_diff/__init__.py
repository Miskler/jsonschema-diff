"""
JSONSchema Diff - A library for comparing JSON schemas and displaying differences.

This package provides utilities for comparing JSON schemas and formatting 
the differences in a human-readable way with colored output.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .comparator import SchemaComparator, compare_schemas
from .config import TYPE_MAP, Config

__all__ = ["SchemaComparator", "compare_schemas", "TYPE_MAP", "Config"]

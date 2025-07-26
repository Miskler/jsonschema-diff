"""
JSON Schema Comparator Module.

This module provides the SchemaComparator class for comparing JSON schemas
and generating formatted difference reports with colored output.
"""

from typing import Any, Dict
from .diff_finder import DiffFinder
from .formatter import Formatter
from .context_manager import ContextManager


class SchemaComparator:
    """
    A class for comparing JSON schemas and formatting differences.
    
    This class provides methods to compare two JSON schemas and generate
    a human-readable diff output with colored formatting using Click.
    
    Attributes:
        old_schema (Dict[str, Any]): The original schema to compare from.
        new_schema (Dict[str, Any]): The new schema to compare to.
    """

    def __init__(self, old_schema: Dict[str, Any], new_schema: Dict[str, Any]):
        """
        Initialize the SchemaComparator with two schemas.
        
        Args:
            old_schema (Dict[str, Any]): The original schema.
            new_schema (Dict[str, Any]): The new schema to compare against.
        """
        self.old_schema = old_schema
        self.new_schema = new_schema
        self.context_manager = ContextManager(old_schema, new_schema)

    def compare(self) -> str:
        """
        Perform schema comparison and return formatted result.
        
        Returns:
            str: A formatted string showing the differences between schemas.
        """
        differences = DiffFinder.find_differences(
            {"properties": self.old_schema.get("properties", {})},
            {"properties": self.new_schema.get("properties", {})}
        )
        
        # Pre-process all differences to combine type/format changes
        processed_differences = self.context_manager.combine_type_format_changes(differences)
        
        # Format the differences using the formatter
        return Formatter.format_differences(processed_differences)

def compare_schemas(old_schema: Dict[str, Any], new_schema: Dict[str, Any]) -> str:
    """
    Convenience function to compare two JSON schemas.
    
    Args:
        old_schema (Dict[str, Any]): The original schema.
        new_schema (Dict[str, Any]): The new schema.
        
    Returns:
        str: Formatted differences between the schemas.
    """
    comparator = SchemaComparator(old_schema, new_schema)
    return comparator.compare()

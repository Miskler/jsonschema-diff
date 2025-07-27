"""
JSON Schema Comparator Module.

This module provides the SchemaComparator class for comparing JSON schemas
and generating formatted difference reports with colored output.
"""

from typing import Any, Dict

from .combiner import ParameterCombiner
from .diff_finder import DiffFinder
from .diff_processor import DiffProcessor
from .formatter import Formatter
from .render_processor import RenderProcessor


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
        self.combiner = ParameterCombiner(old_schema, new_schema)
        self.render_processor = RenderProcessor(old_schema, new_schema)

    def compare(self) -> str:
        """
        Perform schema comparison and return formatted result.

        Returns:
            str: A formatted string showing the differences between schemas.
        """
        # Step 1: Find raw differences
        differences = DiffFinder.find_differences(
            {"properties": self.old_schema.get("properties", {})},
            {"properties": self.new_schema.get("properties", {})},
        )

        # Step 2: Process differences (convert add/remove pairs to changes)
        processed_differences = DiffProcessor.process_differences(differences)

        # Step 3: Combine related parameters (e.g., type + format)
        combined_differences = self.combiner.combine_parameters(processed_differences)

        # Step 4: Process for rendering (add context and group into structured format)
        render_groups = self.render_processor.process_for_render(combined_differences)

        # Step 5: Format the groups
        return Formatter.format_groups(render_groups)


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

"""
JSON Schema Comparator Module.

This module provides the SchemaComparator class for comparing JSON schemas
and generating formatted difference reports with colored output.
"""

from typing import Any, Dict, List, Tuple, Optional
import json
import click
from .config import modes


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

    def compare(self) -> str:
        """
        Perform schema comparison and return formatted result.
        
        Returns:
            str: A formatted string showing the differences between schemas.
        """
        differences = self._find_differences(
            {"properties": self.old_schema.get("properties", {})},
            {"properties": self.new_schema.get("properties", {})}
        )
        return self._format_differences(differences)

    def _format_output(self, text: str, mode: str = "no_diff") -> str:
        """
        Format output text with Click styling.
        
        Args:
            text (str): The text to format.
            mode (str): The formatting mode ('append', 'remove', 'replace', 'no_diff').
            
        Returns:
            str: Formatted text with color and symbol.
        """
        return click.style(
            f'{modes[mode]["symbol"]} {text}', 
            fg=modes[mode]["color"], 
            bold=True
        )

    def _find_differences(
        self, old: Any, new: Any, path: Optional[List[str]] = None
    ) -> List[Tuple[List[str], Any, Any]]:
        """
        Recursively find differences between two data structures.
        
        Args:
            old (Any): The old data structure.
            new (Any): The new data structure.
            path (Optional[List[str]]): Current path in the structure.
            
        Returns:
            List[Tuple[List[str], Any, Any]]: List of differences as (path, old_value, new_value).
        """
        if path is None:
            path = []
        diffs: List[Tuple[List[str], Any, Any]] = []

        # Compare lists
        if isinstance(old, list) and isinstance(new, list):
            if old != new:
                diffs.append((path, old, new))
            return diffs

        # Compare dictionaries
        all_keys = set(old.keys()) | set(new.keys())
        for key in all_keys:
            current_path = path + [key]
            if key not in old:
                diffs.append((current_path, None, new[key]))
            elif key not in new:
                diffs.append((current_path, old[key], None))
            else:
                ov = old[key]
                nv = new[key]
                if isinstance(ov, dict) and isinstance(nv, dict):
                    diffs.extend(self._find_differences(ov, nv, current_path))
                elif isinstance(ov, list) and isinstance(nv, list):
                    if ov != nv:
                        diffs.append((current_path, ov, nv))
                elif ov != nv:
                    diffs.append((current_path, ov, nv))
        return diffs

    @staticmethod
    def _format_path(path: List[str]) -> str:
        """
        Format a path to a change, skipping 'properties' and 'items', 
        shortening .type and .required.
        
        Args:
            path (List[str]): The path components.
            
        Returns:
            str: Formatted path string.
        """
        segments: List[str] = []
        for i, p in enumerate(path):
            if p in ("properties", "items"):
                continue
            # Same condition for type and required
            if p in ("type", "required", "format", "additionalProperties", "anyOf") and (i == 0 or path[i-1] != "properties"):
                segments.append(f".{p}")
            else:
                segments.append(f"[{json.dumps(p, ensure_ascii=False)}]")
        return ''.join(segments)

    def _format_list_diff(
        self, path: str, old_list: Optional[List[Any]], new_list: Optional[List[Any]]
    ) -> List[str]:
        """
        Format diff for lists: complete list with +/- markers.
        
        Args:
            path (str): The path to the list.
            old_list (Optional[List[Any]]): The old list (None if added).
            new_list (Optional[List[Any]]): The new list (None if removed).
            
        Returns:
            List[str]: Formatted list difference lines.
        """
        target_mode = "no_diff"

        if old_list is None:
            target_mode = "append"
            old_list = []
        elif new_list is None:
            target_mode = "remove"
            new_list = []

        result: List[str] = [self._format_output(f"{path}:", target_mode)]

        # Collect all unique elements without hashing
        unique_items: List[Any] = []
        for item in new_list + old_list:
            if not any(item == existing for existing in unique_items):
                unique_items.append(item)

        have_changes = False
        for item in unique_items:
            item_str = json.dumps(item, ensure_ascii=False)
            in_old = any(item == old for old in old_list)
            in_new = any(item == new for new in new_list)

            if in_old and not in_new:
                result.append(self._format_output(f"  {item_str},", "remove"))
                have_changes = True
            elif not in_old and in_new:
                result.append(self._format_output(f"  {item_str},", "append"))
                have_changes = True
            else:
                result.append(self._format_output(f"  {item_str},", "no_diff"))

        if not have_changes:
            return []

        # Remove trailing comma from last element
        head, sep, tail = result[-1].rpartition(',')
        result[-1] = head + tail

        return result

    def _format_differences(
        self, differences: List[Tuple[List[str], Any, Any]]
    ) -> str:
        """
        Format found differences into a readable view.
        
        Args:
            differences (List[Tuple[List[str], Any, Any]]): List of differences.
            
        Returns:
            str: Formatted differences string.
        """
        output: List[str] = []
        for path, old_val, new_val in differences:
            p = self._format_path(path)
            # Lists
            if isinstance(old_val, list) and isinstance(new_val, list):
                output.extend(self._format_list_diff(p, old_val, new_val))
            # Addition
            elif old_val is None:
                if isinstance(new_val, list):
                    output.extend(self._format_list_diff(p, None, new_val))
                else:
                    output.append(self._format_output(
                        f"{p}: {json.dumps(new_val, ensure_ascii=False)}", "append"
                    ))
            # Removal
            elif new_val is None:
                if isinstance(old_val, list):
                    output.extend(self._format_list_diff(p, old_val, None))
                else:
                    output.append(self._format_output(
                        f"{p}: {json.dumps(old_val, ensure_ascii=False)}", "remove"
                    ))
            # Simple value replacement
            elif not isinstance(old_val, (dict, list)) and not isinstance(new_val, (dict, list)):
                output.append(self._format_output(
                    f"{p}: {json.dumps(old_val)} -> {json.dumps(new_val)}", "replace"
                ))
            # Complex structures
            else:
                old_json = json.dumps(old_val, indent=2, ensure_ascii=False)
                new_json = json.dumps(new_val, indent=2, ensure_ascii=False)
                output.append(self._format_output(f"{p}:", "replace"))
                for line in old_json.splitlines():
                    output.append(self._format_output(f"  {line}", "remove"))
                
                for line in new_json.splitlines():
                    output.append(self._format_output(f"  {line}", "append"))

            if len(output) == 0 or len(output[-1]) != 0: 
                output.append("")
        return "\n".join(output).rstrip()


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

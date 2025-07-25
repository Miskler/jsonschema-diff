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
        if isinstance(old, dict) and isinstance(new, dict):
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
        # Different types or simple values
        elif old != new:
            diffs.append((path, old, new))
            
        return diffs

    @staticmethod
    def _format_path(path: List[str]) -> str:
        """
        Format a path to a change, understanding JSON Schema structure.
        Completely skips 'properties' keywords and determines schema parameters based on context.
        
        Args:
            path (List[str]): The path components.
            
        Returns:
            str: Formatted path string.
        """
        segments: List[str] = []
        i = 0
        
        while i < len(path):
            segment = path[i]
            
            # Always skip "properties" completely
            if segment == "properties":
                i += 1
                continue
                
            elif segment == "items":
                # Replace "items" with "[0]" only if there are more path components after it
                # that are not schema parameters (i.e., field names)
                has_field_after = False
                for j in range(i + 1, len(path)):
                    next_segment = path[j]
                    if next_segment == "properties":
                        has_field_after = True
                        break
                    elif next_segment in ("type", "format", "required", "enum", "minimum", "maximum", 
                                        "pattern", "additionalProperties", "patternProperties", "allOf", 
                                        "anyOf", "oneOf", "not", "if", "then", "else", "const", "default", 
                                        "examples", "title", "description", "items"):
                        # This is a schema parameter, not a field name
                        break
                    else:
                        # This could be a field name if we're not inside a schema context
                        # We need to check the context more carefully
                        continue
                
                if has_field_after:
                    segments.append("[0]")
                else:
                    segments.append(f".{segment}")
                i += 1
                continue
                
            elif segment in ("additionalProperties", "patternProperties"):
                # Skip these completely
                i += 1
                continue
            
            # Look ahead to see if next segment is "properties"
            # If so, this is a field name, not a schema parameter
            is_field_name = False
            if i + 1 < len(path) and path[i + 1] == "properties":
                is_field_name = True
            
            # Also check if we just came from "properties" (which was skipped)
            came_from_properties = False
            if i > 0 and path[i - 1] == "properties":
                came_from_properties = True
            
            # Determine formatting based on context
            if came_from_properties or is_field_name:
                # This is a field name - use brackets
                segments.append(f"[{json.dumps(segment, ensure_ascii=False)}]")
            elif segment.isdigit():
                # Array index - use brackets  
                segments.append(f"[{segment}]")
            else:
                # This is a schema parameter - use dot notation
                segments.append(f".{segment}")
            
            i += 1
                
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
        # Now old_list and new_list are guaranteed to be lists, not None
        for item in (new_list or []) + (old_list or []):
            if not any(item == existing for existing in unique_items):
                unique_items.append(item)

        have_changes = False
        for item in unique_items:
            item_str = json.dumps(item, ensure_ascii=False)
            in_old = any(item == old for old in (old_list or []))
            in_new = any(item == new for new in (new_list or []))

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
        # Pre-process all differences to combine type/format changes
        processed_differences = self._combine_type_format_changes(differences)
        
        output: List[str] = []
        for path, old_val, new_val in processed_differences:
            p = self._format_path(path)
            # Lists
            if isinstance(old_val, list) and isinstance(new_val, list):
                output.extend(self._format_list_diff(p, old_val, new_val))
            # Addition
            elif old_val is None:
                if isinstance(new_val, list):
                    output.extend(self._format_list_diff(p, None, new_val))
                elif isinstance(new_val, dict):
                    # Recursively expand dictionary additions
                    sub_diffs = self._find_differences({}, new_val, path)
                    for sub_path, sub_old, sub_new in sub_diffs:
                        sub_p = self._format_path(sub_path)
                        # Skip only properties that are themselves objects (like 'properties')
                        # but NOT 'items' as it's a valid schema field
                        if len(sub_path) > 0 and sub_path[-1] == "properties":
                            continue
                        # If this is a dict value, expand it recursively too
                        if isinstance(sub_new, dict):
                            nested_diffs = self._find_differences({}, sub_new, sub_path)
                            for nested_path, nested_old, nested_new in nested_diffs:
                                nested_p = self._format_path(nested_path)
                                if len(nested_path) > 0 and nested_path[-1] == "properties":
                                    continue
                                output.append(self._format_output(
                                    f"{nested_p}: {json.dumps(nested_new, ensure_ascii=False)}", "append"
                                ))
                        else:
                            output.append(self._format_output(
                                f"{sub_p}: {json.dumps(sub_new, ensure_ascii=False)}", "append"
                            ))
                else:
                    output.append(self._format_output(
                        f"{p}: {json.dumps(new_val, ensure_ascii=False)}", "append"
                    ))
            # Removal
            elif new_val is None:
                if isinstance(old_val, list):
                    output.extend(self._format_list_diff(p, old_val, None))
                elif isinstance(old_val, dict):
                    # Recursively expand dictionary removals
                    sub_diffs = self._find_differences(old_val, {}, path)
                    for sub_path, sub_old, sub_new in sub_diffs:
                        sub_p = self._format_path(sub_path)
                        output.append(self._format_output(
                            f"{sub_p}: {json.dumps(sub_old, ensure_ascii=False)}", "remove"
                        ))
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

    def _combine_type_format_changes(
        self, differences: List[Tuple[List[str], Any, Any]]
    ) -> List[Tuple[List[str], Any, Any]]:
        """
        Combine type and format changes into a single entry when they change together.
        
        Args:
            differences: List of differences as (path, old_value, new_value).
            
        Returns:
            List of processed differences with combined type/format changes.
        """
        # Group differences by their base path (without type/format)
        grouped: Dict[str, Dict[str, Tuple[List[str], Any, Any]]] = {}
        result: List[Tuple[List[str], Any, Any]] = []
        
        for path, old_val, new_val in differences:
            if len(path) >= 1 and path[-1] in ("type", "format"):
                # This is a type or format change
                base_path_str = self._format_path(path[:-1]) if len(path) > 1 else ""
                param_type = path[-1]
                
                if base_path_str not in grouped:
                    grouped[base_path_str] = {}
                grouped[base_path_str][param_type] = (path, old_val, new_val)
            else:
                # Not a type/format change, add as-is
                result.append((path, old_val, new_val))
        
        # Process grouped type/format changes
        for base_path_str, params in grouped.items():
            if "type" in params and "format" in params:
                # Both type and format are present - determine how to handle them
                type_path, type_old, type_new = params["type"]
                format_path, format_old, format_new = params["format"]
                
                # Determine the operation types
                type_operation = self._get_operation_type(type_old, type_new)
                format_operation = self._get_operation_type(format_old, format_new)
                
                # Combine when both type and format are involved in a change
                # This includes cases where one is added/removed and the other changes
                should_combine = (
                    # Both are changing (classic case)
                    (type_operation == format_operation and type_operation == "change") or
                    # Both are being added together
                    (type_operation == format_operation and type_operation == "add") or
                    # Both are being removed together
                    (type_operation == format_operation and type_operation == "remove") or
                    # Type changes and format is removed (e.g., string/uuid -> integer)
                    (type_operation == "change" and format_operation == "remove") or
                    # Type changes and format is added (e.g., integer -> string/uuid)
                    (type_operation == "change" and format_operation == "add") or
                    # Format changes and type is removed (rare case)
                    (format_operation == "change" and type_operation == "remove") or
                    # Format changes and type is added (rare case)
                    (format_operation == "change" and type_operation == "add")
                )
                
                if should_combine:
                    if type_operation == "add" and format_operation == "add":
                        combined_new = f"{type_new}/{format_new}"
                        result.append((type_path, None, combined_new))
                    elif type_operation == "remove" and format_operation == "remove":
                        combined_old = f"{type_old}/{format_old}"
                        result.append((type_path, combined_old, None))
                    elif type_operation == "change" and format_operation == "change":
                        combined_old = f"{type_old}/{format_old}"
                        combined_new = f"{type_new}/{format_new}"
                        result.append((type_path, combined_old, combined_new))
                    elif type_operation == "change" and format_operation == "remove":
                        # e.g., string/uuid -> integer
                        combined_old = f"{type_old}/{format_old}"
                        result.append((type_path, combined_old, type_new))
                    elif type_operation == "change" and format_operation == "add":
                        # e.g., integer -> string/uuid
                        combined_new = f"{type_new}/{format_new}"
                        result.append((type_path, type_old, combined_new))
                    elif format_operation == "change" and type_operation == "remove":
                        # e.g., string/uuid -> /email (rare, type removed)
                        combined_old = f"{type_old}/{format_old}"
                        result.append((type_path, combined_old, format_new))
                    elif format_operation == "change" and type_operation == "add":
                        # e.g., /email -> string/uuid (rare, type added)
                        combined_new = f"{type_new}/{format_new}"
                        result.append((type_path, format_old, combined_new))
                else:
                    # Different operation types or missing values - add separately
                    result.append(params["type"])
                    result.append(params["format"])
            else:
                # Only type or only format changed - add separately
                for param_type, (path, old_val, new_val) in params.items():
                    result.append((path, old_val, new_val))
        
        return result
    
    def _get_operation_type(self, old_val: Any, new_val: Any) -> str:
        """Get the type of operation: add, remove, or change."""
        if old_val is None and new_val is not None:
            return "add"
        elif old_val is not None and new_val is None:
            return "remove"
        elif old_val is not None and new_val is not None:
            return "change"
        else:
            return "none"

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

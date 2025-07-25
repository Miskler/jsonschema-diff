"""
JSON Schema Comparator Module.

This module provides the SchemaComparator class for comparing JSON schemas
and generating formatted difference reports with colored output.
"""

from typing import Any, Dict, List, Tuple, Optional
import json
import click
from .config import modes, context_config, combination_config, context_config


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
                    # Apply type/format combination to the expanded differences
                    processed_sub_diffs = self._combine_type_format_changes(sub_diffs)
                    for sub_path, sub_old, sub_new in processed_sub_diffs:
                        sub_p = self._format_path(sub_path)
                        # Skip only properties that are themselves objects (like 'properties')
                        # but NOT 'items' as it's a valid schema field
                        if len(sub_path) > 0 and sub_path[-1] == "properties":
                            continue
                        # If this is a dict value, expand it recursively too
                        if isinstance(sub_new, dict):
                            nested_diffs = self._find_differences({}, sub_new, sub_path)
                            nested_processed = self._combine_type_format_changes(nested_diffs)
                            for nested_path, nested_old, nested_new in nested_processed:
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
                if old_val == new_val:
                    # This is a no-diff context line (e.g., showing type for format changes)
                    output.append(self._format_output(
                        f"{p}: {json.dumps(old_val, ensure_ascii=False)}", "no_diff"
                    ))
                else:
                    # This is an actual replacement
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

            # Add empty line only if this is not a context line (no_diff) and not following another context line
            should_add_empty_line = (
                len(output) > 0 and 
                len(output[-1]) != 0 and 
                not (old_val == new_val and old_val is not None) and
                # Check if previous line was also a context line
                (len(output) == 1 or not output[-2].strip().startswith(" "))
            )
            if should_add_empty_line:
                output.append("")
        return "\n".join(output).rstrip()

    def _combine_type_format_changes(
        self, differences: List[Tuple[List[str], Any, Any]]
    ) -> List[Tuple[List[str], Any, Any]]:
        """
        Combine related schema changes and add context information based on configuration.
        
        Args:
            differences: List of differences as (path, old_value, new_value).
            
        Returns:
            List of processed differences with combined changes and context.
        """
        # Group differences by their base path (without the last segment)
        grouped: Dict[str, Dict[str, Tuple[List[str], Any, Any]]] = {}
        result: List[Tuple[List[str], Any, Any]] = []
        
        # Collect all schema parameter changes
        all_schema_params = set(context_config.keys()) | set(combination_config.keys())
        for combo_list in combination_config.values():
            all_schema_params.update(combo_list)
        
        for path, old_val, new_val in differences:
            if len(path) >= 1 and path[-1] in all_schema_params:
                # This is a schema parameter change
                base_path_str = self._format_path(path[:-1]) if len(path) > 1 else ""
                param_type = path[-1]
                
                if base_path_str not in grouped:
                    grouped[base_path_str] = {}
                grouped[base_path_str][param_type] = (path, old_val, new_val)
            else:
                # Not a schema parameter change, add as-is
                result.append((path, old_val, new_val))
        
        # Process grouped schema parameter changes
        for base_path_str, params in grouped.items():
            processed_params = set()
            
            # Handle combination rules first
            for primary_key, secondary_keys in combination_config.items():
                if primary_key in params and primary_key not in processed_params:
                    # Check if any secondary keys are also present
                    available_secondary = [key for key in secondary_keys if key in params]
                    
                    if available_secondary:
                        # Try to combine with each available secondary key
                        for secondary_key in available_secondary:
                            if secondary_key not in processed_params:
                                combined_result = self._try_combine_parameters(
                                    params[primary_key], params[secondary_key]
                                )
                                if combined_result:
                                    result.append(combined_result)
                                    processed_params.add(primary_key)
                                    processed_params.add(secondary_key)
                                    break
                    
                    # If no combination was possible, handle individually
                    if primary_key not in processed_params:
                        result.append(params[primary_key])
                        processed_params.add(primary_key)
            
            # Handle context relationships for non-combined parameters
            for param_name, param_data in params.items():
                if param_name in processed_params:
                    continue
                    
                path, old_val, new_val = param_data
                operation = self._get_operation_type(old_val, new_val)
                
                # Check if this parameter should have context
                if param_name in context_config and operation in ("change", "add", "remove"):
                    context_keys = context_config[param_name]
                    
                    # Add context for each dependent key
                    for context_key in context_keys:
                        if context_key in params:
                            # Context key is also changing - already handled above or will be handled
                            continue
                        else:
                            # Context key is not changing - find its value for context
                            context_path = path[:-1] + [context_key]
                            context_value = self._find_context_value(context_path)
                            if context_value:
                                result.append((context_path, context_value, context_value))
                    
                    # Add the actual change
                    result.append(param_data)
                    processed_params.add(param_name)
                else:
                    # No special handling needed
                    result.append(param_data)
                    processed_params.add(param_name)
        
        return result
    
    def _try_combine_parameters(
        self, primary_param: Tuple[List[str], Any, Any], secondary_param: Tuple[List[str], Any, Any]
    ) -> Optional[Tuple[List[str], Any, Any]]:
        """
        Try to combine two parameters (e.g., type and format) into a single change.
        
        Args:
            primary_param: Primary parameter data (path, old_val, new_val)
            secondary_param: Secondary parameter data (path, old_val, new_val)
            
        Returns:
            Combined parameter if successful, None otherwise
        """
        primary_path, primary_old, primary_new = primary_param
        secondary_path, secondary_old, secondary_new = secondary_param
        
        primary_operation = self._get_operation_type(primary_old, primary_new)
        secondary_operation = self._get_operation_type(secondary_old, secondary_new)
        
        # Combine when both parameters are involved in compatible changes
        should_combine = (
            # Both are changing (classic case)
            (primary_operation == secondary_operation and primary_operation == "change") or
            # Both are being added together
            (primary_operation == secondary_operation and primary_operation == "add") or
            # Both are being removed together
            (primary_operation == secondary_operation and primary_operation == "remove") or
            # One changes and the other is removed/added
            (primary_operation == "change" and secondary_operation in ("remove", "add")) or
            (secondary_operation == "change" and primary_operation in ("remove", "add"))
        )
        
        if not should_combine:
            return None
            
        # Create combined values
        if primary_operation == "add" and secondary_operation == "add":
            combined_new = f"{primary_new}/{secondary_new}"
            return (primary_path, None, combined_new)
        elif primary_operation == "remove" and secondary_operation == "remove":
            combined_old = f"{primary_old}/{secondary_old}"
            return (primary_path, combined_old, None)
        elif primary_operation == "change" and secondary_operation == "change":
            combined_old = f"{primary_old}/{secondary_old}"
            combined_new = f"{primary_new}/{secondary_new}"
            return (primary_path, combined_old, combined_new)
        elif primary_operation == "change" and secondary_operation == "remove":
            # e.g., string/uuid -> integer
            combined_old = f"{primary_old}/{secondary_old}"
            return (primary_path, combined_old, primary_new)
        elif primary_operation == "change" and secondary_operation == "add":
            # e.g., integer -> string/uuid
            combined_new = f"{primary_new}/{secondary_new}"
            return (primary_path, primary_old, combined_new)
        elif secondary_operation == "change" and primary_operation == "remove":
            # e.g., string/uuid -> /email (rare, primary removed)
            combined_old = f"{primary_old}/{secondary_old}"
            return (primary_path, combined_old, secondary_new)
        elif secondary_operation == "change" and primary_operation == "add":
            # e.g., /email -> string/uuid (rare, primary added)
            combined_new = f"{primary_new}/{secondary_new}"
            return (primary_path, secondary_old, combined_new)
            
        return None

    def _find_context_value(self, context_path: List[str]) -> Optional[str]:
        """
        Find the context value for a given path in the original schemas.
        
        Args:
            context_path: Path to the context field
            
        Returns:
            Context value if found, None otherwise
        """
        # Try to find in old schema first
        if self.old_schema:
            wrapped_old = {"properties": self.old_schema.get("properties", {})}
            value = self._get_value_at_path(wrapped_old, context_path)
            if value:
                return value
                
        # Try to find in new schema
        if self.new_schema:
            wrapped_new = {"properties": self.new_schema.get("properties", {})}
            value = self._get_value_at_path(wrapped_new, context_path)
            if value:
                return value
                
        return None
    
    def _find_type_for_context(
        self, 
        type_path: List[str], 
        format_old: Any, 
        format_new: Any, 
        old_schema: Optional[Dict[str, Any]], 
        new_schema: Optional[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Find the type value for providing context when only format changes.
        
        Args:
            type_path: Path to the type field
            format_old: Old format value
            format_new: New format value  
            old_schema: Original schema
            new_schema: New schema
            
        Returns:
            Type value if found, None otherwise
        """
        # The type_path already includes 'properties', so use it as-is
        schema_path = type_path
        
        # Try to find type in appropriate schema
        if format_old is not None and old_schema:
            # Format existed before, look in old schema
            # Start from the wrapped schema that includes {"properties": {...}}
            wrapped_old = {"properties": old_schema.get("properties", {})}
            type_value = self._get_value_at_path(wrapped_old, schema_path)
            if type_value:
                return type_value
                
        if format_new is not None and new_schema:
            # Format exists now, look in new schema
            # Start from the wrapped schema that includes {"properties": {...}}
            wrapped_new = {"properties": new_schema.get("properties", {})}
            type_value = self._get_value_at_path(wrapped_new, schema_path)
            if type_value:
                return type_value
                
        return None
    
    def _get_value_at_path(self, schema: Dict[str, Any], path: List[str]) -> Optional[str]:
        """
        Navigate through schema to find value at given path.
        
        Args:
            schema: Schema to navigate
            path: Path components
            
        Returns:
            Value if found, None otherwise
        """
        current = schema
        for segment in path:
            if isinstance(current, dict) and segment in current:
                current = current[segment]
            else:
                return None
        return current if isinstance(current, str) else None
    
    def _get_operation_type(self, old_val: Any, new_val: Any) -> str:
        """Get the type of operation: add, remove, change, or none."""
        if old_val is None and new_val is not None:
            return "add"
        elif old_val is not None and new_val is None:
            return "remove"
        elif old_val is not None and new_val is not None and old_val != new_val:
            return "change"
        elif old_val is not None and new_val is not None and old_val == new_val:
            return "none"  # Value didn't change
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

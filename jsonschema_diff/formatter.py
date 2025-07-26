"""
Formatter for JSON Schema comparison output.

This module provides functionality to format differences between JSON schemas
into human-readable output with colored formatting.
"""

from typing import Any, Dict, List, Optional, Tuple
import json
import click
from .config import modes
from .path_utils import PathUtils
from .diff_finder import DiffFinder


class Formatter:
    """Class for formatting schema comparison output."""
    
    @staticmethod
    def format_output(text: str, mode: str = "no_diff") -> str:
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
    
    @staticmethod
    def format_list_diff(
        path: str, old_list: Optional[List[Any]], new_list: Optional[List[Any]]
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

        result: List[str] = [Formatter.format_output(f"{path}:", target_mode)]

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
                result.append(Formatter.format_output(f"  {item_str},", "remove"))
                have_changes = True
            elif not in_old and in_new:
                result.append(Formatter.format_output(f"  {item_str},", "append"))
                have_changes = True
            else:
                result.append(Formatter.format_output(f"  {item_str},", "no_diff"))

        if not have_changes:
            return []

        # Remove trailing comma from last element
        head, sep, tail = result[-1].rpartition(',')
        result[-1] = head + tail

        return result
    
    @staticmethod
    def format_differences(
        differences: List[Tuple[List[str], Any, Any]]
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
            p = PathUtils.format_path(path)
            # Lists
            if isinstance(old_val, list) and isinstance(new_val, list):
                output.extend(Formatter.format_list_diff(p, old_val, new_val))
            # Addition
            elif old_val is None:
                if isinstance(new_val, list):
                    output.extend(Formatter.format_list_diff(p, None, new_val))
                elif isinstance(new_val, dict):
                    # Recursively expand dictionary additions
                    sub_diffs = DiffFinder.find_differences({}, new_val, path)
                    for sub_path, sub_old, sub_new in sub_diffs:
                        sub_p = PathUtils.format_path(sub_path)
                        # Skip only properties that are themselves objects (like 'properties')
                        # but NOT 'items' as it's a valid schema field
                        if len(sub_path) > 0 and sub_path[-1] == "properties":
                            continue
                        # If this is a dict value, expand it recursively too
                        if isinstance(sub_new, dict):
                            nested_diffs = DiffFinder.find_differences({}, sub_new, sub_path)
                            for nested_path, nested_old, nested_new in nested_diffs:
                                nested_p = PathUtils.format_path(nested_path)
                                if len(nested_path) > 0 and nested_path[-1] == "properties":
                                    continue
                                output.append(Formatter.format_output(
                                    f"{nested_p}: {json.dumps(nested_new, ensure_ascii=False)}", "append"
                                ))
                        else:
                            output.append(Formatter.format_output(
                                f"{sub_p}: {json.dumps(sub_new, ensure_ascii=False)}", "append"
                            ))
                else:
                    output.append(Formatter.format_output(
                        f"{p}: {json.dumps(new_val, ensure_ascii=False)}", "append"
                    ))
            # Removal
            elif new_val is None:
                if isinstance(old_val, list):
                    output.extend(Formatter.format_list_diff(p, old_val, None))
                elif isinstance(old_val, dict):
                    # Recursively expand dictionary removals
                    sub_diffs = DiffFinder.find_differences(old_val, {}, path)
                    for sub_path, sub_old, sub_new in sub_diffs:
                        sub_p = PathUtils.format_path(sub_path)
                        output.append(Formatter.format_output(
                            f"{sub_p}: {json.dumps(sub_old, ensure_ascii=False)}", "remove"
                        ))
                else:
                    output.append(Formatter.format_output(
                        f"{p}: {json.dumps(old_val, ensure_ascii=False)}", "remove"
                    ))
            # Simple value replacement
            elif not isinstance(old_val, (dict, list)) and not isinstance(new_val, (dict, list)):
                if old_val == new_val:
                    # This is a no-diff context line (e.g., showing type for format changes)
                    output.append(Formatter.format_output(
                        f"{p}: {json.dumps(old_val, ensure_ascii=False)}", "no_diff"
                    ))
                else:
                    # This is an actual replacement
                    output.append(Formatter.format_output(
                        f"{p}: {json.dumps(old_val)} -> {json.dumps(new_val)}", "replace"
                    ))
            # Complex structures
            else:
                old_json = json.dumps(old_val, indent=2, ensure_ascii=False)
                new_json = json.dumps(new_val, indent=2, ensure_ascii=False)
                output.append(Formatter.format_output(f"{p}:", "replace"))
                for line in old_json.splitlines():
                    output.append(Formatter.format_output(f"  {line}", "remove"))
                
                for line in new_json.splitlines():
                    output.append(Formatter.format_output(f"  {line}", "append"))

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

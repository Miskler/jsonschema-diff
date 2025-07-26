"""
Difference finder for JSON Schema comparison.

This module provides functionality to find differences between JSON schemas
and classify operation types.
"""

from typing import Any, Dict, List, Optional, Tuple


class DiffFinder:
    """Class for finding differences between JSON structures."""
    
    @staticmethod
    def find_differences(
        old: Any, new: Any, path: Optional[List[str]] = None
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
                        diffs.extend(DiffFinder.find_differences(ov, nv, current_path))
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
    def get_operation_type(old_val: Any, new_val: Any) -> str:
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

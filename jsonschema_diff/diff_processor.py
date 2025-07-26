"""
Difference processor for JSON Schema comparison.

This module provides functionality to post-process raw differences,
converting add/remove pairs into change operations.
"""

from typing import Any, Dict, List, Tuple


class DiffProcessor:
    """Class for post-processing raw differences."""
    
    @staticmethod
    def process_differences(
        differences: List[Tuple[List[str], Any, Any]]
    ) -> List[Tuple[List[str], Any, Any]]:
        """
        Process raw differences to convert add/remove pairs into changes.
        
        Args:
            differences: List of raw differences as (path, old_value, new_value)
            
        Returns:
            List of processed differences with change operations
        """
        if not differences:
            return differences
            
        # Group differences by path
        path_groups: Dict[str, List[Tuple[List[str], Any, Any]]] = {}
        
        for path, old_val, new_val in differences:
            path_str = ".".join(path)
            if path_str not in path_groups:
                path_groups[path_str] = []
            path_groups[path_str].append((path, old_val, new_val))
        
        result: List[Tuple[List[str], Any, Any]] = []
        
        # Process each path group
        for path_str, group in path_groups.items():
            if len(group) == 1:
                # Single operation - add as-is
                result.append(group[0])
            elif len(group) == 2:
                # Potential add/remove pair - check if it should be converted to change
                diff1, diff2 = group
                path1, old1, new1 = diff1
                path2, old2, new2 = diff2
                
                # Check if one is add and other is remove
                if (old1 is None and new1 is not None and 
                    old2 is not None and new2 is None):
                    # diff1 is add, diff2 is remove -> convert to change
                    result.append((path1, old2, new1))
                elif (old2 is None and new2 is not None and 
                      old1 is not None and new1 is None):
                    # diff2 is add, diff1 is remove -> convert to change
                    result.append((path1, old1, new2))
                else:
                    # Not an add/remove pair - add both
                    result.extend(group)
            else:
                # More than 2 operations - add all
                result.extend(group)
        
        return result

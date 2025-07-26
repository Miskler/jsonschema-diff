"""
Render processor for JSON Schema comparison.

This module provides functionality to add context information
and decide what should be rendered in the final output.
"""

from typing import Any, Dict, List, Optional, Tuple, Set, NamedTuple
from .config import Config
from .path_utils import PathUtils
from .diff_finder import DiffFinder


class DiffLine(NamedTuple):
    """Represents a single line in the diff output with metadata."""
    path: List[str]
    old_value: Any
    new_value: Any
    line_type: str  # "main" | "context"
    

class DiffGroup(NamedTuple):
    """Represents a group of related diff lines."""
    main_line: DiffLine
    context_lines: List[DiffLine]


class RenderProcessor:
    """Class for processing differences for final rendering."""
    
    def __init__(self, old_schema: Dict[str, Any], new_schema: Dict[str, Any]):
        """
        Initialize the RenderProcessor with schemas.
        
        Args:
            old_schema: The original schema
            new_schema: The new schema
        """
        self.old_schema = old_schema
        self.new_schema = new_schema
    
    def process_for_render(
        self, differences: List[Tuple[List[str], Any, Any]]
    ) -> List[DiffGroup]:
        """
        Process differences for rendering, grouping main changes with their context.
        
        Args:
            differences: List of differences as (path, old_value, new_value)
            
        Returns:
            List of DiffGroup objects ready for rendering
        """
        if not differences:
            return []
            
        groups: List[DiffGroup] = []
        added_context_paths: Set[str] = set()
        
        for path, old_val, new_val in differences:
            # Create main diff line
            main_line = DiffLine(path, old_val, new_val, "main")
            
            # Collect context lines for this main line
            context_lines: List[DiffLine] = []
            
            # Check if this parameter needs context
            if len(path) >= 1:
                param_name = path[-1]
                context_keys = Config.get_context_params(param_name)
                if context_keys:
                    operation = DiffFinder.get_operation_type(old_val, new_val)
                    
                    # Add context only for meaningful operations
                    if operation in ("change", "add", "remove"):
                        base_path = path[:-1]
                        
                        for context_key in context_keys:
                            context_path = base_path + [context_key]
                            context_path_str = ".".join(context_path)
                            
                            # Avoid duplicate context entries
                            if context_path_str not in added_context_paths:
                                context_value = self._find_context_value(context_path)
                                
                                if context_value is not None:
                                    # Create context line
                                    context_line = DiffLine(context_path, context_value, context_value, "context")
                                    context_lines.append(context_line)
                                    added_context_paths.add(context_path_str)
            
            # Create group
            group = DiffGroup(main_line, context_lines)
            groups.append(group)
        
        return groups
    
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
            value = PathUtils.get_value_at_path(wrapped_old, context_path)
            if value is not None:
                return str(value)
                
        # Try to find in new schema
        if self.new_schema:
            wrapped_new = {"properties": self.new_schema.get("properties", {})}
            value = PathUtils.get_value_at_path(wrapped_new, context_path)
            if value is not None:
                return str(value)
                
        return None

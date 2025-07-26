"""
Context manager for JSON Schema comparison.

This module provides functionality to add context information 
to schema changes for better readability.
"""

from typing import Any, Dict, List, Optional, Tuple
from .config import Config
from .path_utils import PathUtils
from .diff_finder import DiffFinder


class ContextManager:
    """Class for adding context information to schema changes."""
    
    def __init__(self, old_schema: Dict[str, Any], new_schema: Dict[str, Any]):
        """
        Initialize the ContextManager with schemas.
        
        Args:
            old_schema: The original schema
            new_schema: The new schema
        """
        self.old_schema = old_schema
        self.new_schema = new_schema
    
    def add_context_information(
        self, differences: List[Tuple[List[str], Any, Any]]
    ) -> List[Tuple[List[str], Any, Any]]:
        """
        Add context information to differences based on Config.CONTEXT_RULES.
        
        Args:
            differences: List of differences as (path, old_value, new_value)
            
        Returns:
            List of differences with context information added
        """
        if not differences:
            return differences
            
        result: List[Tuple[List[str], Any, Any]] = []
        
        for path, old_val, new_val in differences:
            # Add the original difference
            result.append((path, old_val, new_val))
            
            # Check if this parameter needs context
            if len(path) >= 1:
                param_name = path[-1]
                context_params = Config.get_context_params(param_name)
                
                if context_params:
                    operation = DiffFinder.get_operation_type(old_val, new_val)
                    
                    # Add context only for meaningful operations
                    if operation in ("change", "add", "remove"):
                        base_path = path[:-1]
                        
                        for context_key in context_params:
                            context_path = base_path + [context_key]
                            context_value = self._find_context_value(context_path)
                            
                            if context_value is not None:
                                # Add context as a no-change entry (old == new)
                                result.append((context_path, context_value, context_value))
        
        return result

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

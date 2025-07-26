"""
Context manager for JSON Schema comparison.

This module provides functionality to manage context and combine related
schema changes for better readability.
"""

from typing import Any, Dict, List, Optional, Tuple
from .config import context_config, combination_config
from .path_utils import PathUtils
from .diff_finder import DiffFinder


class ContextManager:
    """Class for managing context and combining schema changes."""
    
    def __init__(self, old_schema: Dict[str, Any], new_schema: Dict[str, Any]):
        """
        Initialize the ContextManager with schemas.
        
        Args:
            old_schema: The original schema
            new_schema: The new schema
        """
        self.old_schema = old_schema
        self.new_schema = new_schema
    
    def combine_type_format_changes(
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
                base_path_str = PathUtils.format_path(path[:-1]) if len(path) > 1 else ""
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
                operation = DiffFinder.get_operation_type(old_val, new_val)
                
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
        
        primary_operation = DiffFinder.get_operation_type(primary_old, primary_new)
        secondary_operation = DiffFinder.get_operation_type(secondary_old, secondary_new)
        
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
            value = PathUtils.get_value_at_path(wrapped_old, context_path)
            if value:
                return value
                
        # Try to find in new schema
        if self.new_schema:
            wrapped_new = {"properties": self.new_schema.get("properties", {})}
            value = PathUtils.get_value_at_path(wrapped_new, context_path)
            if value:
                return value
                
        return None
    
    def find_type_for_context(
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
            type_value = PathUtils.get_value_at_path(wrapped_old, schema_path)
            if type_value:
                return type_value
                
        if format_new is not None and new_schema:
            # Format exists now, look in new schema
            # Start from the wrapped schema that includes {"properties": {...}}
            wrapped_new = {"properties": new_schema.get("properties", {})}
            type_value = PathUtils.get_value_at_path(wrapped_new, schema_path)
            if type_value:
                return type_value
                
        return None

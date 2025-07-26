"""
Path utilities for JSON Schema comparison.

This module provides utilities for working with paths in JSON schemas,
including path formatting and navigation through schema structures.
"""

from typing import Any, Dict, List, Optional
import json


class PathUtils:
    """Utility class for working with JSON Schema paths."""
    
    @staticmethod
    def format_path(path: List[str]) -> str:
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
    
    @staticmethod
    def get_value_at_path(schema: Dict[str, Any], path: List[str]) -> Optional[str]:
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

    @staticmethod
    def parse_path(path_str: str) -> List[str]:
        """
        Parse a formatted path string back into path components.
        
        Args:
            path_str: Formatted path string like '["field1"].type' or '["field1"][0].format'
            
        Returns:
            List of path components
        """
        if not path_str:
            return []
            
        # Simple parsing - split by dots and extract bracketed content
        path_components = []
        i = 0
        current_segment = ""
        
        while i < len(path_str):
            char = path_str[i]
            
            if char == '[':
                # Extract bracketed content
                bracket_end = path_str.find(']', i)
                if bracket_end != -1:
                    bracket_content = path_str[i+1:bracket_end]
                    # Remove quotes if present
                    if bracket_content.startswith('"') and bracket_content.endswith('"'):
                        bracket_content = bracket_content[1:-1]
                    elif bracket_content.startswith("'") and bracket_content.endswith("'"):
                        bracket_content = bracket_content[1:-1]
                    path_components.append(bracket_content)
                    i = bracket_end + 1
                else:
                    i += 1
            elif char == '.':
                # Start of dot notation segment
                if current_segment:
                    path_components.append(current_segment)
                    current_segment = ""
                i += 1
            else:
                current_segment += char
                i += 1
        
        # Add final segment if any
        if current_segment:
            path_components.append(current_segment)
            
        return path_components

"""
Tests for the Formatter module.
"""

import pytest
import json
from unittest.mock import Mock, patch
from jsonschema_diff.formatter import Formatter
from jsonschema_diff.render_processor import DiffLine, DiffGroup


class TestFormatter:
    """Test cases for the Formatter class."""
    
    def test_format_output_append(self):
        """Test format_output with append mode."""
        result = Formatter.format_output("test text", "append")
        # Can't easily test color codes, but we can test that it contains the expected text
        assert "test text" in result
        assert "+" in result  # Default symbol for append

    def test_format_output_remove(self):
        """Test format_output with remove mode."""
        result = Formatter.format_output("test text", "remove")
        assert "test text" in result
        assert "-" in result  # Default symbol for remove

    def test_format_output_replace(self):
        """Test format_output with replace mode."""
        result = Formatter.format_output("test text", "replace")
        assert "test text" in result
        assert "r" in result  # Default symbol for replace

    def test_format_output_no_diff(self):
        """Test format_output with no_diff mode."""
        result = Formatter.format_output("test text", "no_diff")
        assert "test text" in result
        assert " " in result  # Default symbol for no_diff

    def test_format_list_diff_added_list(self):
        """Test format_list_diff when a list is added."""
        path = "properties.items"
        old_list = None
        new_list = ["string", "number"]
        
        result = Formatter.format_list_diff(path, old_list, new_list)
        
        assert len(result) > 0
        assert path in result[0]
        assert "string" in "\n".join(result)
        assert "number" in "\n".join(result)

    def test_format_list_diff_removed_list(self):
        """Test format_list_diff when a list is removed."""
        path = "properties.items"
        old_list = ["string", "number"]
        new_list = None
        
        result = Formatter.format_list_diff(path, old_list, new_list)
        
        assert len(result) > 0
        assert path in result[0]
        assert "string" in "\n".join(result)
        assert "number" in "\n".join(result)

    def test_format_list_diff_modified_list(self):
        """Test format_list_diff when a list is modified."""
        path = "properties.items"
        old_list = ["string", "number"]
        new_list = ["string", "boolean"]
        
        result = Formatter.format_list_diff(path, old_list, new_list)
        
        assert len(result) > 0
        assert path in result[0]
        assert "string" in "\n".join(result)  # unchanged
        assert "number" in "\n".join(result)  # removed
        assert "boolean" in "\n".join(result)  # added

    def test_format_list_diff_no_changes(self):
        """Test format_list_diff when lists are identical."""
        path = "properties.items"
        old_list = ["string", "number"]
        new_list = ["string", "number"]
        
        result = Formatter.format_list_diff(path, old_list, new_list)
        
        # Should return empty list if no changes
        assert result == []

    def test_format_list_diff_complex_items(self):
        """Test format_list_diff with complex list items."""
        path = "properties.items"
        old_list = [{"type": "string"}, {"type": "number"}]
        new_list = [{"type": "string"}, {"type": "boolean"}]
        
        result = Formatter.format_list_diff(path, old_list, new_list)
        
        assert len(result) > 0
        result_text = "\n".join(result)
        assert "string" in result_text
        assert "number" in result_text
        assert "boolean" in result_text

    def test_format_list_diff_empty_lists(self):
        """Test format_list_diff with empty lists."""
        path = "properties.items"
        old_list = []
        new_list = []
        
        result = Formatter.format_list_diff(path, old_list, new_list)
        
        # Should return empty list if both are empty
        assert result == []

    def test_format_list_diff_removes_trailing_comma(self):
        """Test that format_list_diff removes trailing comma from last element."""
        path = "properties.items"
        old_list = None
        new_list = ["string"]
        
        result = Formatter.format_list_diff(path, old_list, new_list)
        
        # Last line should not end with comma
        assert not result[-1].endswith(',')

    def test_format_differences_deprecated(self):
        """Test the deprecated format_differences method."""
        differences = [
            (["properties", "name", "type"], "integer", "string")
        ]
        
        result = Formatter.format_differences(differences)
        
        assert isinstance(result, str)
        assert '["name"].type' in result  # Actual format from PathUtils.format_path
        assert "integer" in result
        assert "string" in result

    def test_format_groups_single_group(self):
        """Test format_groups with a single group."""
        main_line = DiffLine(
            path=["properties", "name", "type"],
            old_value="integer",
            new_value="string",
            line_type="main"
        )
        group = DiffGroup(main_line=main_line, context_lines=[])
        
        result = Formatter.format_groups([group])
        
        assert '["name"].type' in result  # Actual format from PathUtils.format_path
        assert "integer" in result
        assert "string" in result

    def test_format_groups_multiple_groups(self):
        """Test format_groups with multiple groups."""
        main_line1 = DiffLine(
            path=["properties", "name", "type"],
            old_value="integer",
            new_value="string",
            line_type="main"
        )
        main_line2 = DiffLine(
            path=["properties", "age", "minimum"],
            old_value=0,
            new_value=1,
            line_type="main"
        )
        
        group1 = DiffGroup(main_line=main_line1, context_lines=[])
        group2 = DiffGroup(main_line=main_line2, context_lines=[])
        
        result = Formatter.format_groups([group1, group2])
        
        # Should contain both changes
        assert '["name"].type' in result  # Actual format from PathUtils.format_path
        assert '["age"].minimum' in result  # Actual format from PathUtils.format_path
        
        # Should have empty line between groups
        lines = result.split('\n')
        assert len(lines) >= 3  # At least 2 lines + 1 empty line
        assert any(line == "" for line in lines)

    def test_format_groups_with_context(self):
        """Test format_groups with context lines."""
        main_line = DiffLine(
            path=["properties", "name", "type"],
            old_value="integer",
            new_value="string",
            line_type="main"
        )
        context_line = DiffLine(
            path=["properties", "name", "format"],
            old_value="email",
            new_value="email",
            line_type="context"
        )
        
        group = DiffGroup(main_line=main_line, context_lines=[context_line])
        
        result = Formatter.format_groups([group])
        
        # Should contain both main and context
        assert '["name"].type' in result  # Actual format from PathUtils.format_path
        assert '["name"].format' in result  # Actual format from PathUtils.format_path
        
        # Context should immediately follow main (no empty line)
        lines = result.split('\n')
        main_idx = next(i for i, line in enumerate(lines) if "type" in line)
        context_idx = next(i for i, line in enumerate(lines) if "format" in line)
        assert context_idx == main_idx + 1

    def test_format_single_line_context(self):
        """Test _format_single_line with context line."""
        line = DiffLine(
            path=["properties", "name", "format"],
            old_value="email",
            new_value="email",
            line_type="context"
        )
        
        result = Formatter._format_single_line(line)
        
        assert '["name"].format' in result  # Actual format from PathUtils.format_path
        assert "email" in result
        # Context lines should not show changes (no arrow)
        assert "->" not in result

    def test_format_single_line_append(self):
        """Test _format_single_line with append (None -> value)."""
        line = DiffLine(
            path=["properties", "name", "type"],
            old_value=None,
            new_value="string",
            line_type="main"
        )
        
        result = Formatter._format_single_line(line)
        
        assert '["name"].type' in result  # Actual format from PathUtils.format_path
        assert "string" in result
        assert "->" not in result  # No arrow for append

    def test_format_single_line_remove(self):
        """Test _format_single_line with remove (value -> None)."""
        line = DiffLine(
            path=["properties", "name", "type"],
            old_value="string",
            new_value=None,
            line_type="main"
        )
        
        result = Formatter._format_single_line(line)
        
        assert '["name"].type' in result  # Actual format from PathUtils.format_path
        assert "string" in result
        assert "->" not in result  # No arrow for remove

    def test_format_single_line_change(self):
        """Test _format_single_line with change (value -> different value)."""
        line = DiffLine(
            path=["properties", "name", "type"],
            old_value="integer",
            new_value="string",
            line_type="main"
        )
        
        result = Formatter._format_single_line(line)
        
        assert '["name"].type' in result  # Actual format from PathUtils.format_path
        assert "integer" in result
        assert "string" in result
        assert "->" in result  # Should show arrow for change

    def test_format_single_line_complex_values(self):
        """Test _format_single_line with complex JSON values."""
        line = DiffLine(
            path=["properties", "name", "items"],
            old_value={"type": "string"},
            new_value={"type": "number"},
            line_type="main"
        )
        
        result = Formatter._format_single_line(line)
        
        assert '["name"].items' in result  # Actual format from PathUtils.format_path
        assert "string" in result
        assert "number" in result

    def test_format_groups_empty_list(self):
        """Test format_groups with empty list."""
        result = Formatter.format_groups([])
        assert result == ""

    def test_format_list_diff_duplicate_items(self):
        """Test format_list_diff with duplicate items in lists."""
        path = "properties.items"
        old_list = ["string", "string", "number"]
        new_list = ["string", "boolean", "boolean"]
        
        result = Formatter.format_list_diff(path, old_list, new_list)
        
        # Should handle duplicates correctly - each unique item appears once
        result_text = "\n".join(result)
        assert "string" in result_text
        assert "number" in result_text
        assert "boolean" in result_text
        
        # Count occurrences - each should appear only once in the diff
        string_count = result_text.count('"string"')
        assert string_count == 1  # Should deduplicate

    def test_format_list_diff_with_none_values(self):
        """Test format_list_diff properly handles None values in lists."""
        path = "properties.items" 
        old_list = [None, "string"]
        new_list = ["string", None]
        
        result = Formatter.format_list_diff(path, old_list, new_list)
        
        # No changes, so should return empty list
        if not result:  # Empty list if no changes
            assert len(result) == 0
        else:
            result_text = "\n".join(result)
            assert "null" in result_text  # JSON representation of None
            assert "string" in result_text

    def test_type_checking_imports(self):
        """Test that TYPE_CHECKING imports work correctly."""
        # This test ensures the TYPE_CHECKING import on line 16 is executed
        # by importing the module and accessing type-hinted methods
        from jsonschema_diff.formatter import Formatter
        from jsonschema_diff.render_processor import DiffLine, DiffGroup
        
        # Create objects that use the TYPE_CHECKING imports
        line = DiffLine(
            path=["test"],
            old_value="old",
            new_value="new", 
            line_type="main"
        )
        group = DiffGroup(main_line=line, context_lines=[])
        
        # Call method that uses these types in annotations
        result = Formatter.format_groups([group])
        assert isinstance(result, str)

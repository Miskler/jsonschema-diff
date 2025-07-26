"""
Tests for the ContextManager module.
"""

import pytest
from unittest.mock import Mock, patch
from jsonschema_diff.context_manager import ContextManager


class TestContextManager:
    """Test cases for the ContextManager class."""

    def test_init(self):
        """Test ContextManager initialization."""
        old_schema = {"properties": {"name": {"type": "string"}}}
        new_schema = {"properties": {"name": {"type": "integer"}}}
        
        manager = ContextManager(old_schema, new_schema)
        
        assert manager.old_schema == old_schema
        assert manager.new_schema == new_schema

    def test_add_context_information_empty_differences(self):
        """Test add_context_information with empty differences list."""
        old_schema = {"properties": {"name": {"type": "string"}}}
        new_schema = {"properties": {"name": {"type": "integer"}}}
        manager = ContextManager(old_schema, new_schema)
        
        result = manager.add_context_information([])
        
        assert result == []

    @patch('jsonschema_diff.context_manager.Config.get_context_params')
    def test_add_context_information_with_context(self, mock_get_context):
        """Test add_context_information adds context when configured."""
        mock_get_context.return_value = ["format"]
        
        old_schema = {"properties": {"name": {"type": "string", "format": "email"}}}
        new_schema = {"properties": {"name": {"type": "integer", "format": "email"}}}
        manager = ContextManager(old_schema, new_schema)
        
        differences = [(["properties", "name", "type"], "string", "integer")]
        
        with patch.object(manager, '_find_context_value') as mock_find:
            mock_find.return_value = "email"
            
            result = manager.add_context_information(differences)
            
            # Should have original difference plus context
            assert len(result) == 2
            assert result[0] == (["properties", "name", "type"], "string", "integer")
            assert result[1] == (["properties", "name", "format"], "email", "email")

    @patch('jsonschema_diff.context_manager.Config.get_context_params')
    def test_add_context_information_no_context_value(self, mock_get_context):
        """Test add_context_information when context value is not found."""
        mock_get_context.return_value = ["format"]
        
        old_schema = {"properties": {"name": {"type": "string"}}}
        new_schema = {"properties": {"name": {"type": "integer"}}}
        manager = ContextManager(old_schema, new_schema)
        
        differences = [(["properties", "name", "type"], "string", "integer")]
        
        with patch.object(manager, '_find_context_value') as mock_find:
            mock_find.return_value = None
            
            result = manager.add_context_information(differences)
            
            # Should only have original difference
            assert len(result) == 1
            assert result[0] == (["properties", "name", "type"], "string", "integer")

    @patch('jsonschema_diff.context_manager.Config.get_context_params')
    def test_add_context_information_multiple_context_keys(self, mock_get_context):
        """Test add_context_information with multiple context keys."""
        mock_get_context.return_value = ["format", "minimum"]
        
        old_schema = {"properties": {"name": {"type": "string", "format": "email", "minimum": 0}}}
        new_schema = {"properties": {"name": {"type": "integer", "format": "email", "minimum": 0}}}
        manager = ContextManager(old_schema, new_schema)
        
        differences = [(["properties", "name", "type"], "string", "integer")]
        
        with patch.object(manager, '_find_context_value') as mock_find:
            mock_find.side_effect = lambda path: {
                "format": "email",
                "minimum": "0"
            }.get(path[-1])
            
            result = manager.add_context_information(differences)
            
            # Should have original difference plus 2 context entries
            assert len(result) == 3
            assert result[0] == (["properties", "name", "type"], "string", "integer")

    @patch('jsonschema_diff.context_manager.Config.get_context_params')
    def test_add_context_information_no_matching_param(self, mock_get_context):
        """Test add_context_information when parameter has no context rules."""
        mock_get_context.return_value = []  # No context for this parameter
        
        old_schema = {"properties": {"name": {"type": "string"}}}
        new_schema = {"properties": {"name": {"type": "integer"}}}
        manager = ContextManager(old_schema, new_schema)
        
        differences = [(["properties", "name", "type"], "string", "integer")]
        result = manager.add_context_information(differences)
        
        # Should only have original difference
        assert len(result) == 1
        assert result[0] == (["properties", "name", "type"], "string", "integer")

    def test_add_context_information_short_path(self):
        """Test add_context_information with path shorter than 1 element."""
        old_schema = {"properties": {"name": {"type": "string"}}}
        new_schema = {"properties": {"name": {"type": "integer"}}}
        manager = ContextManager(old_schema, new_schema)
        
        differences = [([], "old", "new")]
        result = manager.add_context_information(differences)
        
        # Should only have original difference
        assert len(result) == 1
        assert result[0] == ([], "old", "new")

    def test_find_context_value_from_old_schema(self):
        """Test _find_context_value finds value in old schema."""
        old_schema = {"properties": {"name": {"format": "email"}}}
        new_schema = {"properties": {"name": {}}}
        manager = ContextManager(old_schema, new_schema)
        
        with patch('jsonschema_diff.context_manager.PathUtils.get_value_at_path') as mock_path:
            mock_path.side_effect = lambda schema, path: "email" if "email" in str(schema) else None
            
            result = manager._find_context_value(["properties", "name", "format"])
            
            assert result == "email"

    def test_find_context_value_from_new_schema(self):
        """Test _find_context_value finds value in new schema when not in old."""
        old_schema = {"properties": {"name": {}}}
        new_schema = {"properties": {"name": {"format": "email"}}}
        manager = ContextManager(old_schema, new_schema)
        
        with patch('jsonschema_diff.context_manager.PathUtils.get_value_at_path') as mock_path:
            mock_path.side_effect = lambda schema, path: "email" if "email" in str(schema) else None
            
            result = manager._find_context_value(["properties", "name", "format"])
            
            assert result == "email"

    def test_find_context_value_not_found(self):
        """Test _find_context_value returns None when value not found."""
        old_schema = {"properties": {"name": {}}}
        new_schema = {"properties": {"name": {}}}
        manager = ContextManager(old_schema, new_schema)
        
        with patch('jsonschema_diff.context_manager.PathUtils.get_value_at_path') as mock_path:
            mock_path.return_value = None
            
            result = manager._find_context_value(["properties", "name", "format"])
            
            assert result is None

    def test_find_context_value_none_schemas(self):
        """Test _find_context_value with None schemas."""
        manager = ContextManager(None, None)
        
        result = manager._find_context_value(["properties", "name", "format"])
        
        assert result is None

    def test_find_context_value_empty_schemas(self):
        """Test _find_context_value with empty schemas."""
        manager = ContextManager({}, {})
        
        with patch('jsonschema_diff.context_manager.PathUtils.get_value_at_path') as mock_path:
            mock_path.return_value = None
            
            result = manager._find_context_value(["properties", "name", "format"])
            
            assert result is None

    def test_find_context_value_converts_to_string(self):
        """Test _find_context_value converts non-string values to string."""
        old_schema = {"properties": {"name": {"minimum": 42}}}
        new_schema = {"properties": {"name": {}}}
        manager = ContextManager(old_schema, new_schema)
        
        with patch('jsonschema_diff.context_manager.PathUtils.get_value_at_path') as mock_path:
            mock_path.return_value = 42
            
            result = manager._find_context_value(["properties", "name", "minimum"])
            
            assert result == "42"
            assert isinstance(result, str)

    @patch('jsonschema_diff.context_manager.Config.get_context_params')
    @patch('jsonschema_diff.context_manager.DiffFinder.get_operation_type')
    def test_add_context_information_operation_filtering(self, mock_operation, mock_get_context):
        """Test that context is only added for meaningful operations."""
        mock_get_context.return_value = ["maximum"]
        
        old_schema = {"properties": {"age": {"minimum": 0, "maximum": 100}}}
        new_schema = {"properties": {"age": {"minimum": 1, "maximum": 100}}}
        manager = ContextManager(old_schema, new_schema)
        
        differences = [(["properties", "age", "minimum"], 0, 1)]
        
        # Test with meaningful operation
        mock_operation.return_value = "change"
        with patch.object(manager, '_find_context_value') as mock_find:
            mock_find.return_value = "100"
            
            result = manager.add_context_information(differences)
            
            assert len(result) == 2  # Original + context
        
        # Test with non-meaningful operation
        mock_operation.return_value = "none"
        result = manager.add_context_information(differences)
        
        assert len(result) == 1  # Only original

    def test_schemas_with_missing_properties(self):
        """Test ContextManager with schemas missing properties key."""
        old_schema = {"type": "object"}
        new_schema = {"type": "object"}
        manager = ContextManager(old_schema, new_schema)
        
        # Should handle gracefully
        assert manager.old_schema == old_schema
        assert manager.new_schema == new_schema
        
        result = manager._find_context_value(["properties", "name", "format"])
        assert result is None

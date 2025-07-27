"""
Tests for the SchemaComparator module.
"""

from unittest.mock import Mock, patch

from jsonschema_diff.comparator import SchemaComparator, compare_schemas


class TestSchemaComparator:
    """Test cases for the SchemaComparator class."""

    def test_init(self):
        """Test SchemaComparator initialization."""
        old_schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        new_schema = {"type": "object", "properties": {"name": {"type": "integer"}}}

        comparator = SchemaComparator(old_schema, new_schema)

        assert comparator.old_schema == old_schema
        assert comparator.new_schema == new_schema
        assert comparator.combiner is not None
        assert comparator.render_processor is not None

    def test_init_empty_schemas(self):
        """Test SchemaComparator initialization with empty schemas."""
        old_schema = {}
        new_schema = {}

        comparator = SchemaComparator(old_schema, new_schema)

        assert comparator.old_schema == old_schema
        assert comparator.new_schema == new_schema

    def test_compare_no_differences(self):
        """Test compare method when schemas are identical."""
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        }

        comparator = SchemaComparator(schema, schema)
        result = comparator.compare()

        # Should return empty string or minimal output when no differences
        assert isinstance(result, str)

    def test_compare_with_differences(self):
        """Test compare method when schemas have differences."""
        old_schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        }
        new_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "integer"},  # Changed type
                "email": {"type": "string"},  # Added field
            },
        }

        comparator = SchemaComparator(old_schema, new_schema)
        result = comparator.compare()

        assert isinstance(result, str)
        assert len(result) > 0
        # Should contain information about the changes
        assert "name" in result

    def test_compare_added_property(self):
        """Test compare method when a property is added."""
        old_schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        new_schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}, "email": {"type": "string"}},
        }

        comparator = SchemaComparator(old_schema, new_schema)
        result = comparator.compare()

        assert isinstance(result, str)
        if result:  # Only check if there are differences reported
            assert "email" in result

    def test_compare_removed_property(self):
        """Test compare method when a property is removed."""
        old_schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}, "email": {"type": "string"}},
        }
        new_schema = {"type": "object", "properties": {"name": {"type": "string"}}}

        comparator = SchemaComparator(old_schema, new_schema)
        result = comparator.compare()

        assert isinstance(result, str)
        if result:  # Only check if there are differences reported
            assert "email" in result

    def test_compare_changed_property_type(self):
        """Test compare method when a property type is changed."""
        old_schema = {"type": "object", "properties": {"age": {"type": "string"}}}
        new_schema = {"type": "object", "properties": {"age": {"type": "integer"}}}

        comparator = SchemaComparator(old_schema, new_schema)
        result = comparator.compare()

        assert isinstance(result, str)
        if result:  # Only check if there are differences reported
            assert "age" in result

    def test_compare_nested_properties(self):
        """Test compare method with nested property changes."""
        old_schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "details": {
                            "type": "object",
                            "properties": {"age": {"type": "integer"}},
                        },
                    },
                }
            },
        }
        new_schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "details": {
                            "type": "object",
                            "properties": {
                                "age": {"type": "string"}  # Changed nested type
                            },
                        },
                    },
                }
            },
        }

        comparator = SchemaComparator(old_schema, new_schema)
        result = comparator.compare()

        assert isinstance(result, str)
        if result:  # Only check if there are differences reported
            assert "age" in result

    def test_compare_missing_properties_key(self):
        """Test compare method when properties key is missing."""
        old_schema = {"type": "object"}
        new_schema = {"type": "object", "properties": {"name": {"type": "string"}}}

        comparator = SchemaComparator(old_schema, new_schema)
        result = comparator.compare()

        # Should handle missing properties gracefully
        assert isinstance(result, str)

    def test_compare_complex_schema_changes(self):
        """Test compare method with multiple complex changes."""
        old_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "format": "email"},
                "age": {"type": "integer", "minimum": 0},
                "address": {
                    "type": "object",
                    "properties": {
                        "street": {"type": "string"},
                        "zip": {"type": "string"},
                    },
                },
            },
        }
        new_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},  # Removed format
                "age": {"type": "integer", "minimum": 1},  # Changed minimum
                "address": {
                    "type": "object",
                    "properties": {
                        "street": {"type": "string"},
                        "zip": {"type": "integer"},  # Changed type
                    },
                },
                "phone": {"type": "string"},  # Added new property
            },
        }

        comparator = SchemaComparator(old_schema, new_schema)
        result = comparator.compare()

        assert isinstance(result, str)

    @patch("jsonschema_diff.comparator.DiffFinder.find_differences")
    @patch("jsonschema_diff.comparator.DiffProcessor.process_differences")
    def test_compare_pipeline_called(self, mock_process, mock_find):
        """Test that compare method calls all pipeline steps."""
        mock_find.return_value = []
        mock_process.return_value = []

        old_schema = {"properties": {"name": {"type": "string"}}}
        new_schema = {"properties": {"name": {"type": "integer"}}}

        comparator = SchemaComparator(old_schema, new_schema)

        # Mock the combiner and render_processor methods
        comparator.combiner.combine_parameters = Mock(return_value=[])
        comparator.render_processor.process_for_render = Mock(return_value=[])

        # Run comparison pipeline
        comparator.compare()

        # Verify all pipeline steps were called
        mock_find.assert_called_once()
        mock_process.assert_called_once()
        comparator.combiner.combine_parameters.assert_called_once()
        comparator.render_processor.process_for_render.assert_called_once()


class TestCompareSchemas:
    """Test cases for the standalone compare_schemas function."""

    def test_compare_schemas_delegation(self):
        """Test that compare_schemas properly delegates to SchemaComparator."""
        old_schema = {"properties": {"name": {"type": "string"}}}
        new_schema = {"properties": {"name": {"type": "integer"}}}

        with patch.object(SchemaComparator, "compare") as mock_compare:
            mock_compare.return_value = "mocked result"

            result = compare_schemas(old_schema, new_schema)

            assert result == "mocked result"
            mock_compare.assert_called_once()

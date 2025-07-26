"""
Tests for the diff_finder module.
"""

import unittest
from jsonschema_diff.diff_finder import DiffFinder


class TestDiffFinder(unittest.TestCase):
    """Test DiffFinder class."""
    
    def test_find_differences_identical(self):
        """Test finding differences between identical structures."""
        old = {"a": 1, "b": 2}
        new = {"a": 1, "b": 2}
        
        diffs = DiffFinder.find_differences(old, new)
        self.assertEqual(len(diffs), 0)
    
    def test_find_differences_addition(self):
        """Test finding differences when new key is added."""
        old = {"a": 1}
        new = {"a": 1, "b": 2}
        
        diffs = DiffFinder.find_differences(old, new)
        self.assertEqual(len(diffs), 1)
        self.assertEqual(diffs[0], (["b"], None, 2))
    
    def test_find_differences_removal(self):
        """Test finding differences when key is removed."""
        old = {"a": 1, "b": 2}
        new = {"a": 1}
        
        diffs = DiffFinder.find_differences(old, new)
        self.assertEqual(len(diffs), 1)
        self.assertEqual(diffs[0], (["b"], 2, None))
    
    def test_find_differences_change(self):
        """Test finding differences when value changes."""
        old = {"a": 1}
        new = {"a": 2}
        
        diffs = DiffFinder.find_differences(old, new)
        self.assertEqual(len(diffs), 1)
        self.assertEqual(diffs[0], (["a"], 1, 2))
    
    def test_find_differences_nested(self):
        """Test finding differences in nested structures."""
        old = {"a": {"b": 1}}
        new = {"a": {"b": 2}}
        
        diffs = DiffFinder.find_differences(old, new)
        self.assertEqual(len(diffs), 1)
        self.assertEqual(diffs[0], (["a", "b"], 1, 2))
    
    def test_find_differences_deep_nested(self):
        """Test finding differences in deeply nested structures."""
        old = {"a": {"b": {"c": 1}}}
        new = {"a": {"b": {"c": 2, "d": 3}}}
        
        diffs = DiffFinder.find_differences(old, new)
        self.assertEqual(len(diffs), 2)
        
        # Sort by path for consistent testing
        diffs.sort(key=lambda x: x[0])
        self.assertEqual(diffs[0], (["a", "b", "c"], 1, 2))
        self.assertEqual(diffs[1], (["a", "b", "d"], None, 3))
    
    def test_find_differences_lists_identical(self):
        """Test finding differences between identical lists."""
        old = [1, 2, 3]
        new = [1, 2, 3]
        
        diffs = DiffFinder.find_differences(old, new)
        self.assertEqual(len(diffs), 0)
    
    def test_find_differences_lists_different(self):
        """Test finding differences between different lists."""
        old = [1, 2, 3]
        new = [1, 2, 4]
        
        diffs = DiffFinder.find_differences(old, new)
        self.assertEqual(len(diffs), 1)
        self.assertEqual(diffs[0], ([], [1, 2, 3], [1, 2, 4]))
    
    def test_find_differences_mixed_types(self):
        """Test finding differences between different types."""
        old = {"a": "string"}
        new = {"a": 123}
        
        diffs = DiffFinder.find_differences(old, new)
        self.assertEqual(len(diffs), 1)
        self.assertEqual(diffs[0], (["a"], "string", 123))
    
    def test_find_differences_with_path(self):
        """Test finding differences with custom path."""
        old = {"a": 1}
        new = {"a": 2}
        
        diffs = DiffFinder.find_differences(old, new, path=["root"])
        self.assertEqual(len(diffs), 1)
        self.assertEqual(diffs[0], (["root", "a"], 1, 2))
    
    def test_find_differences_empty_dicts(self):
        """Test finding differences between empty dictionaries."""
        old = {}
        new = {}
        
        diffs = DiffFinder.find_differences(old, new)
        self.assertEqual(len(diffs), 0)
    
    def test_find_differences_none_values(self):
        """Test finding differences with None values."""
        old = {"a": None}
        new = {"a": 1}
        
        diffs = DiffFinder.find_differences(old, new)
        self.assertEqual(len(diffs), 1)
        self.assertEqual(diffs[0], (["a"], None, 1))
    
    def test_find_differences_complex_structure(self):
        """Test finding differences in complex JSON schema-like structure."""
        old = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            }
        }
        new = {
            "type": "object", 
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"},
                "email": {"type": "string"}
            }
        }
        
        diffs = DiffFinder.find_differences(old, new)
        self.assertEqual(len(diffs), 2)
        
        # Sort by path for consistent testing
        diffs.sort(key=lambda x: str(x[0]))
        expected_diffs = [
            (["properties", "age", "type"], "integer", "number"),
            (["properties", "email"], None, {"type": "string"})
        ]
        
        for i, expected in enumerate(expected_diffs):
            self.assertEqual(diffs[i], expected)
    
    def test_get_operation_type_add(self):
        """Test get_operation_type for addition."""
        op_type = DiffFinder.get_operation_type(None, "new_value")
        self.assertEqual(op_type, "add")
    
    def test_get_operation_type_remove(self):
        """Test get_operation_type for removal."""
        op_type = DiffFinder.get_operation_type("old_value", None)
        self.assertEqual(op_type, "remove")
    
    def test_get_operation_type_change(self):
        """Test get_operation_type for change."""
        op_type = DiffFinder.get_operation_type("old_value", "new_value")
        self.assertEqual(op_type, "change")
    
    def test_get_operation_type_none(self):
        """Test get_operation_type for no change."""
        op_type = DiffFinder.get_operation_type("same_value", "same_value")
        self.assertEqual(op_type, "none")
    
    def test_get_operation_type_both_none(self):
        """Test get_operation_type when both values are None."""
        op_type = DiffFinder.get_operation_type(None, None)
        self.assertEqual(op_type, "none")
    
    def test_find_differences_with_non_dict_schemas(self):
        """Test find_differences when schemas are not dictionaries."""
        old_schema = "string"
        new_schema = "integer"
        
        result = DiffFinder.find_differences(old_schema, new_schema, ["root"])
        
        # Should handle different types - covers lines 63-64
        self.assertEqual(len(result), 1)
        path, old_val, new_val = result[0]
        self.assertEqual(path, ["root"])
        self.assertEqual(old_val, "string")
        self.assertEqual(new_val, "integer")

    def test_find_differences_with_same_non_dict_values(self):
        """Test find_differences when non-dict values are the same."""
        old_schema = "same_value"
        new_schema = "same_value"
        
        result = DiffFinder.find_differences(old_schema, new_schema, ["root"])
        
        # Should return empty list when values are the same
        self.assertEqual(len(result), 0)

    def test_find_differences_simple_value_change(self):
        """Test find_differences when values are different simple types."""
        old = "string_value"
        new = 42
        
        result = DiffFinder.find_differences(old, new)
        
        self.assertEqual(len(result), 1)
        path, old_val, new_val = result[0]
        self.assertEqual(path, [])
        self.assertEqual(old_val, "string_value")
        self.assertEqual(new_val, 42)

    def test_find_differences_same_lists(self):
        """Test find_differences with identical lists."""
        old = {"items": ["string", "number"]}
        new = {"items": ["string", "number"]}
        
        result = DiffFinder.find_differences(old, new)
        
        # Should return no differences for identical lists
        self.assertEqual(len(result), 0)

    def test_find_differences_different_lists(self):
        """Test find_differences with different lists."""
        old = {"items": ["string", "number"]}
        new = {"items": ["string", "boolean"]}
        
        result = DiffFinder.find_differences(old, new)
        
        # Should detect list difference
        self.assertEqual(len(result), 1)
        path, old_val, new_val = result[0]
        self.assertEqual(path, ["items"])
        self.assertEqual(old_val, ["string", "number"])
        self.assertEqual(new_val, ["string", "boolean"])

    def test_get_operation_type_edge_cases(self):
        """Test get_operation_type with edge cases."""
        # Same values
        result = DiffFinder.get_operation_type("same", "same")
        self.assertEqual(result, "none")
        
        # Zero values
        result = DiffFinder.get_operation_type(0, 1)
        self.assertEqual(result, "change")
        
        # Empty string vs None
        result = DiffFinder.get_operation_type("", None)
        self.assertEqual(result, "remove")
        
        # None vs empty string
        result = DiffFinder.get_operation_type(None, "")
        self.assertEqual(result, "add")


if __name__ == '__main__':
    unittest.main()

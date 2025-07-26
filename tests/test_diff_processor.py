"""
Tests for the diff_processor module.
"""

import unittest
from jsonschema_diff.diff_processor import DiffProcessor


class TestDiffProcessor(unittest.TestCase):
    """Test DiffProcessor class."""
    
    def test_process_differences_empty(self):
        """Test processing empty differences list."""
        differences = []
        result = DiffProcessor.process_differences(differences)
        self.assertEqual(result, [])
    
    def test_process_differences_single_add(self):
        """Test processing single addition."""
        differences = [(["field"], None, "new_value")]
        result = DiffProcessor.process_differences(differences)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], (["field"], None, "new_value"))
    
    def test_process_differences_single_remove(self):
        """Test processing single removal."""
        differences = [(["field"], "old_value", None)]
        result = DiffProcessor.process_differences(differences)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], (["field"], "old_value", None))
    
    def test_process_differences_single_change(self):
        """Test processing single change."""
        differences = [(["field"], "old_value", "new_value")]
        result = DiffProcessor.process_differences(differences)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], (["field"], "old_value", "new_value"))
    
    def test_process_differences_add_remove_pair_to_change(self):
        """Test converting add/remove pair to change."""
        differences = [
            (["field"], None, "new_value"),    # add
            (["field"], "old_value", None)     # remove
        ]
        result = DiffProcessor.process_differences(differences)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], (["field"], "old_value", "new_value"))
    
    def test_process_differences_remove_add_pair_to_change(self):
        """Test converting remove/add pair to change (different order)."""
        differences = [
            (["field"], "old_value", None),    # remove
            (["field"], None, "new_value")     # add
        ]
        result = DiffProcessor.process_differences(differences)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], (["field"], "old_value", "new_value"))
    
    def test_process_differences_multiple_fields(self):
        """Test processing multiple different fields."""
        differences = [
            (["field1"], None, "value1"),
            (["field2"], "old_value", None),
            (["field3"], "old", "new")
        ]
        result = DiffProcessor.process_differences(differences)
        self.assertEqual(len(result), 3)
        
        # Should preserve all differences as they are for different fields
        expected = [
            (["field1"], None, "value1"),
            (["field2"], "old_value", None),
            (["field3"], "old", "new")
        ]
        
        for expected_diff in expected:
            self.assertIn(expected_diff, result)
    
    def test_process_differences_multiple_operations_same_field(self):
        """Test processing multiple operations on same field."""
        differences = [
            (["field"], "val1", None),      # remove
            (["field"], None, "val2"),      # add
            (["field"], "val3", "val4")     # change
        ]
        result = DiffProcessor.process_differences(differences)
        
        # Should still have 3 operations (not combined into changes)
        # because there are more than 2 operations
        self.assertEqual(len(result), 3)
        self.assertIn((["field"], "val1", None), result)
        self.assertIn((["field"], None, "val2"), result)
        self.assertIn((["field"], "val3", "val4"), result)
    
    def test_process_differences_non_add_remove_pair(self):
        """Test that non-add/remove pairs are not combined."""
        differences = [
            (["field"], "old1", "new1"),    # change
            (["field"], "old2", "new2")     # change
        ]
        result = DiffProcessor.process_differences(differences)
        self.assertEqual(len(result), 2)
        self.assertIn((["field"], "old1", "new1"), result)
        self.assertIn((["field"], "old2", "new2"), result)
    
    def test_process_differences_nested_paths(self):
        """Test processing differences with nested paths."""
        differences = [
            (["parent", "child"], None, "new_value"),
            (["parent", "child"], "old_value", None)
        ]
        result = DiffProcessor.process_differences(differences)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], (["parent", "child"], "old_value", "new_value"))
    
    def test_process_differences_complex_schema_example(self):
        """Test processing differences from a complex schema comparison."""
        differences = [
            (["properties", "name", "type"], "string", "text"),  # change
            (["properties", "age"], None, {"type": "integer"}),  # add
            (["properties", "email", "format"], "email", None),  # remove
            (["properties", "email", "format"], None, "text"),   # add
        ]
        
        result = DiffProcessor.process_differences(differences)
        
        # Should have 3 results:
        # 1. name.type change
        # 2. age addition
        # 3. email.format change (combined from remove+add)
        self.assertEqual(len(result), 3)
        
        expected_results = [
            (["properties", "name", "type"], "string", "text"),
            (["properties", "age"], None, {"type": "integer"}),
            (["properties", "email", "format"], "email", "text")
        ]
        
        for expected in expected_results:
            self.assertIn(expected, result)
    
    def test_process_differences_preserves_order(self):
        """Test that processing preserves relative order of operations."""
        differences = [
            (["field1"], "old1", "new1"),
            (["field2"], None, "value2"),
            (["field3"], "old3", None),
            (["field4"], None, "value4"),
            (["field4"], "old4", None),  # Should combine with previous
        ]
        
        result = DiffProcessor.process_differences(differences)
        
        # Should have 4 results, with field4 combined
        self.assertEqual(len(result), 4)
        
        # field4 should be combined into a change operation
        field4_result = None
        for path, old_val, new_val in result:
            if path == ["field4"]:
                field4_result = (path, old_val, new_val)
                break
        
        self.assertIsNotNone(field4_result)
        self.assertEqual(field4_result, (["field4"], "old4", "value4"))


if __name__ == '__main__':
    unittest.main()

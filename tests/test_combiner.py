"""
Tests for the combiner module.
"""

import unittest
from unittest.mock import Mock, patch
from jsonschema_diff.combiner import ParameterCombiner
from jsonschema_diff.config import Config, CombineMode


class TestParameterCombiner(unittest.TestCase):
    """Test ParameterCombiner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.old_schema = {
            "properties": {
                "field1": {"type": "string", "format": "email"},
                "field2": {"type": "integer"},
                "field3": {"type": "string", "format": "date"},
                "field4": {"minimum": 0, "maximum": 100}
            }
        }
        
        self.new_schema = {
            "properties": {
                "field1": {"type": "string", "format": "url"},
                "field2": {"type": "number", "format": "float"},
                "field3": {"type": "string"},
                "field4": {"minimum": 10, "maximum": 90}
            }
        }
        
        self.combiner = ParameterCombiner(self.old_schema, self.new_schema)
    
    def test_init(self):
        """Test ParameterCombiner initialization."""
        self.assertEqual(self.combiner.old_schema, self.old_schema)
        self.assertEqual(self.combiner.new_schema, self.new_schema)
    
    def test_combine_parameters_empty(self):
        """Test combining empty differences list."""
        differences = []
        result = self.combiner.combine_parameters(differences)
        self.assertEqual(result, [])
    
    def test_combine_parameters_no_combinable(self):
        """Test combining differences with no combinable parameters."""
        differences = [
            (["properties", "field", "description"], "old", "new")
        ]
        result = self.combiner.combine_parameters(differences)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], (["properties", "field", "description"], "old", "new"))
    
    def test_combine_type_and_format_both_change(self):
        """Test combining type and format when both change."""
        differences = [
            (["properties", "field1", "type"], "string", "number"),
            (["properties", "field1", "format"], "email", "float")
        ]
        result = self.combiner.combine_parameters(differences)
        
        # Should combine into single type change
        self.assertEqual(len(result), 1)
        path, old_val, new_val = result[0]
        self.assertEqual(path, ["properties", "field1", "type"])
        self.assertEqual(old_val, "string/email")
        self.assertEqual(new_val, "number/float")
    
    def test_combine_type_changes_format_same(self):
        """Test combining when type changes but format exists in schema."""
        differences = [
            (["properties", "field1", "type"], "string", "number")
        ]
        result = self.combiner.combine_parameters(differences)
        
        # Since no format difference exists, type should not be combined
        self.assertEqual(len(result), 1)
        path, old_val, new_val = result[0]
        self.assertEqual(path, ["properties", "field1", "type"])
        self.assertEqual(old_val, "string")  # Unchanged
        self.assertEqual(new_val, "number")  # Unchanged
    
    def test_combine_format_changes_type_same(self):
        """Test combining when format changes but type exists in schema."""
        differences = [
            (["properties", "field1", "format"], "email", "url")
        ]
        result = self.combiner.combine_parameters(differences)
        
        # Should combine with type from schema
        self.assertEqual(len(result), 1)
        path, old_val, new_val = result[0]
        self.assertEqual(path, ["properties", "field1", "type"])
        self.assertIn("string", old_val)  # type from schema
        self.assertIn("email", old_val)   # old format
        self.assertIn("string", new_val)  # type from schema
        self.assertIn("url", new_val)     # new format
    
    def test_no_combination_when_rules_dont_match(self):
        """Test no combination when rules don't allow it."""
        # minimum/maximum are configured to not combine on addition
        differences = [
            (["properties", "field", "minimum"], None, 10)
        ]
        result = self.combiner.combine_parameters(differences)
        
        # Should not combine
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], (["properties", "field", "minimum"], None, 10))
    
    def test_get_operation_type(self):
        """Test _get_operation_type method."""
        # Test add
        op_type = self.combiner._get_operation_type(None, "new")
        self.assertEqual(op_type, "add")
        
        # Test remove
        op_type = self.combiner._get_operation_type("old", None)
        self.assertEqual(op_type, "remove")
        
        # Test change
        op_type = self.combiner._get_operation_type("old", "new")
        self.assertEqual(op_type, "change")
        
        # Test none
        op_type = self.combiner._get_operation_type("same", "same")
        self.assertEqual(op_type, "none")
    
    def test_can_combine_main_param_change(self):
        """Test _can_combine for main parameter change."""
        rule = Config.get_combination_rules()[0]  # type/format rule
        
        # Should allow combination for change
        can_combine = self.combiner._can_combine(rule, ["field", "type"], "old", "new", "main")
        self.assertTrue(can_combine)
        
        # Should allow combination for addition
        can_combine = self.combiner._can_combine(rule, ["field", "type"], None, "new", "main")
        self.assertTrue(can_combine)
        
        # Should allow combination for removal
        can_combine = self.combiner._can_combine(rule, ["field", "type"], "old", None, "main")
        self.assertTrue(can_combine)
    
    def test_can_combine_sub_param_change(self):
        """Test _can_combine for sub parameter change."""
        rule = Config.get_combination_rules()[0]  # type/format rule
        
        # Should allow combination for change
        can_combine = self.combiner._can_combine(rule, ["field", "format"], "old", "new", "sub")
        self.assertTrue(can_combine)
    
    @patch('jsonschema_diff.combiner.Config.get_combination_rules')
    def test_can_combine_with_none_rules(self, mock_get_rules):
        """Test _can_combine with rules that don't allow combination."""
        from jsonschema_diff.config import CombinationRule, CombinationRules, CombineMode
        
        # Create rule that doesn't allow combination
        mock_rule = CombinationRule(
            main_param="test",
            sub_param="format",
            display_name="test",
            format_template="{main}/{sub}",
            rules=CombinationRules(
                removal=CombineMode.NONE,
                addition=CombineMode.NONE,
                change=CombineMode.NONE
            )
        )
        mock_get_rules.return_value = [mock_rule]
        
        combiner = ParameterCombiner({}, {})
        can_combine = combiner._can_combine(mock_rule, ["field", "test"], "old", "new", "main")
        self.assertFalse(can_combine)
    
    def test_build_combined_value_both_values(self):
        """Test _build_combined_value with both values present."""
        rule = Config.get_combination_rules()[0]  # type/format rule
        
        result = self.combiner._build_combined_value(rule, "string", "email")
        self.assertEqual(result, "string/email")
    
    def test_build_combined_value_main_only(self):
        """Test _build_combined_value with only main value."""
        rule = Config.get_combination_rules()[0]  # type/format rule
        
        result = self.combiner._build_combined_value(rule, "string", None)
        self.assertEqual(result, "string")
    
    def test_build_combined_value_sub_only(self):
        """Test _build_combined_value with only sub value."""
        rule = Config.get_combination_rules()[0]  # type/format rule
        
        result = self.combiner._build_combined_value(rule, None, "email")
        self.assertEqual(result, "email")
    
    def test_build_combined_value_both_none(self):
        """Test _build_combined_value with both values None."""
        rule = Config.get_combination_rules()[0]  # type/format rule
        
        result = self.combiner._build_combined_value(rule, None, None)
        self.assertIsNone(result)
    
    def test_create_virtual_param_same_value(self):
        """Test _create_virtual_param when value is same in both schemas."""
        path = ["properties", "field1", "format"]
        rule = Config.get_combination_rules()[0]
        
        # Modify schemas so format is same in both
        old_schema = {"properties": {"field1": {"format": "email"}}}
        new_schema = {"properties": {"field1": {"format": "email"}}}
        combiner = ParameterCombiner(old_schema, new_schema)
        
        result = combiner._create_virtual_param(path, rule, "sub")
        self.assertIsNotNone(result)
        self.assertEqual(result, (path, "email", "email"))
    
    def test_create_virtual_param_no_value(self):
        """Test _create_virtual_param when value doesn't exist."""
        path = ["properties", "nonexistent", "format"]
        rule = Config.get_combination_rules()[0]
        
        result = self.combiner._create_virtual_param(path, rule, "sub")
        self.assertIsNone(result)
    
    def test_get_schema_value(self):
        """Test _get_schema_value method."""
        path = ["properties", "field1", "format"]
        result = self.combiner._get_schema_value(path, self.old_schema)
        self.assertEqual(result, "email")
        
        # Test non-existent path
        path = ["properties", "nonexistent", "format"]
        result = self.combiner._get_schema_value(path, self.old_schema)
        self.assertIsNone(result)
        
        # Test empty schema
        result = self.combiner._get_schema_value(path, {})
        self.assertIsNone(result)
    
    def test_combine_params_method(self):
        """Test _combine_params method."""
        rule = Config.get_combination_rules()[0]  # type/format rule
        main_diff = (["properties", "field", "type"], "string", "number")
        sub_diff = (["properties", "field", "format"], "email", "float")
        
        result = self.combiner._combine_params(rule, main_diff, sub_diff)
        
        path, old_val, new_val = result
        self.assertEqual(path, ["properties", "field", "type"])  # Uses display_name
        self.assertEqual(old_val, "string/email")
        self.assertEqual(new_val, "number/float")
    
    def test_complex_combination_scenario(self):
        """Test complex scenario with multiple combinations."""
        differences = [
            (["properties", "field1", "type"], "string", "number"),
            (["properties", "field1", "format"], "email", "float"),
            (["properties", "field2", "type"], "integer", "string"),
            (["properties", "field3", "format"], "date", None),
        ]
        
        result = self.combiner.combine_parameters(differences)
        
        # Should have 3 results:
        # 1. field1: combined type/format
        # 2. field2: type change only (no format in schema)
        # 3. field3: combined with type from schema
        self.assertEqual(len(result), 3)
        
        # Check that field1 was combined
        field1_result = None
        for path, old_val, new_val in result:
            if path == ["properties", "field1", "type"]:
                field1_result = (path, old_val, new_val)
                break
        
        self.assertIsNotNone(field1_result)
        _, old_val, new_val = field1_result
        self.assertEqual(old_val, "string/email")
        self.assertEqual(new_val, "number/float")
    
    def test_can_combine_with_none_mode(self):
        """Test _can_combine method with CombineMode.NONE."""
        from jsonschema_diff.config import CombinationRule, CombinationRules, CombineMode
        
        rule = CombinationRule(
            main_param="type",
            sub_param="format",
            display_name="type",
            format_template="{main}/{sub}",
            rules=CombinationRules(
                removal=CombineMode.NONE,
                addition=CombineMode.NONE,
                change=CombineMode.NONE
            )
        )
        
        result = self.combiner._can_combine(rule, ["properties", "field", "type"], "old", "new", "main")
        self.assertFalse(result)

    def test_can_combine_with_main_only_mode_sub_param(self):
        """Test _can_combine method with CombineMode.MAIN_ONLY and sub param."""
        from jsonschema_diff.config import CombinationRule, CombinationRules, CombineMode
        
        rule = CombinationRule(
            main_param="type",
            sub_param="format",
            display_name="type",
            format_template="{main}/{sub}",
            rules=CombinationRules(
                removal=CombineMode.MAIN_ONLY,
                addition=CombineMode.MAIN_ONLY,
                change=CombineMode.MAIN_ONLY
            )
        )
        
        result = self.combiner._can_combine(rule, ["properties", "field", "type"], "old", "new", "sub")
        self.assertFalse(result)

    def test_can_combine_with_sub_only_mode_main_param(self):
        """Test _can_combine method with CombineMode.SUB_ONLY and main param."""
        from jsonschema_diff.config import CombinationRule, CombinationRules, CombineMode
        
        rule = CombinationRule(
            main_param="type",
            sub_param="format", 
            display_name="type",
            format_template="{main}/{sub}",
            rules=CombinationRules(
                removal=CombineMode.SUB_ONLY,
                addition=CombineMode.SUB_ONLY,
                change=CombineMode.SUB_ONLY
            )
        )
        
        result = self.combiner._can_combine(rule, ["properties", "field", "type"], "old", "new", "main")
        self.assertFalse(result)

    def test_can_combine_with_all_mode(self):
        """Test _can_combine method with CombineMode.ALL."""
        from jsonschema_diff.config import CombinationRule, CombinationRules, CombineMode
        
        rule = CombinationRule(
            main_param="type",
            sub_param="format",
            display_name="type",
            format_template="{main}/{sub}",
            rules=CombinationRules(
                removal=CombineMode.ALL,
                addition=CombineMode.ALL,
                change=CombineMode.ALL
            )
        )
        
        result = self.combiner._can_combine(rule, ["properties", "field", "type"], "old", "new", "main")
        self.assertTrue(result)

    def test_create_virtual_param_with_same_values(self):
        """Test _create_virtual_param when values are same in both schemas."""
        from jsonschema_diff.config import CombinationRule, CombinationRules, CombineMode
        
        # Set up schemas with same format value
        old_schema = {"properties": {"field": {"format": "email"}}}
        new_schema = {"properties": {"field": {"format": "email"}}}
        combiner = ParameterCombiner(old_schema, new_schema)
        
        rule = CombinationRule(
            main_param="type",
            sub_param="format",
            display_name="type",
            format_template="{main}/{sub}",
            rules=CombinationRules(
                removal=CombineMode.ALL,
                addition=CombineMode.ALL,
                change=CombineMode.ALL
            )
        )
        path = ["properties", "field", "format"]
        
        result = combiner._create_virtual_param(path, rule, "sub")
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], path)
        self.assertEqual(result[1], "email")
        self.assertEqual(result[2], "email")

    def test_create_virtual_param_with_different_values(self):
        """Test _create_virtual_param when values are different."""
        from jsonschema_diff.config import CombinationRule, CombinationRules, CombineMode
        
        old_schema = {"properties": {"field": {"format": "email"}}}
        new_schema = {"properties": {"field": {"format": "uri"}}}
        combiner = ParameterCombiner(old_schema, new_schema)
        
        rule = CombinationRule(
            main_param="type",
            sub_param="format",
            display_name="type",
            format_template="{main}/{sub}",
            rules=CombinationRules(
                removal=CombineMode.ALL,
                addition=CombineMode.ALL,
                change=CombineMode.ALL
            )
        )
        path = ["properties", "field", "format"]
        
        result = combiner._create_virtual_param(path, rule, "sub")
        
        self.assertIsNone(result)

    def test_create_virtual_param_with_missing_value(self):
        """Test _create_virtual_param when value is missing from schema."""
        from jsonschema_diff.config import CombinationRule, CombinationRules, CombineMode
        
        old_schema = {"properties": {"field": {}}}
        new_schema = {"properties": {"field": {}}}
        combiner = ParameterCombiner(old_schema, new_schema)
        
        rule = CombinationRule(
            main_param="type",
            sub_param="format",
            display_name="type",
            format_template="{main}/{sub}",
            rules=CombinationRules(
                removal=CombineMode.ALL,
                addition=CombineMode.ALL,
                change=CombineMode.ALL
            )
        )
        path = ["properties", "field", "format"]
        
        result = combiner._create_virtual_param(path, rule, "sub")
        
        self.assertIsNone(result)

    def test_build_combined_value_with_none_values(self):
        """Test _build_combined_value with various None combinations."""
        from jsonschema_diff.config import CombinationRule, CombinationRules, CombineMode
        
        rule = CombinationRule(
            main_param="type",
            sub_param="format",
            display_name="type",
            format_template="{main}/{sub}",
            rules=CombinationRules(
                removal=CombineMode.ALL,
                addition=CombineMode.ALL,
                change=CombineMode.ALL
            )
        )
        
        # Both None
        result = self.combiner._build_combined_value(rule, None, None)
        self.assertIsNone(result)
        
        # Main None, sub exists
        result = self.combiner._build_combined_value(rule, None, "email")
        self.assertEqual(result, "email")
        
        # Main exists, sub None
        result = self.combiner._build_combined_value(rule, "string", None)
        self.assertEqual(result, "string")

    def test_get_operation_type_all_cases(self):
        """Test _get_operation_type method with all possible cases."""
        # Add operation
        result = self.combiner._get_operation_type(None, "new_value")
        self.assertEqual(result, "add")
        
        # Remove operation
        result = self.combiner._get_operation_type("old_value", None)
        self.assertEqual(result, "remove")
        
        # Change operation
        result = self.combiner._get_operation_type("old_value", "new_value")
        self.assertEqual(result, "change")
        
        # No change (same values)
        result = self.combiner._get_operation_type("same_value", "same_value")
        self.assertEqual(result, "none")
    
    def test_can_combine_return_false_fallback(self):
        """Test _can_combine method fallback return False."""
        from jsonschema_diff.config import CombinationRule, CombinationRules, CombineMode
        
        rule = CombinationRule(
            main_param="type",
            sub_param="format",
            display_name="type",
            format_template="{main}/{sub}",
            rules=CombinationRules(
                removal=CombineMode.NONE,
                addition=CombineMode.NONE,
                change=CombineMode.NONE
            )
        )
        
        # Test with "none" operation - should hit return False at line 132
        result = self.combiner._can_combine(rule, ["properties", "field", "type"], "same", "same", "main")
        self.assertFalse(result)

    def test_get_schema_value_with_empty_schema(self):
        """Test _get_schema_value with empty schema."""
        combiner = ParameterCombiner({}, {})
        
        result = combiner._get_schema_value(["properties", "field", "type"], {})
        self.assertIsNone(result)

    def test_edge_cases_coverage(self):
        """Test edge cases to improve coverage."""
        from jsonschema_diff.config import CombinationRule, CombinationRules, CombineMode
        
        # Test _can_combine with unknown operation
        rule = CombinationRule(
            main_param="type",
            sub_param="format",
            display_name="type",
            format_template="{main}/{sub}",
            rules=CombinationRules(
                removal=CombineMode.ALL,
                addition=CombineMode.ALL,
                change=CombineMode.ALL
            )
        )
        
        # Test with an unknown operation - should return False
        result = self.combiner._can_combine(rule, ["properties", "field", "type"], "old", "new", "main")
        # This depends on _get_operation_type returning something other than add/remove/change
        
        # Test _get_operation_type with same values (should return "none") 
        result = self.combiner._get_operation_type("same", "same")
        self.assertEqual(result, "none")

    def test_find_or_create_main_param_not_found(self):
        """Test _find_or_create_main_param when parameter is not found."""
        from jsonschema_diff.config import CombinationRule, CombinationRules, CombineMode
        
        rule = CombinationRule(
            main_param="type",
            sub_param="format",
            display_name="type",
            format_template="{main}/{sub}",
            rules=CombinationRules(
                removal=CombineMode.ALL,
                addition=CombineMode.ALL,
                change=CombineMode.ALL
            )
        )
        
        # Test with differences that don't contain the main parameter
        differences = [
            (["properties", "other_field", "format"], "email", "url")
        ]
        
        result = self.combiner._find_or_create_main_param(
            differences, ["properties", "field", "type"], rule, "format"
        )
        
        # Should try to create virtual parameter, which will likely return None
        # since the schemas don't contain the required field
        # This tests the _create_virtual_param path
        self.assertIsNone(result)

    def test_get_operation_type_none_case(self):
        """Test _get_operation_type returning 'none' for identical values."""
        result = self.combiner._get_operation_type("same", "same")
        self.assertEqual(result, "none")
    
    def test_create_virtual_param_none_old_value(self):
        """Test _create_virtual_param when old_value is None."""
        from jsonschema_diff.config import CombinationRule, CombinationRules, CombineMode
        
        # Schema where old has None, new has value
        old_schema = {"properties": {"field": {}}}  # No format
        new_schema = {"properties": {"field": {"format": "email"}}}
        combiner = ParameterCombiner(old_schema, new_schema)
        
        rule = CombinationRule(
            main_param="type",
            sub_param="format",
            display_name="type",
            format_template="{main}/{sub}",
            rules=CombinationRules(
                removal=CombineMode.ALL,
                addition=CombineMode.ALL,
                change=CombineMode.ALL
            )
        )
        path = ["properties", "field", "format"]
        
        result = combiner._create_virtual_param(path, rule, "sub")
        
        # Should return None because values are different (None != "email")
        self.assertIsNone(result)

    def test_build_combined_value_both_values_template(self):
        """Test _build_combined_value when both values exist, using template."""
        from jsonschema_diff.config import CombinationRule, CombinationRules, CombineMode
        
        rule = CombinationRule(
            main_param="type",
            sub_param="format",
            display_name="type",
            format_template="{main}/{sub}",
            rules=CombinationRules(
                removal=CombineMode.ALL,
                addition=CombineMode.ALL,
                change=CombineMode.ALL
            )
        )
        
        # Both values exist - should use template
        result = self.combiner._build_combined_value(rule, "string", "email")
        self.assertEqual(result, "string/email")
    

if __name__ == '__main__':
    unittest.main()

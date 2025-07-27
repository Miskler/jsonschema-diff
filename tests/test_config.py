"""
Tests for the configuration module.
"""

import unittest

from jsonschema_diff.config import (
    TYPE_MAP,
    CombinationRule,
    CombinationRules,
    CombineMode,
    Config,
    ContextRule,
    DisplayMode,
)


class TestDisplayMode(unittest.TestCase):
    """Test DisplayMode dataclass."""

    def test_display_mode_creation(self):
        """Test creating a DisplayMode instance."""
        mode = DisplayMode(color="red", symbol="-")
        self.assertEqual(mode.color, "red")
        self.assertEqual(mode.symbol, "-")

    def test_display_mode_frozen(self):
        """Test that DisplayMode is frozen (immutable)."""
        mode = DisplayMode(color="red", symbol="-")
        with self.assertRaises(AttributeError):
            mode.color = "blue"


class TestContextRule(unittest.TestCase):
    """Test ContextRule dataclass."""

    def test_context_rule_creation(self):
        """Test creating a ContextRule instance."""
        rule = ContextRule(trigger_param="type", context_params=["format"])
        self.assertEqual(rule.trigger_param, "type")
        self.assertEqual(rule.context_params, ["format"])

    def test_context_rule_frozen(self):
        """Test that ContextRule is frozen (immutable)."""
        rule = ContextRule(trigger_param="type", context_params=["format"])
        with self.assertRaises(AttributeError):
            rule.trigger_param = "other"


class TestCombineMode(unittest.TestCase):
    """Test CombineMode enum."""

    def test_combine_mode_values(self):
        """Test all CombineMode enum values."""
        self.assertEqual(CombineMode.MAIN_ONLY.value, "main_only")
        self.assertEqual(CombineMode.SUB_ONLY.value, "sub_only")
        self.assertEqual(CombineMode.ALL.value, "all")
        self.assertEqual(CombineMode.NONE.value, "none")


class TestCombinationRules(unittest.TestCase):
    """Test CombinationRules dataclass."""

    def test_combination_rules_creation(self):
        """Test creating a CombinationRules instance."""
        rules = CombinationRules(
            removal=CombineMode.ALL,
            addition=CombineMode.MAIN_ONLY,
            change=CombineMode.SUB_ONLY,
        )
        self.assertEqual(rules.removal, CombineMode.ALL)
        self.assertEqual(rules.addition, CombineMode.MAIN_ONLY)
        self.assertEqual(rules.change, CombineMode.SUB_ONLY)


class TestCombinationRule(unittest.TestCase):
    """Test CombinationRule dataclass."""

    def test_combination_rule_creation(self):
        """Test creating a CombinationRule instance."""
        rules = CombinationRules(
            removal=CombineMode.ALL, addition=CombineMode.ALL, change=CombineMode.ALL
        )
        rule = CombinationRule(
            main_param="type",
            sub_param="format",
            display_name="type",
            format_template="{main}/{sub}",
            rules=rules,
        )
        self.assertEqual(rule.main_param, "type")
        self.assertEqual(rule.sub_param, "format")
        self.assertEqual(rule.display_name, "type")
        self.assertEqual(rule.format_template, "{main}/{sub}")
        self.assertEqual(rule.rules, rules)


class TestConfig(unittest.TestCase):
    """Test Config class."""

    def test_modes_configuration(self):
        """Test MODES configuration."""
        self.assertIn("append", Config.MODES)
        self.assertIn("remove", Config.MODES)
        self.assertIn("replace", Config.MODES)
        self.assertIn("no_diff", Config.MODES)

        append_mode = Config.MODES["append"]
        self.assertEqual(append_mode.color, "green")
        self.assertEqual(append_mode.symbol, "+")

    def test_context_rules_configuration(self):
        """Test CONTEXT_RULES configuration."""
        self.assertIsInstance(Config.CONTEXT_RULES, list)
        self.assertTrue(len(Config.CONTEXT_RULES) > 0)

        # Test that all rules are ContextRule instances
        for rule in Config.CONTEXT_RULES:
            self.assertIsInstance(rule, ContextRule)

    def test_combination_rules_configuration(self):
        """Test COMBINATION_RULES configuration."""
        self.assertIsInstance(Config.COMBINATION_RULES, list)
        self.assertTrue(len(Config.COMBINATION_RULES) > 0)

        # Test that all rules are CombinationRule instances
        for rule in Config.COMBINATION_RULES:
            self.assertIsInstance(rule, CombinationRule)

    def test_get_context_params_existing(self):
        """Test getting context params for existing trigger."""
        params = Config.get_context_params("type")
        self.assertIsInstance(params, list)
        self.assertIn("format", params)

    def test_get_context_params_nonexistent(self):
        """Test getting context params for non-existent trigger."""
        params = Config.get_context_params("nonexistent")
        self.assertEqual(params, [])

    def test_get_display_mode_existing(self):
        """Test getting display mode for existing mode."""
        mode = Config.get_display_mode("append")
        self.assertIsInstance(mode, DisplayMode)
        self.assertEqual(mode.color, "green")
        self.assertEqual(mode.symbol, "+")

    def test_get_display_mode_nonexistent(self):
        """Test getting display mode for non-existent mode."""
        with self.assertRaises(KeyError):
            Config.get_display_mode("nonexistent")

    def test_get_combination_rules(self):
        """Test getting combination rules."""
        rules = Config.get_combination_rules()
        self.assertIsInstance(rules, list)
        self.assertTrue(len(rules) > 0)
        for rule in rules:
            self.assertIsInstance(rule, CombinationRule)


class TestTypeMap(unittest.TestCase):
    """Test TYPE_MAP constant."""

    def test_type_map_contents(self):
        """Test TYPE_MAP contains expected mappings."""
        expected_mappings = {
            type(None): "null",
            bool: "boolean",
            int: "integer",
            float: "number",
            str: "string",
            list: "array",
            tuple: "array",
            dict: "object",
        }

        for python_type, json_type in expected_mappings.items():
            self.assertIn(python_type, TYPE_MAP)
            self.assertEqual(TYPE_MAP[python_type], json_type)


if __name__ == "__main__":
    unittest.main()

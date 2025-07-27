"""
Parameter combiner for JSON Schema comparison.

This module provides functionality to combine related parameters
(like type+format) into single display entries.
"""

from typing import Any, Dict, List, Optional, Set, Tuple

from .config import CombinationRule, CombineMode, Config
from .path_utils import PathUtils


class ParameterCombiner:
    """Class for combining related parameters based on configuration rules."""

    def __init__(self, old_schema: Dict[str, Any], new_schema: Dict[str, Any]):
        """
        Initialize the ParameterCombiner with schemas.

        Args:
            old_schema: The original schema
            new_schema: The new schema
        """
        self.old_schema = old_schema
        self.new_schema = new_schema

    def combine_parameters(
        self, differences: List[Tuple[List[str], Any, Any]]
    ) -> List[Tuple[List[str], Any, Any]]:
        """
        Combine related parameters based on combination rules.

        Args:
            differences: List of differences as (path, old_value, new_value)

        Returns:
            List of differences with parameters combined
        """
        if not differences or not Config.get_combination_rules():
            return differences

        result: List[Tuple[List[str], Any, Any]] = []
        processed_paths: Set[str] = set()

        for path, old_val, new_val in differences:
            path_str = ".".join(path)

            if path_str in processed_paths:
                continue

            # Check if this parameter can be combined
            combined = False
            for rule in Config.get_combination_rules():
                main_param = rule.main_param
                sub_param = rule.sub_param

                if len(path) > 0 and path[-1] == main_param:
                    # This is a main parameter - try to combine with sub parameter
                    base_path = path[:-1]
                    sub_path = base_path + [sub_param]
                    sub_path_str = ".".join(sub_path)

                    if self._can_combine(rule, path, old_val, new_val, "main"):
                        # Look for sub parameter in differences or create virtual one
                        sub_diff = self._find_or_create_sub_param(
                            differences, sub_path, rule, "main"
                        )
                        if sub_diff:
                            combined_diff = self._combine_params(
                                rule, (path, old_val, new_val), sub_diff
                            )
                            result.append(combined_diff)
                            processed_paths.add(path_str)
                            processed_paths.add(sub_path_str)
                            combined = True
                            break

                elif len(path) > 0 and path[-1] == sub_param:
                    # This is a sub parameter - try to combine with main parameter
                    base_path = path[:-1]
                    main_path = base_path + [main_param]
                    main_path_str = ".".join(main_path)

                    if self._can_combine(rule, path, old_val, new_val, "sub"):
                        # Look for main parameter in differences or create virtual one
                        main_diff = self._find_or_create_main_param(
                            differences, main_path, rule, "sub"
                        )
                        if main_diff:
                            combined_diff = self._combine_params(
                                rule, main_diff, (path, old_val, new_val)
                            )
                            result.append(combined_diff)
                            processed_paths.add(path_str)
                            processed_paths.add(main_path_str)
                            combined = True
                            break

            if not combined:
                result.append((path, old_val, new_val))
                processed_paths.add(path_str)

        return result

    def _can_combine(
        self,
        rule: "CombinationRule",
        path: List[str],
        old_val: Any,
        new_val: Any,
        param_type: str,
    ) -> bool:
        """
        Check if parameter can be combined based on rules.

        Args:
            rule: Combination rule configuration
            path: Parameter path
            old_val: Old value
            new_val: New value
            param_type: "main" or "sub"

        Returns:
            True if parameter can be combined
        """
        operation = self._get_operation_type(old_val, new_val)

        if operation == "add":
            combine_mode = rule.rules.addition
        elif operation == "remove":
            combine_mode = rule.rules.removal
        elif operation == "change":
            combine_mode = rule.rules.change
        else:
            return False

        # Check if this parameter type should be combined based on the mode
        if combine_mode == CombineMode.ALL:
            return True
        elif combine_mode == CombineMode.MAIN_ONLY:
            return param_type == "main"
        elif combine_mode == CombineMode.SUB_ONLY:
            return param_type == "sub"
        else:  # CombineMode.NONE
            return False

    def _find_or_create_sub_param(
        self,
        differences: List[Tuple[List[str], Any, Any]],
        sub_path: List[str],
        rule: CombinationRule,
        triggered_by: str,
    ) -> Optional[Tuple[List[str], Any, Any]]:
        """
        Find sub parameter in differences or create virtual one from schema.

        Args:
            differences: List of all differences
            sub_path: Path to the sub parameter
            rule: Combination rule configuration
            triggered_by: What triggered this combination
                (unused but kept for consistency)

        Returns:
            Sub parameter tuple or None if not found/creatable
        """
        # First try to find in existing differences
        sub_path_str = ".".join(sub_path)
        for path, old_val, new_val in differences:
            if ".".join(path) == sub_path_str:
                return (path, old_val, new_val)

        # If not found, try to create virtual parameter from schema
        return self._create_virtual_param(sub_path, rule, "sub")

    def _find_or_create_main_param(
        self,
        differences: List[Tuple[List[str], Any, Any]],
        main_path: List[str],
        rule: CombinationRule,
        triggered_by: str,
    ) -> Optional[Tuple[List[str], Any, Any]]:
        """
        Find main parameter in differences or create virtual one from schema.

        Args:
            differences: List of all differences
            main_path: Path to the main parameter
            rule: Combination rule configuration
            triggered_by: What triggered this combination
                (unused but kept for consistency)

        Returns:
            Main parameter tuple or None if not found/creatable
        """
        # First try to find in existing differences
        main_path_str = ".".join(main_path)
        for path, old_val, new_val in differences:
            if ".".join(path) == main_path_str:
                return (path, old_val, new_val)

        # If not found, try to create virtual parameter from schema
        return self._create_virtual_param(main_path, rule, "main")

    def _create_virtual_param(
        self, param_path: List[str], rule: CombinationRule, param_type: str
    ) -> Optional[Tuple[List[str], Any, Any]]:
        """
        Create virtual parameter from schema context.

        Args:
            param_path: Path to the parameter
            rule: Combination rule
            param_type: "main" or "sub"

        Returns:
            Virtual parameter tuple or None
        """
        # Get value from old schema
        old_value = self._get_schema_value(param_path, self.old_schema)

        # Get value from new schema
        new_value = self._get_schema_value(param_path, self.new_schema)

        # If values are same in both schemas, create virtual "no change" parameter
        if old_value is not None and old_value == new_value:
            return (param_path, old_value, new_value)

        return None

    def _get_schema_value(
        self, param_path: List[str], schema: Dict[str, Any]
    ) -> Optional[Any]:
        """Get value from schema at given path."""
        if not schema:
            return None

        # Wrap schema in properties structure for PathUtils
        wrapped_schema = {"properties": schema.get("properties", {})}
        return PathUtils.get_value_at_path(wrapped_schema, param_path)

    def _combine_params(
        self,
        rule: CombinationRule,
        main_diff: Tuple[List[str], Any, Any],
        sub_diff: Tuple[List[str], Any, Any],
    ) -> Tuple[List[str], Any, Any]:
        """
        Combine main and sub parameters into single difference.

        Args:
            rule: Combination rule configuration
            main_diff: Main parameter difference
            sub_diff: Sub parameter difference

        Returns:
            Combined difference tuple
        """
        main_path, main_old, main_new = main_diff
        sub_path, sub_old, sub_new = sub_diff

        # Use main parameter path but with display name from rule
        display_path = main_path[:-1] + [rule.display_name]

        # Build combined old value
        combined_old = self._build_combined_value(rule, main_old, sub_old)

        # Build combined new value
        combined_new = self._build_combined_value(rule, main_new, sub_new)

        return (display_path, combined_old, combined_new)

    def _build_combined_value(
        self, rule: CombinationRule, main_val: Any, sub_val: Any
    ) -> Optional[str]:
        """Build combined value using rule template."""
        if main_val is None and sub_val is None:
            return None

        template = rule.format_template

        # Handle cases where one value is None
        if main_val is None:
            main_str = ""
        else:
            main_str = str(main_val)

        if sub_val is None:
            sub_str = ""
        else:
            sub_str = str(sub_val)

        # If both values exist, use template
        if main_val is not None and sub_val is not None:
            return template.format(main=main_str, sub=sub_str)
        # If only main exists, return just main
        elif main_val is not None:
            return main_str
        # If only sub exists, return just sub
        elif sub_val is not None:
            return sub_str
        else:
            return None

    def _get_operation_type(self, old_val: Any, new_val: Any) -> str:
        """Get the type of operation: add, remove, change, or none."""
        if old_val is None and new_val is not None:
            return "add"
        elif old_val is not None and new_val is None:
            return "remove"
        elif old_val is not None and new_val is not None and old_val != new_val:
            return "change"
        else:
            return "none"

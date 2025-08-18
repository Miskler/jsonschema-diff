from collections import OrderedDict
from typing import Any, Dict, List, Tuple, TypeAlias

COMBINE_RULES_TYPE: TypeAlias = List[List[str]]
"""Rule format: each inner list declares a logical group of keys."""


class LogicCombinerHandler:
    """Group items by user-defined rules and merge their inner fields."""

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _require_inner_fields(inner_key_field: str | None, inner_value_field: str | None) -> None:
        if not inner_key_field or not inner_value_field:
            raise ValueError("inner_key_field и inner_value_field должны быть заданы.")

    @staticmethod
    def _extract(
        item: Any, key_name: str, inner_key_field: str, inner_value_field: str
    ) -> Tuple[Any, Any]:
        """
        Return ``(inner_key, inner_value)`` taken from ``item`` (a dict).

        Parameters
        ----------
        item : Any
            Mapping that must contain both inner fields.
        key_name : str
            Name of *item* inside the outer ``subset`` (used for messages).
        inner_key_field, inner_value_field : str
            Mandatory keys to pull out.

        Raises
        ------
        TypeError
            If *item* is not a dict or lacks required fields.
        """
        if not isinstance(item, dict):
            raise TypeError(f"Expected dict for '{key_name}', got {type(item).__name__}")
        if inner_key_field not in item or inner_value_field not in item:
            raise TypeError(
                f"Item '{key_name}' must contain '{inner_key_field}' and '{inner_value_field}'"
            )
        return item[inner_key_field], item[inner_value_field]

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    @staticmethod
    def combine(
        subset: Dict[str, Any],
        rules: List[List[str]],
        inner_key_field: str = "comparator",
        inner_value_field: str = "to_compare",
    ) -> Dict[Tuple[str, ...], Dict[str, Any]]:
        """
        Build an ``OrderedDict`` that groups *subset* items per *rules*.

        Returns
        -------
        dict
            ``(k1, k2, …) -> {inner_key_field: common_key, inner_value_field: [v1, v2, …]}``

        Note
        ----
        * Keys not covered by *rules* stay as single-element groups.
        * Inner keys in the same group must match or ``ValueError`` is raised.
        """
        LogicCombinerHandler._require_inner_fields(inner_key_field, inner_value_field)
        out: "OrderedDict[Tuple[str, ...], Dict[str, Any]]" = OrderedDict()
        seen_in_rules: set[str] = set()

        # 1. groups coming from explicit rules
        for rule in rules:
            present = [k for k in rule if k in subset]
            if not present:
                continue

            fields, vals = [], []
            for k in present:
                f, v = LogicCombinerHandler._extract(
                    subset[k], k, inner_key_field, inner_value_field
                )
                fields.append(f)
                vals.append(v)

            base_field = fields[0]
            if any(f != base_field for f in fields[1:]):
                raise ValueError(f"Mismatched '{inner_key_field}' inside group {tuple(present)}")

            out[tuple(present)] = {inner_key_field: base_field, inner_value_field: vals}
            seen_in_rules.update(present)

        # 2. leftover singletons, keep original order
        for k, item in subset.items():
            if k in seen_in_rules:
                continue
            f, v = LogicCombinerHandler._extract(item, k, inner_key_field, inner_value_field)
            out[(k,)] = {inner_key_field: f, inner_value_field: [v]}

        return out

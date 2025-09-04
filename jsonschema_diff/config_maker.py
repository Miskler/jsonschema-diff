"""
Factory for a ready-to-use :class:`jsonschema_diff.core.Config` instance.

All optional switches are enabled by default; pass ``False`` to disable.
"""

from dataclasses import dataclass
from enum import Enum

from .core import Compare, Config
from .core.custom_compare import CompareList, CompareRange
from .core.tools.combine import COMBINE_RULES_TYPE
from .core.tools.compare import COMPARE_RULES_TYPE
from .core.tools.context import CONTEXT_RULES_TYPE, PAIR_CONTEXT_RULES_TYPE
from .core.tools.render import PATH_MAKER_IGNORE_RULES_TYPE


@dataclass(frozen=True)
class MultilineChars:
    START_LINE: str
    MIDDLE_LINE: str
    END_LINE: str
    SINGLE_LINE: str


class MultilineListRender(Enum):
    Soft = MultilineChars("╭", "│", "╰", " ")
    Hard = MultilineChars("┌", "│", "└", " ")
    Double = MultilineChars("╔", "║", "╚", " ")
    Without = MultilineChars(" ", " ", " ", " ")


class ConfigMaker:
    """Helper that builds a fully populated :class:`~jsonschema_diff.core.Config`."""

    # pylint: disable=too-many-arguments
    @staticmethod
    def make(
        *,
        tab_size: int = 2,
        path_render_with_properies: bool = False,
        path_render_with_items: bool = False,
        list_comparator: bool = True,
        list_multiline_render: MultilineListRender = MultilineListRender.Soft,
        range_digit_comparator: bool = True,
        range_length_comparator: bool = True,
        range_items_comparator: bool = True,
        range_properties_comparator: bool = True,
        additional_compare_rules: COMPARE_RULES_TYPE = {},
        additional_combine_rules: COMBINE_RULES_TYPE = [],
        additional_pair_context_rules: PAIR_CONTEXT_RULES_TYPE = [],
        additional_context_rules: CONTEXT_RULES_TYPE = {},
        additional_path_maker_ignore: PATH_MAKER_IGNORE_RULES_TYPE = [],
    ) -> Config:
        """
        Assemble and return a :class:`~jsonschema_diff.core.Config`.

        Parameters
        ----------
        tab_size : int
            Number of spaces per indentation level.
        path_render_with_properies, path_render_with_items : bool
            Include these schema service tokens in rendered paths.
        list_comparator : bool
            Enable :class:`~jsonschema_diff.core.custom_compare.CompareList`.
        list_multiline_render : MultilineListRender
            How to render multi-line elements of list.
        range_*_comparator : bool
            Enable :class:`~jsonschema_diff.core.custom_compare.CompareRange`
            for numeric/length/items/properties limits.
        additional_* : collections
            User-supplied rules that override the built-ins.
        """
        tab = " " * tab_size

        compare_rules: COMPARE_RULES_TYPE = {}
        combine_rules: COMBINE_RULES_TYPE = []
        pair_context_rules: list[list[str | type[Compare]]] = []
        context_rules: dict[str | type[Compare], list[str | type[Compare]]] = {}
        path_maker_ignore: list[str] = []
        compare_config: dict[type[Compare], dict] = {}

        # Built-in comparators
        if list_comparator:
            compare_rules[list] = CompareList
            compare_config[CompareList] = {
                field: getattr(list_multiline_render.value, field)
                for field in list_multiline_render.value.__dataclass_fields__
            }

        def add_rule(keys: list[str], value: type[Compare]) -> None:
            combine_rules.append(keys)
            for key in keys:
                compare_rules[key] = value

        ranger = CompareRange
        if range_digit_comparator:
            add_rule(["minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum"], ranger)
        if range_length_comparator:
            add_rule(["minLength", "maxLength"], ranger)
        if range_items_comparator:
            add_rule(["minItems", "maxItems"], ranger)
        if range_properties_comparator:
            add_rule(["minProperties", "maxProperties"], ranger)

        # Path-render filters
        if not path_render_with_properies:
            path_maker_ignore.append("properties")
        if not path_render_with_items:
            path_maker_ignore.append("items")

        # User additions override defaults
        compare_rules.update(additional_compare_rules)
        combine_rules.extend(additional_combine_rules)
        pair_context_rules.extend([list(r) for r in additional_pair_context_rules])
        context_rules.update({k: list(v) for k, v in additional_context_rules.items()})
        path_maker_ignore.extend(additional_path_maker_ignore)

        return Config(
            tab=tab,
            compare_rules=compare_rules,
            combine_rules=combine_rules,
            path_maker_ignore=path_maker_ignore,
            pair_context_rules=pair_context_rules,
            context_rules=context_rules,
            compare_config=compare_config,
        )

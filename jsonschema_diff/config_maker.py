from .core import Compare, Config
from .core.custom_compare import CompareList, CompareRange

from .core.tools.combine import COMBINE_RULES_TYPE
from .core.tools.compare import COMPARE_RULES_TYPE
from .core.tools.context import CONTEXT_RULES_TYPE, PAIR_CONTEXT_RULES_TYPE
from .core.tools.render import PATH_MAKER_IGNORE_RULES_TYPE


class ConfigMaker:
    @staticmethod
    def make(
        tab_size: int = 2,
        path_render_with_properies: bool = False,
        path_render_with_items: bool = False,
        list_comparator: bool = True,
        
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
        tab = " " * tab_size

        compare_rules = {}
        combine_rules = []
        pair_context_rules = []
        context_rules = {}
        path_maker_ignore = []


        if list_comparator:
            compare_rules[list] = CompareList

        def add_rule(keys: list[str], value: type[Compare]):
            combine_rules.append(keys)
            for key in keys:
                compare_rules[key] = value

        ranger = CompareRange
        if range_digit_comparator:
            add_rule(["minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum"],
                     ranger)
        if range_length_comparator:
            add_rule(["minLength", "maxLength"], ranger)
        if range_items_comparator:
            add_rule(["minItems", "maxItems"], ranger)
        if range_properties_comparator:
            add_rule(["minProperties", "maxProperties"], ranger)


        if not path_render_with_properies:
            path_maker_ignore.append("properties")
        if not path_render_with_items:
            path_maker_ignore.append("items")
        

        # additional имеют приоритет и перезаписывают остальное при конфликте
        compare_rules.update(additional_compare_rules)
        combine_rules.extend(additional_combine_rules)
        pair_context_rules.extend(additional_pair_context_rules)
        context_rules.update(additional_context_rules)
        path_maker_ignore.extend(additional_path_maker_ignore)

        return Config(
            tab=tab,
            compare_rules=compare_rules,
            combine_rules=combine_rules,
            path_maker_ignore=path_maker_ignore,
            pair_context_rules=pair_context_rules,
            context_rules=context_rules,
        )

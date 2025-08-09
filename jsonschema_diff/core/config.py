from typing import Any
from types import NoneType
from typing import TYPE_CHECKING

from .parameter_base import Compare
from .custom_compare.list import CompareList
from .custom_compare.range import CompareRange

class CompareRules:
    def __init__(self,
                 rules: dict[type | tuple[type, type] | str | tuple[str, type, type] | tuple[str, type], type[Compare]] = {},
                 default: type[Compare] = Compare):
        self.compare_rules = rules
        self.default = default
    
    def get_comparator_from_values(self, key: str, old: Any, new: Any) -> type[Compare]:
        return self.get_comparator(key, type(old), type(new))

    def get_comparator(self, key: str, old: type, new: type) -> type[Compare]:
        # (ключ, старое, новое)
        # (ключ)
        # (старое, новое)
        # (общий валидный тип)
        # -> по умолчанию
        for search in [
            ((key, old, new)),
            (key),
            ((old, new)),
        ]:
            tuple_types = self.compare_rules.get(search, None)
            if tuple_types is not None:
                return tuple_types
        else:
            if old is NoneType:
                return self.compare_rules.get(new, self.default)
            elif old is not NoneType or old is new:
                return self.compare_rules.get(old, self.default)
            else:
                return self.default


class Config:
    def __init__(self,
                 tab: str = "  ",
                 compare_rules: CompareRules | None = None,
                 combine_rules: list[list[str]] = [],
                 path_maker_ignore: list[str] = ["properties", "items"],
                 pair_context_rules: list = [],
                 context_rules: dict = {}):
        self.TAB = tab
        
        if compare_rules is None:
            compare_rules = CompareRules()
        self.COMPARE_RULES = compare_rules
        
        self.COMBINE_RULES = combine_rules

        self.PATH_MAKER_IGNORE = path_maker_ignore

        self.PAIR_CONTEXT_RULES = pair_context_rules
        self.CONTEXT_RULES = context_rules


config = Config(
    compare_rules=CompareRules({
        list: CompareList,
        
        #  ЧИСЛА
        "minimum":          CompareRange,
        "maximum":          CompareRange,
        "exclusiveMinimum": CompareRange,
        "exclusiveMaximum": CompareRange,
        #  СТРОКИ (длины)
        "minLength":        CompareRange,
        "maxLength":        CompareRange,
        #  МАССИВЫ (число элементов)
        "minItems":         CompareRange,
        "maxItems":         CompareRange,
        #  ОБЪЕКТЫ (число свойств)
        "minProperties":    CompareRange,
        "maxProperties":    CompareRange,
    }),
    combine_rules=[
        ["minimum", "exclusiveMinimum", "maximum", "exclusiveMaximum"],
        ["minLength", "maxLength"],
        ["minItems", "maxItems"],
        ["minProperties", "maxProperties"],
    ],
    pair_context_rules=[
        ["one", "other"],
    ],
    context_rules={
        "something": ["one", "other"],
    }
)

from typing import Any
from types import NoneType
from typing import TYPE_CHECKING

from .parameter_base import Compare
from .custom_compare.list import CompareList

class CompareRules:
    def __init__(self, rules: dict[type | tuple[type, type], type[Compare]] = {}, default: type[Compare] = Compare):
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

class CombineRules:
    def __init__(self, rules: dict[type | tuple[type, type], type[Compare]] = {}, default: type[Compare] = Compare):
        self.compare_rules = rules
        self.default = default


class Config:
    def __init__(self,
                 tab: str = "  ",
                 compare_rules: CompareRules | None = None,
                 path_maker_ignore: list[str] = ["properties", "items"]):
        self.TAB = tab
        if compare_rules is None:
            self.COMPARE_RULES = CompareRules()
        self.COMPARE_RULES = compare_rules
        self.PATH_MAKER_IGNORE = path_maker_ignore


config = Config(compare_rules=CompareRules({list: CompareList}))
